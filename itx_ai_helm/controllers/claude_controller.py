# itx_ai_helm/controllers/claude_controller.py

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class ClaudeController(http.Controller):

    @http.route('/ai_helm/execute', type='json', auth='user')
    def execute_command(self, command, timeout=30):
        """Execute Claude command via web interface"""
        from ..services.claude_cli_interface_old1 import get_claude_cli

        cli = get_claude_cli()
        result = cli.send_command(command, timeout)

        return result

    @http.route('/ai_helm/status', type='json', auth='user')
    def get_status(self):
        """Get Claude CLI status"""
        from ..services.claude_cli_interface_old1 import get_claude_cli

        cli = get_claude_cli()
        return cli.get_status()

    @http.route('/ai_helm/restart', type='json', auth='user')
    def restart_cli(self):
        """Restart Claude CLI"""
        from ..services.claude_cli_interface_old1 import get_claude_cli

        cli = get_claude_cli()
        success = cli.restart_cli()

        return {
            'success': success,
            'status': cli.get_status()
        }

    @http.route('/ai_helm/generate', type='json', auth='user')
    def generate_component(self, component_type, specs):
        """Generate Odoo component"""
        from ..services.claude_cli_interface_old1 import get_claude_cli

        cli = get_claude_cli()
        result = cli.generate_odoo_component(component_type, specs)

        return result

    @http.route('/ai_helm/get_or_create_conversation', type='jsonrpc', auth='user')
    def get_or_create_conversation(self):
        """Get or create conversation for current user"""
        try:
            # Find active conversation for current user
            Conversation = request.env['ai.conversation']
            conversation = Conversation.search([
                ('user_id', '=', request.env.user.id),
                ('active', '=', True)
            ], limit=1, order='create_date desc')

            if not conversation:
                # Create new conversation
                conversation = Conversation.create({
                    'name': f'Chat - {request.env.user.name}',
                    'user_id': request.env.user.id,
                })

            # Get messages
            messages = []
            for msg in conversation.message_ids.sorted('create_date'):
                messages.append({
                    'type': msg.message_type,
                    'content': msg.content,
                    'code_blocks': json.loads(msg.code_blocks) if msg.code_blocks else [],
                    'timestamp': msg.create_date.isoformat() if msg.create_date else '',
                    'status': msg.status
                })

            return {
                'conversation_id': conversation.id,
                'messages': messages
            }
        except Exception as e:
            _logger.error(f"Error in get_or_create_conversation: {e}")
            return {'error': str(e)}

    @http.route('/ai_helm/send_message', type='jsonrpc', auth='user')
    def send_message(self, conversation_id, message):
        """Send message to Claude and get response"""
        try:
            Conversation = request.env['ai.conversation']
            Message = request.env['ai.conversation.message']

            conversation = Conversation.browse(conversation_id)
            if not conversation.exists() or conversation.user_id.id != request.env.user.id:
                return {'error': 'Conversation not found'}

            # Save user message
            Message.create({
                'conversation_id': conversation.id,
                'message_type': 'user',
                'content': message,
                'status': 'complete'
            })

            # TODO: Call Claude API here
            # For now, return a dummy response
            response = "Claude API integration is pending. Please configure your Claude API key first."

            # Save assistant message
            Message.create({
                'conversation_id': conversation.id,
                'message_type': 'assistant',
                'content': response,
                'status': 'complete'
            })

            return {
                'response': response,
                'code_blocks': []
            }

        except Exception as e:
            _logger.error(f"Error in send_message: {e}")
            return {'error': str(e)}

    @http.route('/ai_helm/clear_conversation', type='jsonrpc', auth='user')
    def clear_conversation(self, conversation_id):
        """Clear all messages in conversation"""
        try:
            Conversation = request.env['ai.conversation']
            conversation = Conversation.browse(conversation_id)

            if not conversation.exists() or conversation.user_id.id != request.env.user.id:
                return {'error': 'Conversation not found'}

            # Delete all messages
            conversation.message_ids.unlink()

            return {'success': True}

        except Exception as e:
            _logger.error(f"Error in clear_conversation: {e}")
            return {'error': str(e)}
