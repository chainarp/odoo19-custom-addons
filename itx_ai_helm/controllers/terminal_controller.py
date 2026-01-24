# itx_ai_helm/controllers/terminal_controller.py
# WebSocket Controller for Terminal (Odoo 17+ pattern)

from odoo import http
from odoo.http import request, WebSocket
import json
import logging
import threading

_logger = logging.getLogger(__name__)


class TerminalWebSocketController(http.Controller):
    """
    WebSocket Controller for Terminal

    ใช้ Odoo 17+ WebSocket pattern:
    - type='http', websocket=True
    - ใช้ request.ws (WebSocket object)

    Protocol:
    Client -> Server:
        { type: 'input', data: '...' }
        { type: 'resize', rows: 24, cols: 80 }
        { type: 'ping' }

    Server -> Client:
        { type: 'connect', session_id: '...', is_resumed: bool, history: '...' }
        { type: 'output', data: '...' }
        { type: 'pong' }
        { type: 'error', message: '...' }
    """

    @http.route('/terminal/ws', type='http', auth='user', websocket=True)
    def terminal_websocket(self, session_id=None, command='bash'):
        """
        Handle WebSocket connection for terminal

        Args:
            session_id: Optional session ID for resume
            command: Command to run (default: 'bash')
        """
        ws = request.ws

        try:
            from ..services.terminal_manager import TerminalManager

            is_resumed = False
            history = ''

            # Try to resume existing session
            if session_id:
                existing_session = TerminalManager.get_session(session_id)
                if existing_session and existing_session.running and existing_session.is_alive():
                    is_resumed = True
                    history = existing_session.get_history(lines=500)
                    _logger.info(f"WebSocket resumed session: {session_id}")
                else:
                    # Session dead, create new with same ID
                    _logger.warning(f"Session {session_id} is dead, creating new")
                    session_id = None

            # Create new session if needed
            if not session_id:
                # Create database record
                Terminal = request.env['terminal.session']
                db_session = Terminal.create_session(command)
                session_id = db_session.session_id
                _logger.info(f"WebSocket created new session: {session_id}")

            # Create or get terminal session
            session = TerminalManager.create_session(session_id, command)
            if not is_resumed:
                session.start()

            # Register WebSocket with session for broadcast
            session.add_websocket(ws)

            # Send connect message
            connect_msg = {
                'type': 'connect',
                'session_id': session_id,
                'is_resumed': is_resumed,
                'history': history
            }
            ws.send(json.dumps(connect_msg))

            _logger.info(f"WebSocket connected: session={session_id}, resumed={is_resumed}")

            # Handle incoming messages
            try:
                while True:
                    message = ws.receive()
                    if message is None:
                        # Connection closed
                        break

                    try:
                        data = json.loads(message)
                        msg_type = data.get('type')

                        if msg_type == 'input':
                            # Write input to terminal
                            session.write(data.get('data', ''))

                        elif msg_type == 'resize':
                            # Resize terminal
                            rows = data.get('rows', 24)
                            cols = data.get('cols', 80)
                            session.resize(rows, cols)

                        elif msg_type == 'ping':
                            # Respond with pong
                            ws.send(json.dumps({'type': 'pong'}))

                    except json.JSONDecodeError:
                        _logger.warning(f"Invalid JSON from WebSocket: {message}")
                    except Exception as e:
                        _logger.error(f"Error handling WebSocket message: {e}")
                        ws.send(json.dumps({'type': 'error', 'message': str(e)}))

            finally:
                # Cleanup: Remove WebSocket from session
                session.remove_websocket(ws)
                _logger.info(f"WebSocket disconnected: session={session_id}")

        except Exception as e:
            _logger.error(f"WebSocket error: {e}", exc_info=True)
            try:
                ws.send(json.dumps({'type': 'error', 'message': str(e)}))
            except:
                pass
