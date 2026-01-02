# itx_ai_helm/controllers/ai_chat_controller.py

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class AIChatController(http.Controller):

    @http.route('/ai_helm/get_or_create_conversation', type='json', auth='user')
    def get_or_create_conversation(self):
        """Get existing or create new conversation"""
        try:
            Conversation = request.env['ai.conversation']

            # Find active conversation for current user
            conversation = Conversation.search([
                ('user_id', '=', request.env.user.id),
                ('active', '=', True)
            ], limit=1, order='create_date desc')

            if not conversation:
                conversation = Conversation.create_new_conversation()

            # Get messages
            messages = []
            for msg in conversation.message_ids:
                messages.append(msg.format_for_display())

            return {
                'conversation_id': conversation.id,
                'messages': messages
            }
        except Exception as e:
            _logger.error(f"Error in get_or_create_conversation: {str(e)}")
            return {'error': str(e)}

    @http.route('/ai_helm/send_message', type='json', auth='user')
    def send_message(self, conversation_id, message):
        """Send message to Claude and get response"""
        try:
            _logger.info(f"=== SEND MESSAGE DEBUG ===")
            _logger.info(f"Conversation ID: {conversation_id}")
            _logger.info(f"User message: {message}")

            from ..services.claude_cli_interface import get_claude_cli

            Conversation = request.env['ai.conversation']
            Message = request.env['ai.conversation.message']

            conversation = Conversation.browse(conversation_id)
            if not conversation.exists():
                _logger.error(f"Conversation {conversation_id} not found")
                return {'error': 'Conversation not found'}

            # Save user message
            user_msg = Message.create({
                'conversation_id': conversation_id,
                'message_type': 'user',
                'content': message,
                'status': 'complete'
            })
            _logger.info(f"User message saved with ID: {user_msg.id}")

            # Get Claude response
            cli = get_claude_cli()
            _logger.info(f"CLI instance obtained: {cli}")

            result = cli.execute_command(message, workspace=f"conv_{conversation_id}")
            _logger.info(f"CLI Result Status: {result.get('status')}")
            _logger.info(f"CLI Output: {result.get('output', 'NO OUTPUT')[:500]}")
            _logger.info(f"CLI Errors: {result.get('errors', 'NO ERRORS')}")
            _logger.info(f"CLI Full Result: {json.dumps(result, indent=2)}")

            # Prepare response content
            response_content = None

            # Try to get output from different possible fields
            if result.get('status') == 'success':
                response_content = result.get('output', '').strip()

                # If output is empty, check other fields
                if not response_content:
                    response_content = result.get('response', '').strip()

                if not response_content:
                    response_content = result.get('message', '').strip()

                if not response_content:
                    _logger.warning("Success status but no content found")
                    response_content = "ได้รับคำสั่งแล้ว แต่ไม่มีข้อความตอบกลับ"
            else:
                # Error case
                response_content = result.get('error', '')
                if not response_content:
                    response_content = result.get('errors', '')
                if not response_content:
                    response_content = "เกิดข้อผิดพลาดในการประมวลผล"

            _logger.info(f"Final response content: {response_content}")

            # Handle empty response
            if not response_content or response_content == 'assistant':
                _logger.warning("Empty or invalid response, using default")
                response_content = f"ขออภัย ไม่สามารถประมวลผลคำสั่ง '{message}' ได้ในขณะนี้"

            # Save assistant response
            assistant_msg = Message.create({
                'conversation_id': conversation_id,
                'message_type': 'assistant' if result.get('status') == 'success' else 'error',
                'content': response_content,
                'code_blocks': json.dumps(result.get('code_blocks', [])),
                'status': 'complete'
            })
            _logger.info(f"Assistant message saved with ID: {assistant_msg.id}")
            _logger.info(f"Assistant message content: {assistant_msg.content}")

            response = {
                'response': assistant_msg.content,
                'code_blocks': result.get('code_blocks', [])
            }

            _logger.info(f"Returning response: {json.dumps(response, indent=2)}")
            return response

        except Exception as e:
            _logger.error(f"Error in send_message: {str(e)}", exc_info=True)

            # Try to save error message
            try:
                Message.create({
                    'conversation_id': conversation_id,
                    'message_type': 'error',
                    'content': f"Error: {str(e)}",
                    'status': 'error'
                })
            except:
                pass

            return {
                'response': f"เกิดข้อผิดพลาด: {str(e)}",
                'code_blocks': []
            }

    @http.route('/ai_helm/clear_conversation', type='json', auth='user')
    def clear_conversation(self, conversation_id):
        """Clear conversation messages"""
        try:
            Conversation = request.env['ai.conversation']
            conversation = Conversation.browse(conversation_id)

            if conversation.exists():
                conversation.message_ids.unlink()
                _logger.info(f"Cleared conversation {conversation_id}")
                return {'success': True}

            return {'error': 'Conversation not found'}
        except Exception as e:
            _logger.error(f"Error clearing conversation: {str(e)}")
            return {'error': str(e)}