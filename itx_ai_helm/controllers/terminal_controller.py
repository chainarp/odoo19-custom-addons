# itx_ai_helm/controllers/terminal_controller.py

from odoo import http
import json
import asyncio
import websockets


class TerminalController(http.Controller):
    terminals = {}

    @http.route('/terminal/ws', type='websocket', auth='user')
    async def terminal_websocket(self, websocket):
        """Handle WebSocket connection"""
        from ..services.claude_terminal import ClaudeTerminal

        # Create new terminal instance
        terminal = ClaudeTerminal(websocket)
        terminal.start()

        session_id = id(websocket)
        self.terminals[session_id] = terminal

        try:
            async for message in websocket:
                data = json.loads(message)

                if data['type'] == 'input':
                    terminal.write(data['data'])

                elif data['type'] == 'resize':
                    terminal.resize(data['rows'], data['cols'])

        finally:
            # Cleanup
            del self.terminals[session_id]