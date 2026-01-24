# itx_ai_helm/services/terminal_manager.py

import os
import pty
import subprocess
import select
import termios
import struct
import fcntl
import logging
import threading
import json
import signal
import resource
from pathlib import Path

_logger = logging.getLogger(__name__)


class TerminalManager:
    """Manage terminal sessions"""

    _sessions = {}

    @classmethod
    def create_session(cls, session_id, command='bash', cwd=None):
        """
        Create new terminal session

        Args:
            session_id: Unique session ID
            command: Command to run (default: 'bash')
            cwd: Working directory (default: /tmp)
        """
        # Cleanup dead sessions ก่อน
        cls.cleanup_dead_sessions()

        # ✅ FIX: ตรวจสอบ session เดิมว่ายังใช้งานได้หรือไม่
        if session_id in cls._sessions:
            existing_session = cls._sessions[session_id]
            # ถ้า session เดิมยังทำงานอยู่ → ใช้อันเดิมต่อ
            if existing_session.running and existing_session.is_alive():
                _logger.info(f"Reusing existing session {session_id}")
                return existing_session
            else:
                # Session เดิมตายแล้ว → ลบแล้วสร้างใหม่
                _logger.warning(f"Session {session_id} is dead, creating new one")
                cls.remove_session(session_id)

        # สร้าง session ใหม่
        session = TerminalSession(session_id, command, cwd)
        cls._sessions[session_id] = session
        _logger.info(f"Created new session {session_id}. Total active: {len(cls._sessions)}")
        return session

    @classmethod
    def get_session(cls, session_id):
        """Get existing session"""
        return cls._sessions.get(session_id)

    @classmethod
    def remove_session(cls, session_id):
        """Remove session and cleanup"""
        if session_id in cls._sessions:
            cls._sessions[session_id].cleanup()
            del cls._sessions[session_id]
            _logger.info(f"Removed session {session_id}. Remaining: {len(cls._sessions)}")

    @classmethod
    def cleanup_dead_sessions(cls):
        """
        ลบ sessions ที่ process ตายแล้ว (zombie processes)

        เรียกทุกครั้งก่อนสร้าง session ใหม่
        """
        dead_sessions = []

        for session_id, session in cls._sessions.items():
            if not session.running or not session.is_alive():
                dead_sessions.append(session_id)

        for session_id in dead_sessions:
            _logger.info(f"Cleaning up dead session: {session_id}")
            cls.remove_session(session_id)


