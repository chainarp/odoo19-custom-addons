# itx_ai_helm/controllers/terminal_websocket.py
# Long Polling Implementation (แทน WebSocket)

from odoo import http
from odoo.http import request
import json
import logging
import time
import queue

_logger = logging.getLogger(__name__)

# ติดตั้ง log filter เพื่อลด terminal logs (optional)
try:
    from ..services.log_filter import install_terminal_log_filter
    install_terminal_log_filter()
    _logger.info("✓ Terminal log filter installed - polling logs will be hidden")
except Exception as e:
    _logger.warning(f"Could not install log filter: {e}")


class TerminalController(http.Controller):
    """
    Terminal Controller แบบ Long Polling

    Long Polling ทำงานโดย:
    1. Client ส่ง request มาที่ /terminal/poll
    2. Server รอจนกว่าจะมี output ใหม่ (หรือ timeout)
    3. ส่ง output กลับไป
    4. Client ส่ง request ใหม่ทันที (วนไปเรื่อยๆ)

    ข้อดี: ใช้ HTTP ธรรมดา ไม่ต้องติดตั้งอะไรเพิ่ม
    ข้อเสีย: มี latency มากกว่า WebSocket เล็กน้อย แต่ยอมรับได้
    """

    @http.route('/terminal/connect', type='json', auth='user')
    def connect_terminal(self, session_id=None, command='bash'):
        """
        สร้างหรือ Resume terminal session

        Args:
            session_id: ID ของ session เดิม (ถ้ามี) หรือ None เพื่อสร้างใหม่
            command: คำสั่งที่จะรัน (default: 'bash')

        Returns:
            dict: {
                'success': True,
                'session_id': '...',
                'is_resumed': True/False,
                'history': '...'  # ถ้า resume
            }
        """
        try:
            from ..services.terminal_manager import TerminalManager

            is_resumed = False
            history = ''

            # ถ้ามี session_id → ลอง resume
            if session_id:
                existing_session = TerminalManager.get_session(session_id)
                if existing_session and existing_session.running and existing_session.is_alive():
                    # Resume session เดิม
                    is_resumed = True
                    history = existing_session.get_history(lines=500)  # ส่ง history 500 บรรทัดล่าสุด
                    _logger.info(f"Resumed terminal session: {session_id}")

                    return {
                        'success': True,
                        'session_id': session_id,
                        'is_resumed': True,
                        'history': history
                    }
                else:
                    # Session เก่าตายแล้ว → สร้างใหม่ด้วย session_id เดิม
                    _logger.warning(f"Session {session_id} is dead, creating new one")

            # สร้าง session ใหม่
            if not session_id:
                # บันทึกลง database
                Terminal = request.env['terminal.session']
                db_session = Terminal.create_session(command)
                session_id = db_session.session_id
                _logger.info(f"Created new terminal session: {session_id}")

            # สร้าง terminal process
            session = TerminalManager.create_session(session_id, command)
            session.start()

            return {
                'success': True,
                'session_id': session_id,
                'is_resumed': False,
                'message': f'Terminal session started: {session_id[:8]}'
            }

        except Exception as e:
            _logger.error(f"Failed to connect terminal: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/terminal/poll', type='json', auth='user')
    def poll_output(self, session_id, timeout=30):
        """
        รับ output จาก terminal (Long Polling)

        Method นี้จะ "รอ" จนกว่า:
        1. มี output ใหม่จาก terminal
        2. หรือครบ timeout (default 30 วินาที)

        Args:
            session_id: ID ของ session
            timeout: เวลารอสูงสุด (วินาที)

        Returns:
            dict: {'output': '...', 'success': True} หรือ {'success': False}
        """
        try:
            from ..services.terminal_manager import TerminalManager

            session = TerminalManager.get_session(session_id)
            if not session:
                return {
                    'success': False,
                    'error': 'Session not found'
                }

            # รอ output ใหม่ (หรือ timeout)
            # ใช้ non-blocking queue เพื่อไม่ให้ block Odoo worker
            start_time = time.time()
            output_parts = []

            while time.time() - start_time < timeout:
                # ดึง output จาก buffer
                new_output = session.get_pending_output()

                if new_output:
                    output_parts.append(new_output)
                    # ได้ output แล้ว ส่งกลับทันที
                    break

                # ยังไม่มี output รอ 0.1 วินาทีแล้วลองใหม่
                time.sleep(0.1)

            return {
                'success': True,
                'output': ''.join(output_parts),
                'has_more': len(session.output_buffer) > 0
            }

        except Exception as e:
            _logger.error(f"Poll error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/terminal/write', type='json', auth='user')
    def write_input(self, session_id, data):
        """
        ส่ง input ไปยัง terminal

        Args:
            session_id: ID ของ session
            data: ข้อความที่จะส่งไป (keyboard input)

        Returns:
            dict: {'success': True} หรือ {'success': False}
        """
        try:
            from ..services.terminal_manager import TerminalManager

            session = TerminalManager.get_session(session_id)
            if not session:
                return {
                    'success': False,
                    'error': 'Session not found'
                }

            # เขียนไปยัง terminal
            success = session.write(data)

            return {
                'success': success
            }

        except Exception as e:
            _logger.error(f"Write error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    @http.route('/terminal/resize', type='json', auth='user')
    def resize_terminal(self, session_id, rows, cols):
        """
        ปรับขนาด terminal

        Args:
            session_id: ID ของ session
            rows: จำนวนแถว
            cols: จำนวนคอลัมน์

        Returns:
            dict: {'success': True}
        """
        try:
            from ..services.terminal_manager import TerminalManager

            session = TerminalManager.get_session(session_id)
            if session:
                session.resize(rows, cols)

            return {'success': True}

        except Exception as e:
            _logger.error(f"Resize error: {e}", exc_info=True)
            return {'success': False}

    @http.route('/terminal/disconnect', type='json', auth='user')
    def disconnect_terminal(self, session_id):
        """
        ปิด terminal session

        Args:
            session_id: ID ของ session

        Returns:
            dict: {'success': True}
        """
        try:
            from ..services.terminal_manager import TerminalManager

            TerminalManager.remove_session(session_id)

            return {'success': True}

        except Exception as e:
            _logger.error(f"Disconnect error: {e}", exc_info=True)
            return {'success': False}
