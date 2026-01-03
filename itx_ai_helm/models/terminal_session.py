# itx_ai_helm/models/terminal_session.py

from odoo import models, fields, api
import uuid
import os
import signal


class TerminalSession(models.Model):
    _name = 'terminal.session'
    _description = 'Terminal Session'

    name = fields.Char('Session Name', required=True)
    session_id = fields.Char('Session ID', readonly=True)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    pid = fields.Integer('Process ID')
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], default='inactive')
    command = fields.Char('Command', default='claude')
    workspace_path = fields.Char('Workspace Path')

    @api.model
    def create_session(self, command='claude'):
        """Create new terminal session"""
        session_id = str(uuid.uuid4())
        workspace = f"/tmp/terminal_{session_id}"
        os.makedirs(workspace, exist_ok=True)

        return self.create({
            'name': f"Terminal {fields.Datetime.now()}",
            'session_id': session_id,
            'command': command,
            'workspace_path': workspace,
            'state': 'active'
        })

    def kill_session(self):
        """Kill terminal process"""
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGTERM)
            except:
                pass
        self.state = 'inactive'