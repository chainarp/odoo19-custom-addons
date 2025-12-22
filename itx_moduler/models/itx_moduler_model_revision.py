# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api, _


class ItxModulerModelRevision(models.Model):
    _name = 'itx.moduler.model.revision'
    _description = 'Model Revision History'
    _order = 'version desc, create_date desc'
    _rec_name = 'change_summary'

    model_id = fields.Many2one(
        'itx.moduler.model',
        string='Model',
        required=True,
        ondelete='cascade',
        index=True
    )

    version = fields.Integer(
        string='Version',
        required=True,
        help='Version number at time of revision'
    )

    # Complete snapshot
    snapshot_data = fields.Text(
        string='Snapshot Data (JSON)',
        required=True,
        help='JSON snapshot: {model: {...}, fields: [{...}], methods: [{...}]}'
    )

    change_summary = fields.Char(
        string='Change Summary',
        required=True,
        help='Brief description of what changed'
    )

    change_type = fields.Selection([
        ('create', 'Created'),
        ('edit', 'Edited'),
        ('ai_regen', 'AI Regenerated'),
        ('validate', 'Validated'),
        ('apply', 'Applied'),
        ('export', 'Exported'),
    ], string='Change Type', required=True, default='edit')

    # Who/When
    create_uid = fields.Many2one(
        'res.users',
        string='Changed By',
        readonly=True
    )

    create_date = fields.Datetime(
        string='Changed Date',
        readonly=True
    )

    # AI-specific
    created_by_ai = fields.Boolean(
        string='AI Generated',
        default=False
    )

    ai_prompt = fields.Text(
        string='AI Prompt',
        help='Prompt used if AI-generated'
    )

    ai_prompt_diff = fields.Text(
        string='Prompt Changes',
        help='What changed in prompt from previous version'
    )

    # Diff statistics
    fields_added = fields.Integer(
        string='Fields Added',
        compute='_compute_diff_stats',
        store=True
    )

    fields_removed = fields.Integer(
        string='Fields Removed',
        compute='_compute_diff_stats',
        store=True
    )

    fields_modified = fields.Integer(
        string='Fields Modified',
        compute='_compute_diff_stats',
        store=True
    )

    @api.depends('snapshot_data', 'model_id')
    def _compute_diff_stats(self):
        """Calculate what changed from previous revision"""
        for rev in self:
            # Find previous revision
            prev_rev = self.search([
                ('model_id', '=', rev.model_id.id),
                ('id', '<', rev.id)
            ], order='id desc', limit=1)

            if prev_rev and rev.snapshot_data and prev_rev.snapshot_data:
                try:
                    current = json.loads(rev.snapshot_data)
                    previous = json.loads(prev_rev.snapshot_data)

                    current_fields = {f['name']: f for f in current.get('fields', [])}
                    prev_fields = {f['name']: f for f in previous.get('fields', [])}

                    # Calculate diff
                    rev.fields_added = len(set(current_fields.keys()) - set(prev_fields.keys()))
                    rev.fields_removed = len(set(prev_fields.keys()) - set(current_fields.keys()))

                    # Modified = fields that exist in both but changed
                    common_fields = set(current_fields.keys()) & set(prev_fields.keys())
                    modified = 0
                    for fname in common_fields:
                        if current_fields[fname] != prev_fields[fname]:
                            modified += 1
                    rev.fields_modified = modified

                except (json.JSONDecodeError, KeyError):
                    rev.fields_added = 0
                    rev.fields_removed = 0
                    rev.fields_modified = 0
            else:
                # First revision
                rev.fields_added = 0
                rev.fields_removed = 0
                rev.fields_modified = 0

    def action_view_snapshot(self):
        """View snapshot in readable format"""
        self.ensure_one()

        try:
            snapshot = json.loads(self.snapshot_data)
            formatted = json.dumps(snapshot, indent=2)
        except:
            formatted = self.snapshot_data

        return {
            'type': 'ir.actions.act_window',
            'name': f'Snapshot - Version {self.version}',
            'res_model': 'itx.moduler.snapshot.viewer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_snapshot_text': formatted,
                'default_revision_id': self.id
            }
        }

    def action_restore_from_revision(self):
        """Restore model to this revision state"""
        self.ensure_one()

        if not self.snapshot_data:
            raise UserError(_('No snapshot data available'))

        try:
            snapshot = json.loads(self.snapshot_data)
        except json.JSONDecodeError:
            raise UserError(_('Invalid snapshot data'))

        # Create new version from this snapshot
        model = self.model_id

        # Update model data
        model_data = snapshot.get('model', {})
        model.write({
            'name': model_data.get('name', model.name),
            'description': model_data.get('description', ''),
            'inherit_model_names': model_data.get('inherit_model_names', ''),
            'rec_name': model_data.get('rec_name', 'name'),
            'order_field': model_data.get('order_field', 'id desc'),
            'transient_model': model_data.get('transient_model', False),
            'abstract_model': model_data.get('abstract_model', False),
            'state': 'draft',
        })

        # Clear existing fields
        model.field_ids.unlink()

        # Recreate fields from snapshot
        for field_data in snapshot.get('fields', []):
            self.env['itx.moduler.model.field'].create({
                'model_id': model.id,
                'name': field_data.get('name'),
                'field_description': field_data.get('field_description'),
                'ttype': field_data.get('ttype', 'char'),
                'required': field_data.get('required', False),
                'help': field_data.get('help', ''),
            })

        # Clear existing methods
        model.method_ids.unlink()

        # Recreate methods from snapshot
        for method_data in snapshot.get('methods', []):
            self.env['itx.moduler.model.method'].create({
                'model_id': model.id,
                'name': method_data.get('name'),
                'code': method_data.get('code', ''),
            })

        # Create revision for restore action
        model._create_revision('edit', f'Restored from revision {self.version}')

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Restored'),
                'message': _('Model restored from version %s') % self.version,
                'type': 'success',
            }
        }