class TerminalSession:
    """
    Single terminal session

    รองรับ 3 modes:
    1. Bus.bus (Primary) - Real-time push ผ่าน Odoo WebSocket
    2. Long Polling (Fallback) - เก็บ output ใน pending_output queue
    3. Direct WebSocket (Legacy) - broadcast ไปยัง connected websockets
    """

    def __init__(self, session_id, command='claude', cwd=None):
        self.session_id = session_id
        self.command = command
        self.cwd = cwd or '/tmp'
        self.child_pid = None
        self.fd = None
        self.websockets = set()  # WebSocket connections for broadcast (legacy)
        self._ws_lock = threading.Lock()  # Thread-safe access to websockets
        self.output_buffer = []  # เก็บ history ทั้งหมด
        self.pending_output = []  # เก็บ output ใหม่ที่ยังไม่ได้ส่ง (สำหรับ polling)
        self.max_buffer_size = 1000
        self.running = False

        # Bus.bus callback for real-time output
        # Set by controller via set_bus_broadcaster()
        self._bus_broadcaster = None
        self._bus_lock = threading.Lock()

        # Claude specific path
        self.claude_path = self._find_claude_cli()

        _logger.info(f"Creating terminal session {session_id}")

    def set_bus_broadcaster(self, broadcaster_func):
        """
        Set callback function for broadcasting output via bus.bus

        Args:
            broadcaster_func: Function(session_id, output_text) that broadcasts via bus.bus
        """
        with self._bus_lock:
            self._bus_broadcaster = broadcaster_func
            _logger.info(f"Bus broadcaster set for session {self.session_id}")

    def _broadcast_to_bus(self, text):
        """
        Broadcast output via bus.bus (real-time)

        Args:
            text: Output text to broadcast
        """
        with self._bus_lock:
            if self._bus_broadcaster:
                try:
                    self._bus_broadcaster(self.session_id, text)
                except Exception as e:
                    _logger.warning(f"Bus broadcast failed: {e}")

    def _find_claude_cli(self):
        """Find claude CLI executable"""
        paths = [
            # Native Claude CLI (primary)
            os.path.expanduser('~/.local/bin/claude'),
            '/home/chainarp/.local/bin/claude',
            # Fallback to PATH
            'claude'
        ]

        for path in paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                _logger.info(f"Found Claude CLI at: {path}")
                return path

        # Try which
        try:
            result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
            if result.returncode == 0:
                found_path = result.stdout.strip()
                _logger.info(f"Found Claude CLI via which: {found_path}")
                return found_path
        except:
            pass

        _logger.warning("Claude CLI not found, will use 'claude' from PATH")
        return 'claude'  # Fallback

    def start(self):
        """Start terminal process"""
        if self.running:
            return

        try:
            # Create pseudo terminal
            self.child_pid, self.fd = pty.fork()

            if self.child_pid == 0:
                # Child process
                os.chdir(self.cwd)

                # 🔧 FIX: Remove address space limit for WebAssembly (Claude CLI)
                # Odoo parent process มี limit = 2.5GB แต่ Claude ต้องการมากกว่านั้น
                try:
                    resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
                    _logger.info("✓ Removed address space limit for child process")
                except Exception as e:
                    _logger.warning(f"Could not set resource limits: {e}")

                # Set environment
                env = os.environ.copy()
                env['TERM'] = 'xterm-256color'
                env['PYTHONUNBUFFERED'] = '1'

                # เพิ่ม Node.js memory limit สำหรับทุก subprocess
                # (ไม่เสียหายแม้จะไม่ใช้ Node.js)
                env['NODE_OPTIONS'] = '--max-old-space-size=4096'

                # สำหรับ Claude CLI: เพิ่ม PATH
                if self.command == 'claude':
                    # Add claude to PATH
                    claude_dir = os.path.dirname(self.claude_path)
                    if claude_dir:
                        env['PATH'] = f"{claude_dir}:{env.get('PATH', '')}"

                    try:
                        os.execve(self.claude_path, [self.claude_path], env)
                    except Exception as e:
                        # ถ้า claude fail ให้แสดง error แล้ว fallback เป็น bash
                        print(f"\n\n❌ Failed to start Claude CLI: {e}")
                        print("📌 Tip: Claude CLI requires lots of memory. Try 'Bash Terminal' instead.\n\n")
                        os.execvpe('bash', ['bash'], env)

                elif self.command == 'bash':
                    # เรียก bash แบบ interactive login shell
                    # -i = interactive (จะโหลด ~/.bashrc)
                    # --login = login shell (จะโหลด ~/.bash_profile)
                    os.execvpe('bash', ['bash', '--login', '-i'], env)

                else:
                    # คำสั่งอื่นๆ
                    os.execvpe(self.command, [self.command], env)
            else:
                # Parent process
                self.running = True
                self._set_winsize(24, 80)

                # Start reader thread
                self.reader_thread = threading.Thread(target=self._read_output)
                self.reader_thread.daemon = True
                self.reader_thread.start()

                _logger.info(f"Started terminal session {self.session_id} with PID {self.child_pid}")

        except Exception as e:
            _logger.error(f"Failed to start terminal: {e}")
            self.running = False

    def add_websocket(self, ws):
        """
        Register a WebSocket connection for output broadcast

        Args:
            ws: WebSocket object from request.ws
        """
        with self._ws_lock:
            self.websockets.add(ws)
            _logger.info(f"WebSocket added to session {self.session_id}. Total: {len(self.websockets)}")

    def remove_websocket(self, ws):
        """
        Unregister a WebSocket connection

        Args:
            ws: WebSocket object to remove
        """
        with self._ws_lock:
            self.websockets.discard(ws)
            _logger.info(f"WebSocket removed from session {self.session_id}. Remaining: {len(self.websockets)}")

    def _broadcast_to_websockets(self, text):
        """
        Broadcast output to all connected WebSocket clients

        Args:
            text: Output text to broadcast
        """
        import json

        message = json.dumps({
            'type': 'output',
            'data': text
        })

        dead_sockets = []

        with self._ws_lock:
            for ws in self.websockets:
                try:
                    ws.send(message)
                except Exception as e:
                    _logger.warning(f"Failed to send to WebSocket: {e}")
                    dead_sockets.append(ws)

            # Cleanup dead sockets
            for ws in dead_sockets:
                self.websockets.discard(ws)

    def _read_output(self):
        """
        อ่าน output จาก terminal

        รองรับ 3 modes:
        1. Bus.bus (Primary) - Real-time push ผ่าน Odoo WebSocket
        2. Long Polling (Fallback) - เก็บ output ใน pending_output
        3. Direct WebSocket (Legacy) - broadcast ไปยัง connected websockets
        """
        while self.running:
            try:
                r, _, _ = select.select([self.fd], [], [], 0.1)
                if r:
                    output = os.read(self.fd, 4096)
                    if output:
                        # Decode output
                        text = output.decode('utf-8', errors='replace')

                        # 1. Bus.bus broadcast (Primary - real-time)
                        self._broadcast_to_bus(text)

                        # 2. Direct WebSocket broadcast (Legacy)
                        if self.websockets:
                            self._broadcast_to_websockets(text)

                        # 3. เก็บใน pending_output สำหรับ Long Polling fallback
                        self.pending_output.append(text)

                        # เก็บใน history buffer
                        self.output_buffer.append(text)
                        if len(self.output_buffer) > self.max_buffer_size:
                            self.output_buffer = self.output_buffer[-self.max_buffer_size:]
                    else:
                        # EOF - terminal process ended
                        self.running = False
                        break
            except Exception as e:
                _logger.error(f"Read error: {e}")
                self.running = False
                break

    def write(self, data):
        """Write to terminal"""
        if self.fd and self.running:
            try:
                os.write(self.fd, data.encode('utf-8'))
                return True
            except Exception as e:
                _logger.error(f"Write error: {e}")
                return False
        return False

    def resize(self, rows, cols):
        """Resize terminal"""
        self._set_winsize(rows, cols)

    def _set_winsize(self, rows, cols):
        """Set window size"""
        if self.fd:
            try:
                winsize = struct.pack('HHHH', rows, cols, 0, 0)
                fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)
            except:
                pass

    def get_pending_output(self):
        """
        ดึง output ที่ยังไม่ได้ส่ง (สำหรับ Long Polling)

        Method นี้จะ:
        1. ดึง output ทั้งหมดที่มีใน pending_output
        2. ล้าง pending_output (เพราะส่งไปแล้ว)
        3. return เป็น string

        Returns:
            str: output ที่ยังไม่ได้ส่ง หรือ empty string ถ้าไม่มี
        """
        if self.pending_output:
            # รวม output ทั้งหมด
            result = ''.join(self.pending_output)
            # ล้าง pending (เพราะส่งไปแล้ว)
            self.pending_output = []
            return result
        return ''

    def get_history(self, lines=100):
        """
        ดึง history ย้อนหลัง (สำหรับ client ที่ connect ใหม่)

        Args:
            lines: จำนวนบรรทัดที่ต้องการ (default: 100)

        Returns:
            str: output history
        """
        if self.output_buffer:
            return ''.join(self.output_buffer[-lines:])
        return ''

    def is_alive(self):
        """
        เช็คว่า process ยังทำงานอยู่หรือไม่

        Returns:
            bool: True ถ้า process ยังทำงาน, False ถ้าตายแล้ว
        """
        if not self.child_pid:
            return False

        try:
            # ใช้ os.waitpid แบบ non-blocking (WNOHANG) เพื่อเช็คสถานะ
            pid, status = os.waitpid(self.child_pid, os.WNOHANG)
            if pid == 0:
                # Process ยังทำงานอยู่
                return True
            else:
                # Process ตายแล้ว
                _logger.info(f"Process {self.child_pid} exited with status {status}")
                return False
        except ChildProcessError:
            # Process ไม่มีอยู่แล้ว
            return False
        except Exception as e:
            _logger.error(f"Error checking process: {e}")
            return False

    def cleanup(self):
        """Cleanup session"""
        self.running = False

        if self.child_pid:
            try:
                os.kill(self.child_pid, signal.SIGTERM)
                os.waitpid(self.child_pid, 0)
            except:
                pass

        if self.fd:
            try:
                os.close(self.fd)
            except:
                pass

        _logger.info(f"Cleaned up session {self.session_id}")