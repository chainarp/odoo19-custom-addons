# -*- coding: utf-8 -*-

# Controllers for AI chat endpoints (future)
# from . import main
# from . import claude_controller
from . import ai_chat_controller

# Terminal controllers
# NOTE: WebSocket not supported in Odoo 19 without bus module integration
# from . import terminal_controller  # WebSocket - disabled for now
from . import terminal_websocket   # Long Polling (primary)