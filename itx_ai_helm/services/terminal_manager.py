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

    แก้ไขเพื่อรองรับ Long Polling:
    - เพิ่ม pending_output_queue เพื่อเก็บ output ใหม่ที่ยังไม่ได้ส่ง
    - เพิ่ม get_pending_output() method สำหรับ polling
    - เก็บ websockets ไว้เผื่ออนาคตจะใช้ (ตอนนี้ไม่ใช้)
    """

    def __init__(self, session_id, command='claude', cwd=None):
        self.session_id = session_id
        self.command = command
        self.cwd = cwd or '/tmp'
        self.child_pid = None
        self.fd = None
        self.websockets = set()  # เก็บไว้เผื่ออนาคต (ไม่ใช้แล้ว)
        self.output_buffer = []  # เก็บ history ทั้งหมด
        self.pending_output = []  # เก็บ output ใหม่ที่ยังไม่ได้ส่ง (สำหรับ polling)
        self.max_buffer_size = 1000
        self.running = False

        # Claude specific path
        self.claude_path = self._find_claude_cli()

        _logger.info(f"Creating terminal session {session_id}")

    def _find_claude_cli(self):
        """Find claude CLI executable"""
        paths = [
            '/home/chainarp/.nvm/versions/node/v22.19.0/bin/claude',
            os.path.expanduser('~/.nvm/versions/node/v22.19.0/bin/claude'),
            'claude'
        ]

        for path in paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        # Try which
        try:
            result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

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

    def _read_output(self):
        """
        อ่าน output จาก terminal

        แก้ไขสำหรับ Long Polling:
        - เก็บ output ใน pending_output list (สำหรับ client ดึงไปแสดง)
        - เก็บ output ใน output_buffer (เป็น history)
        - ไม่ broadcast ผ่าน websocket แล้ว (ใช้ polling แทน)
        """
        while self.running:
            try:
                r, _, _ = select.select([self.fd], [], [], 0.1)
                if r:
                    output = os.read(self.fd, 4096)
                    if output:
                        # Decode output
                        text = output.decode('utf-8', errors='replace')

                        # เก็บใน pending_output สำหรับ polling
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