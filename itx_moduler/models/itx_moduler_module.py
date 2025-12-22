# -*- coding: utf-8 -*-

import base64
import logging

import lxml
from docutils.core import publish_string
from odoo import models, fields, api, modules, tools, _
from odoo.addons.base.models.ir_module import MyWriter

_logger = logging.getLogger(__name__)


class ItxModulerModule(models.Model):
    _inherit = 'ir.module.module'
    _name = 'itx.moduler.module'
    _description = 'ITX Moduler Module'

    country_ids = fields.Many2many(
        'ir.module.module', 'itx_moduler_module_rel',
        'module_id', 'tag_id',
        string='Tags')

    name = fields.Char(
        readonly=False
    )

    category_id = fields.Many2one(
        readonly=False
    )

    shortdesc = fields.Char(
        readonly=False,
        required=True
    )

    summary = fields.Char(
        readonly=False
    )

    description = fields.Text(
        readonly=False
    )

    author = fields.Char(
        readonly=False
    )

    maintainer = fields.Char(
        readonly=False
    )

    contributors = fields.Text(
        readonly=False
    )

    website = fields.Char(
        readonly=False
    )

    latest_version = fields.Char(
        readonly=False
    )

    published_version = fields.Char(
        readonly=False
    )

    url = fields.Char(
        readonly=False
    )

    dependencies_id = fields.One2many(
        'itx.moduler.module.dependency',
        'module_id',
        readonly=False
    )

    state = fields.Selection(
        readonly=False,
        default='uninstalled'
    )

    demo = fields.Boolean(
        readonly=False
    )

    license = fields.Selection(
        readonly=False
    )

    application = fields.Boolean(
        readonly=False
    )

    icon_image = fields.Binary(
        readonly=False
    )

    o2m_groups = fields.One2many(
        'res.groups',
        'm2o_module'
    )

    o2m_models = fields.One2many(
        'itx.moduler.model',
        'module_id',
        string='Models (Snapshot)',
        help='Snapshot models for code generation - persists after source module uninstall'
    )

    o2m_model_access = fields.Many2many(
        'ir.model.access',
        compute='_get_models_info'
    )

    o2m_model_rules = fields.Many2many(
        'ir.rule',
        compute='_get_models_info'
    )

    o2m_model_constraints = fields.Many2many(
        'ir.model.constraint',
        compute='_get_models_info'
    )

    o2m_model_views = fields.Many2many(
        'ir.ui.view',
        compute='_get_models_info'
    )

    o2m_model_act_window = fields.Many2many(
        'ir.actions.act_window',
        compute='_get_models_info'
    )

    o2m_model_act_server = fields.Many2many(
        'ir.actions.server',
        compute='_get_models_info'
    )

    o2m_model_serverconstrains = fields.Many2many(
        'ir.model.server_constrain',
        compute='_get_models_info'
    )

    o2m_model_reports = fields.Many2many(
        'ir.actions.report',
        compute='_get_models_info'
    )

    @api.depends('o2m_models', 'name')
    def _get_models_info(self):
        for module in self:
            # Collect ACLs from ir.model.access based on module name
            all_access = self.env['ir.model.access'].search([
                '|',
                ('name', 'ilike', module.name),
                ('id', 'in', [])  # Will be extended below
            ])

            # Also get ACLs from ir.model.data
            access_data = self.env['ir.model.data'].search([
                ('module', '=', module.name),
                ('model', '=', 'ir.model.access')
            ])
            if access_data:
                access_ids = access_data.mapped('res_id')
                all_access |= self.env['ir.model.access'].browse(access_ids)

            # Set computed fields
            module.o2m_model_access = all_access
            module.o2m_model_rules = self.env['ir.rule'].browse([])
            module.o2m_model_constraints = self.env['ir.model.constraint'].browse([])
            module.o2m_model_views = self.env['ir.ui.view'].browse([])
            module.o2m_model_act_window = self.env['ir.actions.act_window'].browse([])
            module.o2m_model_act_server = self.env['ir.actions.server'].browse([])
            module.o2m_model_serverconstrains = self.env['ir.model.server_constrain'].browse([])
            module.o2m_model_reports = self.env['ir.actions.report'].browse([])

    o2m_views = fields.One2many(
        'itx.moduler.view',
        'module_id',
        string='Views (Snapshot)',
        help='Snapshot views for code generation - persists after source module uninstall'
    )

    o2m_actions = fields.One2many(
        'itx.moduler.action.window',
        'module_id',
        string='Window Actions (Snapshot)',
        help='Snapshot actions for code generation - persists after source module uninstall'
    )

    o2m_menus = fields.One2many(
        'itx.moduler.menu',
        'module_id',
        string='Menus (Snapshot)',
        help='Snapshot menus for code generation - persists after source module uninstall'
    )

    # Sprint 3: Security & Advanced Elements (Snapshot Architecture)
    o2m_groups_snapshot = fields.One2many(
        'itx.moduler.group',
        'module_id',
        string='Groups (Snapshot)',
        help='Snapshot groups - persists after source module uninstall'
    )

    o2m_acls_snapshot = fields.One2many(
        'itx.moduler.acl',
        'module_id',
        string='ACLs (Snapshot)',
        help='Snapshot ACLs - persists after source module uninstall'
    )

    o2m_rules_snapshot = fields.One2many(
        'itx.moduler.rule',
        'module_id',
        string='Rules (Snapshot)',
        help='Snapshot record rules - persists after source module uninstall'
    )

    o2m_server_actions_snapshot = fields.One2many(
        'itx.moduler.server.action',
        'module_id',
        string='Server Actions (Snapshot)',
        help='Snapshot server actions - persists after source module uninstall'
    )

    o2m_reports_snapshot = fields.One2many(
        'itx.moduler.report',
        'module_id',
        string='Reports (Snapshot)',
        help='Snapshot reports - persists after source module uninstall'
    )

    o2m_constraints_snapshot = fields.One2many(
        'itx.moduler.constraint',
        'module_id',
        string='Constraints (Snapshot)',
        help='Snapshot SQL constraints - persists after source module uninstall'
    )

    o2m_server_constraints_snapshot = fields.One2many(
        'itx.moduler.server.constraint',
        'module_id',
        string='Python Constraints (Snapshot)',
        help='Snapshot Python constraints - persists after source module uninstall'
    )

    # === Workspace Statistics (for Dashboard) ===
    # These fields show real-time stats of what's in the workspace
    snapshot_model_count = fields.Integer(
        string='Models in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of models in this module workspace'
    )

    snapshot_view_count = fields.Integer(
        string='Views in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of views in this module workspace'
    )

    snapshot_menu_count = fields.Integer(
        string='Menus in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of menus in this module workspace'
    )

    snapshot_action_count = fields.Integer(
        string='Actions in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of actions in this module workspace'
    )

    snapshot_group_count = fields.Integer(
        string='Groups in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of groups in this module workspace'
    )

    snapshot_acl_count = fields.Integer(
        string='ACLs in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of ACLs in this module workspace'
    )

    snapshot_rule_count = fields.Integer(
        string='Rules in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of record rules in this module workspace'
    )

    snapshot_server_action_count = fields.Integer(
        string='Server Actions in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of server actions in this module workspace'
    )

    snapshot_report_count = fields.Integer(
        string='Reports in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of reports in this module workspace'
    )

    snapshot_constraint_count = fields.Integer(
        string='SQL Constraints in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of SQL constraints in this module workspace'
    )

    snapshot_server_constraint_count = fields.Integer(
        string='Python Constraints in Workspace',
        compute='_compute_workspace_stats',
        store=False,
        help='Number of Python constraints in this module workspace'
    )

    workspace_status = fields.Selection([
        ('empty', 'Empty'),
        ('draft', 'Draft'),
        ('editing', 'Editing'),
        ('ready', 'Ready'),
        ('applied', 'Applied'),
        ('exported', 'Exported'),
    ], string='Workspace Status', compute='_compute_workspace_status', store=False)

    workspace_status_color = fields.Integer(
        string='Status Color',
        compute='_compute_workspace_status',
        store=False,
        help='Color for kanban card (0-11)'
    )

    last_activity = fields.Datetime(
        string='Last Activity',
        compute='_compute_last_activity',
        store=False,
        help='Last modification in this workspace'
    )

    @api.depends('name')
    def _compute_workspace_stats(self):
        """Compute workspace statistics for dashboard display"""
        for module in self:
            # Count snapshot records (workspace items)
            module.snapshot_model_count = self.env['itx.moduler.model'].search_count([
                ('module_id', '=', module.id)
            ])
            module.snapshot_view_count = self.env['itx.moduler.view'].search_count([
                ('module_id', '=', module.id)
            ])
            module.snapshot_menu_count = self.env['itx.moduler.menu'].search_count([
                ('module_id', '=', module.id)
            ])
            module.snapshot_action_count = self.env['itx.moduler.action.window'].search_count([
                ('module_id', '=', module.id)
            ])
            module.snapshot_group_count = self.env['itx.moduler.group'].search_count([
                ('module_id', '=', module.id)
            ])
            module.snapshot_acl_count = self.env['itx.moduler.acl'].search_count([
                ('module_id', '=', module.id)
            ])
            module.snapshot_rule_count = self.env['itx.moduler.rule'].search_count([
                ('module_id', '=', module.id)
            ])
            module.snapshot_server_action_count = self.env['itx.moduler.server.action'].search_count([
                ('module_id', '=', module.id)
            ])
            module.snapshot_report_count = self.env['itx.moduler.report'].search_count([
                ('module_id', '=', module.id)
            ])
            module.snapshot_constraint_count = self.env['itx.moduler.constraint'].search_count([
                ('module_id', '=', module.id),
                ('type', '=', 'u')  # SQL constraints (UNIQUE)
            ]) + self.env['itx.moduler.constraint'].search_count([
                ('module_id', '=', module.id),
                ('type', '=', 'c')  # SQL constraints (CHECK)
            ])
            module.snapshot_server_constraint_count = self.env['itx.moduler.server.constraint'].search_count([
                ('module_id', '=', module.id)
            ])

    @api.depends('name')
    def _compute_workspace_status(self):
        """Compute overall workspace status based on snapshot states"""
        for module in self:
            # Get all snapshot models
            models = self.env['itx.moduler.model'].search([('module_id', '=', module.id)])

            if not models:
                module.workspace_status = 'empty'
                module.workspace_status_color = 7  # Gray
            else:
                # Check states
                states = models.mapped('state')

                if 'exported' in states:
                    module.workspace_status = 'exported'
                    module.workspace_status_color = 10  # Green
                elif all(state == 'applied' for state in states):
                    module.workspace_status = 'applied'
                    module.workspace_status_color = 3  # Blue
                elif any(state == 'applied' for state in states):
                    module.workspace_status = 'ready'
                    module.workspace_status_color = 9  # Purple
                elif any(state == 'validated' for state in states):
                    module.workspace_status = 'editing'
                    module.workspace_status_color = 1  # Orange
                else:
                    module.workspace_status = 'draft'
                    module.workspace_status_color = 8  # Yellow

    @api.depends('name')
    def _compute_last_activity(self):
        """Compute last modification time in workspace"""
        for module in self:
            # Get latest write_date from all workspace items
            dates = []

            models = self.env['itx.moduler.model'].search([
                ('module_id', '=', module.id)
            ], order='write_date desc', limit=1)
            if models:
                dates.append(models.write_date)

            views = self.env['itx.moduler.view'].search([
                ('module_id', '=', module.id)
            ], order='write_date desc', limit=1)
            if views:
                dates.append(views.write_date)

            menus = self.env['itx.moduler.menu'].search([
                ('module_id', '=', module.id)
            ], order='write_date desc', limit=1)
            if menus:
                dates.append(menus.write_date)

            actions = self.env['itx.moduler.action.window'].search([
                ('module_id', '=', module.id)
            ], order='write_date desc', limit=1)
            if actions:
                dates.append(actions.write_date)

            module.last_activity = max(dates) if dates else fields.Datetime.now()

    @api.depends('name', 'description')
    def _get_desc(self):
        for module in self:
            if module.name and module.description:
                path = modules.get_module_resource(module.name, 'static/description/index.html')
                if path:
                    with tools.file_open(path, 'rb') as desc_file:
                        doc = desc_file.read()
                        html = lxml.html.document_fromstring(doc)
                        for element, attribute, link, pos in html.iterlinks():
                            if element.get('src') and '//' not in element.get('src') and \
                                    'static/' not in element.get('src'):
                                element.set('src', "/%s/static/description/%s" % (module.name, element.get('src')))
                        module.description_html = tools.html_sanitize(lxml.html.tostring(html))
                else:
                    overrides = {
                        'embed_stylesheet': False,
                        'doctitle_xform': False,
                        'output_encoding': 'unicode',
                        'xml_declaration': False,
                        'file_insertion_enabled': False,
                    }
                    output = publish_string(
                        source=module.description if not module.application and module.description else '',
                        settings_overrides=overrides, writer=MyWriter()
                    )
                    module.description_html = tools.html_sanitize(output)

    @api.depends('icon')
    def _get_icon_image(self):
        for module in self:
            module.icon_image = ''
            if module.icon:
                path_parts = module.icon.split('/')
                path = modules.get_module_resource(path_parts[1], *path_parts[2:])
            else:
                path = modules.module.get_module_icon(module.name)
                path = path[1:]
            if path:
                with tools.file_open(path, 'rb') as image_file:
                    module.icon_image = base64.b64encode(image_file.read())

    @api.model
    def create(self, vals):
        return super(models.Model, self).create(vals)

    def action_import_from_module(self):
        """Open a wizard to select and import an existing Odoo module"""
        return {
            'name': 'Import Odoo Module',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.module.module',
            'view_mode': 'list',
            'views': [(False, 'list')],
            'domain': [('state', '=', 'installed'), ('name', 'not in', ['base', 'web'])],
            'target': 'new',
            'context': {
                'search_default_app': 1,
                'create': False,
                'edit': False,
            },
        }

    @api.model
    def create_from_odoo_module(self, module_id):
        """Create a itx.moduler.module from an existing ir.module.module"""
        source_module = self.env['ir.module.module'].browse(module_id)

        # Check if already exists
        existing = self.search([('name', '=', source_module.name)], limit=1)
        if existing:
            return existing

        # Create new ITX Moduler module
        vals = {
            'name': source_module.name,
            'shortdesc': source_module.shortdesc,
            'summary': source_module.summary,
            'description': source_module.description,
            'author': source_module.author,
            'website': source_module.website,
            'category_id': source_module.category_id.id,
            'license': source_module.license,
            'application': source_module.application,
            'state': source_module.state,
        }

        new_module = self.create(vals)

        # ========================================
        # OLD CODE - DISABLED (Using Snapshot Architecture instead)
        # ========================================
        # Previously we changed ownership of ir.model, ir.ui.menu, res.groups
        # This was DANGEROUS because uninstalling source module would delete them!
        # Now we use Snapshot Architecture - we create copies in snapshot tables
        # ========================================
        # Link models that belong to this module using ir.model.data
        # model_data = self.env['ir.model.data'].search([
        #     ('module', '=', source_module.name),
        #     ('model', '=', 'ir.model')
        # ])
        # if model_data:
        #     model_ids = model_data.mapped('res_id')
        #     models_to_link = self.env['ir.model'].browse(model_ids)
        #     models_to_link.write({'m2o_module': new_module.id})

        # Link menus that belong to this module using ir.model.data
        # menu_data = self.env['ir.model.data'].search([
        #     ('module', '=', source_module.name),
        #     ('model', '=', 'ir.ui.menu')
        # ])
        # if menu_data:
        #     menu_ids = menu_data.mapped('res_id')
        #     menus_to_link = self.env['ir.ui.menu'].browse(menu_ids)
        #     menus_to_link.write({'m2o_module': new_module.id})

        # Link groups that belong to this module
        # group_data = self.env['ir.model.data'].search([
        #     ('module', '=', source_module.name),
        #     ('model', '=', 'res.groups')
        # ])
        # if group_data:
        #     group_ids = group_data.mapped('res_id')
        #     groups_to_link = self.env['res.groups'].browse(group_ids)
        #     groups_to_link.write({'m2o_module': new_module.id})
        # ========================================

        # Import snapshots (models, fields, views, menus, actions)
        new_module.action_import_snapshots()

        return new_module

    def action_import_snapshots(self):
        """Import module data into snapshot tables"""
        self.ensure_one()

        # Import Models and Fields
        model_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'ir.model')
        ])

        if model_data:
            model_ids = model_data.mapped('res_id')
            ir_models = self.env['ir.model'].browse(model_ids)

            for ir_model in ir_models:
                # Skip if already imported
                existing_snapshot = self.env['itx.moduler.model'].search([
                    ('model', '=', ir_model.model),
                    ('module_id', '=', self.id)
                ], limit=1)

                if existing_snapshot:
                    continue

                # Create model snapshot
                model_snapshot = self.env['itx.moduler.model'].create({
                    'name': ir_model.name,
                    'model': ir_model.model,
                    'module_id': self.id,
                    'description': ir_model.info or '',
                    'transient_model': ir_model.transient,
                    'state': 'applied',
                    'ir_model_id': ir_model.id,
                })

                # Import fields
                for ir_field in ir_model.field_id:
                    # Skip magic fields
                    if ir_field.name in ('id', 'create_uid', 'create_date',
                                         'write_uid', 'write_date', '__last_update',
                                         'display_name'):
                        continue

                    # Skip fields with unsupported types
                    supported_types = [
                        'char', 'text', 'html', 'integer', 'float', 'monetary',
                        'boolean', 'date', 'datetime', 'binary', 'selection',
                        'many2one', 'one2many', 'many2many', 'many2one_reference',
                        'reference', 'json', 'properties', 'properties_definition'
                    ]
                    if ir_field.ttype not in supported_types:
                        continue

                    field_vals = {
                        'model_id': model_snapshot.id,
                        'name': ir_field.name,
                        'field_description': ir_field.field_description,
                        'ttype': ir_field.ttype,
                        'required': ir_field.required,
                        'readonly': ir_field.readonly,
                        'help': ir_field.help or '',
                    }

                    # Relational fields
                    if ir_field.ttype in ('many2one', 'one2many', 'many2many'):
                        field_vals['relation'] = ir_field.relation
                        if ir_field.ttype == 'one2many':
                            # Skip one2many without relation_field
                            if not ir_field.relation_field:
                                continue
                            field_vals['relation_field'] = ir_field.relation_field

                    # Selection fields
                    if ir_field.ttype == 'selection' and ir_field.selection_ids:
                        field = self.env['itx.moduler.model.field'].create(field_vals)
                        for selection in ir_field.selection_ids:
                            self.env['itx.moduler.model.field.selection'].create({
                                'field_id': field.id,
                                'value': selection.value,
                                'label': selection.name,
                                'sequence': selection.sequence,
                            })
                    else:
                        self.env['itx.moduler.model.field'].create(field_vals)

        # Import Views
        view_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'ir.ui.view')
        ])

        if view_data:
            view_ids = view_data.mapped('res_id')
            ir_views = self.env['ir.ui.view'].browse(view_ids)

            for ir_view in ir_views:
                # Find corresponding model snapshot
                model_snapshot = self.env['itx.moduler.model'].search([
                    ('model', '=', ir_view.model),
                    ('module_id', '=', self.id)
                ], limit=1)

                if not model_snapshot:
                    continue

                # Skip if already imported
                existing = self.env['itx.moduler.view'].search([
                    ('name', '=', ir_view.name),
                    ('model_id', '=', model_snapshot.id)
                ], limit=1)

                if existing:
                    continue

                self.env['itx.moduler.view'].create({
                    'name': ir_view.name,
                    'module_id': self.id,
                    'model_id': model_snapshot.id,
                    'view_type': ir_view.type,
                    'arch': ir_view.arch,
                    'mode': 'extension' if ir_view.inherit_id else 'primary',
                    'inherit_id': ir_view.inherit_id.id if ir_view.inherit_id else False,
                    'state': 'applied',
                    'ir_view_id': ir_view.id,
                })

        # Import Actions
        action_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'ir.actions.act_window')
        ])

        if action_data:
            action_ids = action_data.mapped('res_id')
            ir_actions = self.env['ir.actions.act_window'].browse(action_ids)

            for ir_action in ir_actions:
                # Find corresponding model snapshot
                model_snapshot = self.env['itx.moduler.model'].search([
                    ('model', '=', ir_action.res_model),
                    ('module_id', '=', self.id)
                ], limit=1)

                if not model_snapshot:
                    continue

                # Skip if already imported
                existing = self.env['itx.moduler.action.window'].search([
                    ('name', '=', ir_action.name),
                    ('model_id', '=', model_snapshot.id)
                ], limit=1)

                if existing:
                    continue

                # Safely convert context to string
                context_str = '{}'
                if ir_action.context:
                    try:
                        import json
                        # Try to convert context to JSON string
                        if isinstance(ir_action.context, dict):
                            context_str = json.dumps(ir_action.context)
                        else:
                            context_str = str(ir_action.context)
                    except:
                        context_str = '{}'

                self.env['itx.moduler.action.window'].create({
                    'name': ir_action.name,
                    'module_id': self.id,
                    'model_id': model_snapshot.id,
                    'view_mode': ir_action.view_mode,
                    'domain': ir_action.domain or '[]',
                    'context': context_str,
                    'limit': ir_action.limit,
                    'target': ir_action.target,
                    'help': ir_action.help or '',
                    'state': 'applied',
                    'ir_action_id': ir_action.id,
                })

        # Import Menus
        menu_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'ir.ui.menu')
        ])

        if menu_data:
            menu_ids = menu_data.mapped('res_id')
            ir_menus = self.env['ir.ui.menu'].browse(menu_ids).sorted(
                lambda m: len(m.parent_path or ''), reverse=False
            )

            for ir_menu in ir_menus:
                # Skip if already imported
                existing = self.env['itx.moduler.menu'].search([
                    ('name', '=', ir_menu.name),
                    ('module_id', '=', self.id)
                ], limit=1)

                if existing:
                    continue

                # Find parent menu snapshot
                parent_snapshot = False
                if ir_menu.parent_id:
                    parent_snapshot = self.env['itx.moduler.menu'].search([
                        ('ir_menu_id', '=', ir_menu.parent_id.id)
                    ], limit=1)

                # Find action snapshot
                action_snapshot = False
                if ir_menu.action and 'act_window' in ir_menu.action._name:
                    action_snapshot = self.env['itx.moduler.action.window'].search([
                        ('ir_action_id', '=', ir_menu.action.id)
                    ], limit=1)

                self.env['itx.moduler.menu'].create({
                    'name': ir_menu.name,
                    'module_id': self.id,
                    'sequence': ir_menu.sequence,
                    'parent_id': parent_snapshot.id if parent_snapshot else False,
                    'action_id': action_snapshot.id if action_snapshot else False,
                    'web_icon': ir_menu.web_icon,
                    'state': 'applied',
                    'ir_menu_id': ir_menu.id,
                })

        # Import Groups into snapshot table
        group_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'res.groups')
        ])

        if group_data:
            group_ids = group_data.mapped('res_id')
            ir_groups = self.env['res.groups'].browse(group_ids)

            for ir_group in ir_groups:
                # Skip if already imported
                existing = self.env['itx.moduler.group'].search([
                    ('name', '=', ir_group.name),
                    ('module_id', '=', self.id)
                ], limit=1)

                if existing:
                    continue

                # Create group snapshot
                # Odoo 19: res.groups.category_id moved to res.groups.privilege_id.category_id
                category_id = False
                try:
                    if hasattr(ir_group, 'privilege_id') and ir_group.privilege_id:
                        # Odoo 19+: category is under privilege
                        if hasattr(ir_group.privilege_id, 'category_id') and ir_group.privilege_id.category_id:
                            category_id = ir_group.privilege_id.category_id.id
                    elif hasattr(ir_group, 'category_id') and ir_group.category_id:
                        # Odoo 18 and earlier: category directly on group
                        category_id = ir_group.category_id.id
                except AttributeError:
                    # Some groups may not have category - that's ok
                    pass

                self.env['itx.moduler.group'].create({
                    'name': ir_group.name,
                    'module_id': self.id,
                    'category_id': category_id,
                    'comment': ir_group.comment or '',
                    'implied_ids': [(6, 0, ir_group.implied_ids.ids)],
                    'state': 'applied',
                    'ir_group_id': ir_group.id,
                })
                _logger.info(f"✅ Imported Group: {ir_group.name}")

        # Import ACLs (Access Control Lists) into snapshot table
        self.env.flush_all()

        # Get ACLs by ir.model.data
        acl_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'ir.model.access')
        ])

        acl_records = self.env['ir.model.access'].browse([])

        if acl_data:
            acl_records = self.env['ir.model.access'].browse(acl_data.mapped('res_id'))
            _logger.info(f"🔍 Found {len(acl_records)} ACLs via ir.model.data")
        else:
            # Fallback: Search ACLs by models in this module (for CSV imports)
            model_names = self.env['itx.moduler.model'].search([
                ('module_id', '=', self.id)
            ]).mapped('model')

            if model_names:
                model_ids = self.env['ir.model'].search([('model', 'in', model_names)])
                acl_records = self.env['ir.model.access'].search([
                    ('model_id', 'in', model_ids.ids)
                ])
                _logger.info(f"🔍 Fallback found {len(acl_records)} ACLs by model")

        # Import ACLs into snapshot
        for ir_acl in acl_records:
            # Skip if already imported
            existing = self.env['itx.moduler.acl'].search([
                ('name', '=', ir_acl.name),
                ('module_id', '=', self.id)
            ], limit=1)

            if existing:
                continue

            # Find model snapshot
            model_snapshot = self.env['itx.moduler.model'].search([
                ('model', '=', ir_acl.model_id.model),
                ('module_id', '=', self.id)
            ], limit=1)

            if not model_snapshot:
                continue

            # Find group snapshot (if ACL has group)
            group_snapshot = False
            external_group = False

            if ir_acl.group_id:
                # Check if group is in this module
                group_snapshot = self.env['itx.moduler.group'].search([
                    ('ir_group_id', '=', ir_acl.group_id.id),
                    ('module_id', '=', self.id)
                ], limit=1)

                if not group_snapshot:
                    # External group (e.g., base.group_user)
                    external_group = ir_acl.group_id

            # Create ACL snapshot
            self.env['itx.moduler.acl'].create({
                'name': ir_acl.name,
                'module_id': self.id,
                'model_id': model_snapshot.id,
                'group_id': group_snapshot.id if group_snapshot else False,
                'external_group_id': external_group.id if external_group else False,
                'perm_read': ir_acl.perm_read,
                'perm_write': ir_acl.perm_write,
                'perm_create': ir_acl.perm_create,
                'perm_unlink': ir_acl.perm_unlink,
                'state': 'applied',
                'ir_access_id': ir_acl.id,
            })
            _logger.info(f"✅ Imported ACL: {ir_acl.name}")

        # Import Rules (Record Rules) into snapshot table
        rule_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'ir.rule')
        ])

        if rule_data:
            rule_ids = rule_data.mapped('res_id')
            ir_rules = self.env['ir.rule'].browse(rule_ids)

            for ir_rule in ir_rules:
                existing = self.env['itx.moduler.rule'].search([
                    ('name', '=', ir_rule.name),
                    ('module_id', '=', self.id)
                ], limit=1)

                if existing:
                    continue

                model_snapshot = self.env['itx.moduler.model'].search([
                    ('model', '=', ir_rule.model_id.model),
                    ('module_id', '=', self.id)
                ], limit=1)

                if not model_snapshot:
                    continue

                # Find group snapshots
                group_snapshots = self.env['itx.moduler.group'].search([
                    ('ir_group_id', 'in', ir_rule.groups.ids),
                    ('module_id', '=', self.id)
                ])

                external_groups = ir_rule.groups - self.env['res.groups'].browse(group_snapshots.mapped('ir_group_id').ids)

                self.env['itx.moduler.rule'].create({
                    'name': ir_rule.name,
                    'module_id': self.id,
                    'model_id': model_snapshot.id,
                    'active': ir_rule.active,
                    'domain_force': ir_rule.domain_force or '[]',
                    'group_ids': [(6, 0, group_snapshots.ids)],
                    'external_group_ids': [(6, 0, external_groups.ids)],
                    'perm_read': ir_rule.perm_read,
                    'perm_write': ir_rule.perm_write,
                    'perm_create': ir_rule.perm_create,
                    'perm_unlink': ir_rule.perm_unlink,
                    'global_rule': getattr(ir_rule, 'global', False),
                    'state': 'applied',
                    'ir_rule_id': ir_rule.id,
                })
                _logger.info(f"✅ Imported Rule: {ir_rule.name}")

        # Import Action Servers (Automated Actions) into snapshot table
        action_server_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'ir.actions.server')
        ])

        if action_server_data:
            server_ids = action_server_data.mapped('res_id')
            ir_servers = self.env['ir.actions.server'].browse(server_ids)

            for ir_server in ir_servers:
                existing = self.env['itx.moduler.server.action'].search([
                    ('name', '=', ir_server.name),
                    ('module_id', '=', self.id)
                ], limit=1)

                if existing:
                    continue

                model_snapshot = self.env['itx.moduler.model'].search([
                    ('model', '=', ir_server.model_id.model),
                    ('module_id', '=', self.id)
                ], limit=1)

                if not model_snapshot:
                    continue

                self.env['itx.moduler.server.action'].create({
                    'name': ir_server.name,
                    'module_id': self.id,
                    'model_id': model_snapshot.id,
                    'state': ir_server.state,
                    'code': ir_server.code or '',
                    'action_state': 'applied',
                    'ir_action_id': ir_server.id,
                })
                _logger.info(f"✅ Imported Server Action: {ir_server.name}")

        # Import Reports into snapshot table
        report_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'ir.actions.report')
        ])

        if report_data:
            report_ids = report_data.mapped('res_id')
            ir_reports = self.env['ir.actions.report'].browse(report_ids)

            for ir_report in ir_reports:
                existing = self.env['itx.moduler.report'].search([
                    ('name', '=', ir_report.name),
                    ('module_id', '=', self.id)
                ], limit=1)

                if existing:
                    continue

                model_snapshot = self.env['itx.moduler.model'].search([
                    ('model', '=', ir_report.model),
                    ('module_id', '=', self.id)
                ], limit=1)

                if not model_snapshot:
                    continue

                self.env['itx.moduler.report'].create({
                    'name': ir_report.name,
                    'module_id': self.id,
                    'model_id': model_snapshot.id,
                    'report_type': ir_report.report_type,
                    'report_name': ir_report.report_name,
                    'report_file': ir_report.report_file or ir_report.report_name,
                    'print_report_name': ir_report.print_report_name or '',
                    'paperformat_id': ir_report.paperformat_id.id if ir_report.paperformat_id else False,
                    'multi': ir_report.multi,
                    'state': 'applied',
                    'ir_report_id': ir_report.id,
                })
                _logger.info(f"✅ Imported Report: {ir_report.name}")

        # Import SQL Constraints into snapshot table
        constraint_data = self.env['ir.model.data'].search([
            ('module', '=', self.name),
            ('model', '=', 'ir.model.constraint')
        ])

        if constraint_data:
            constraint_ids = constraint_data.mapped('res_id')
            ir_constraints = self.env['ir.model.constraint'].browse(constraint_ids)

            for ir_constraint in ir_constraints:
                existing = self.env['itx.moduler.constraint'].search([
                    ('name', '=', ir_constraint.name),
                    ('module_id', '=', self.id)
                ], limit=1)

                if existing:
                    continue

                model_snapshot = self.env['itx.moduler.model'].search([
                    ('ir_model_id', '=', ir_constraint.model.id),
                    ('module_id', '=', self.id)
                ], limit=1)

                if not model_snapshot:
                    continue

                self.env['itx.moduler.constraint'].create({
                    'name': ir_constraint.name,
                    'module_id': self.id,
                    'model_id': model_snapshot.id,
                    'type': ir_constraint.type,
                    'definition': ir_constraint.definition or '',
                    'message': ir_constraint.message or '',
                    'state': 'applied',
                    'ir_constraint_id': ir_constraint.id,
                })
                _logger.info(f"✅ Imported SQL Constraint: {ir_constraint.name}")

        # Import Python Constraints from model registry
        import inspect

        model_snapshots = self.env['itx.moduler.model'].search([
            ('module_id', '=', self.id)
        ])

        for model_snapshot in model_snapshots:
            if not model_snapshot.ir_model_id:
                continue

            try:
                # Get the actual Python model class
                py_model = self.env[model_snapshot.model]

                # Check if model has constraint methods
                if hasattr(py_model, '_constraint_methods'):
                    for method_name in py_model._constraint_methods:
                        method = getattr(py_model.__class__, method_name, None)
                        if not method:
                            continue

                        # Get constraint info from method
                        constraint_fields = getattr(method, '_constrains', [])
                        if not constraint_fields:
                            continue

                        # Check if already imported
                        existing = self.env['itx.moduler.server.constraint'].search([
                            ('name', '=', method_name),
                            ('model_id', '=', model_snapshot.id),
                            ('module_id', '=', self.id)
                        ], limit=1)

                        if existing:
                            continue

                        # Get method docstring as description
                        description = method.__doc__ or f"Python constraint on {', '.join(constraint_fields)}"

                        # Try to get source code
                        try:
                            source_code = inspect.getsource(method)
                        except Exception:
                            # Fallback if source not available
                            source_code = f'''# Constraint method: {method_name}
# Validates: {', '.join(constraint_fields)}
for record in self:
    # Original validation logic
    pass
'''

                        # Create Python constraint snapshot
                        self.env['itx.moduler.server.constraint'].create({
                            'name': method_name,
                            'module_id': self.id,
                            'model_id': model_snapshot.id,
                            'field_names': ', '.join(constraint_fields),
                            'code': source_code,
                            'description': description.strip(),
                            'message': 'Validation failed',  # Default message
                            'state': 'applied',
                        })
                        _logger.info(f"✅ Imported Python Constraint: {method_name} on {model_snapshot.model}")

            except Exception as e:
                _logger.warning(f"⚠️ Could not import Python constraints for {model_snapshot.model}: {e}")
                continue

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Import Complete'),
                'message': _('Module "%s" imported successfully into snapshots') % self.name,
                'type': 'success',
                'sticky': False,
            }
        }

    def _is_standard_module(self):
        """Check if this is a standard Odoo module"""
        self.ensure_one()

        STANDARD_MODULES = [
            'base', 'web', 'web_studio', 'web_editor',
            'sale', 'sale_management', 'sale_stock',
            'purchase', 'purchase_stock',
            'stock', 'stock_account',
            'account', 'account_payment', 'account_accountant',
            'hr', 'hr_attendance', 'hr_holidays', 'hr_payroll', 'hr_expense', 'hr_recruitment',
            'crm', 'crm_iap',
            'project', 'project_todo',
            'mrp', 'mrp_account',
            'point_of_sale', 'pos_restaurant',
            'website', 'website_sale', 'website_blog',
            'mail', 'calendar', 'contacts',
            'im_livechat', 'helpdesk',
            'survey', 'mass_mailing',
        ]

        return self.name in STANDARD_MODULES

    def unlink(self):
        """Delete module workspace and all related snapshot data"""
        for module in self:
            # ⚠️ NOTE: Groups and ACLs now owned by 'itx_moduler' (changed during import)
            # So they won't be deleted when source module is uninstalled
            # But we need to clean up when deleting workspace itself

            # Delete ACLs owned by itx_moduler for this workspace
            access_data = self.env['ir.model.data'].search([
                ('module', '=', 'itx_moduler'),
                ('model', '=', 'ir.model.access'),
                ('name', 'like', f'{module.name}%')  # Filter by original module name
            ])
            if access_data:
                access_ids = access_data.mapped('res_id')
                access_records = self.env['ir.model.access'].browse(access_ids)
                access_data.unlink()
                access_records.unlink()

            # Delete Groups owned by itx_moduler for this workspace
            group_data = self.env['ir.model.data'].search([
                ('module', '=', 'itx_moduler'),
                ('model', '=', 'res.groups'),
                ('name', 'like', f'{module.name}%')  # Filter by original module name
            ])
            if group_data:
                group_ids = group_data.mapped('res_id')
                group_records = self.env['res.groups'].browse(group_ids)
                group_data.unlink()
                group_records.unlink()

            # Delete Rules owned by itx_moduler for this workspace
            rule_data = self.env['ir.model.data'].search([
                ('module', '=', 'itx_moduler'),
                ('model', '=', 'ir.rule'),
                ('name', 'like', f'{module.name}%')
            ])
            if rule_data:
                rule_ids = rule_data.mapped('res_id')
                rule_records = self.env['ir.rule'].browse(rule_ids)
                rule_data.unlink()
                rule_records.unlink()

            # Delete Action Servers owned by itx_moduler for this workspace
            action_server_data = self.env['ir.model.data'].search([
                ('module', '=', 'itx_moduler'),
                ('model', '=', 'ir.actions.server'),
                ('name', 'like', f'{module.name}%')
            ])
            if action_server_data:
                server_ids = action_server_data.mapped('res_id')
                server_records = self.env['ir.actions.server'].browse(server_ids)
                action_server_data.unlink()
                server_records.unlink()

            # Delete Reports owned by itx_moduler for this workspace
            report_data = self.env['ir.model.data'].search([
                ('module', '=', 'itx_moduler'),
                ('model', '=', 'ir.actions.report'),
                ('name', 'like', f'{module.name}%')
            ])
            if report_data:
                report_ids = report_data.mapped('res_id')
                report_records = self.env['ir.actions.report'].browse(report_ids)
                report_data.unlink()
                report_records.unlink()

            # Snapshot tables (models, views, menus, actions) have ondelete='cascade'
            # They will be auto-deleted when module is deleted

            # Set state to uninstalled to bypass ir.module.module's unlink constraint
            module.write({'state': 'uninstalled'})

        return super(ItxModulerModule, self).unlink()

    def action_generate_xml(self):
        """Generate complete XML export for entire module workspace"""
        self.ensure_one()

        # Collect all snapshot items
        models = self.env['itx.moduler.model'].search([('module_id', '=', self.id)])
        views = self.env['itx.moduler.view'].search([('module_id', '=', self.id)])
        actions = self.env['itx.moduler.action.window'].search([('module_id', '=', self.id)])
        menus = self.env['itx.moduler.menu'].search([('module_id', '=', self.id)])

        # Start XML
        xml_content = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml_content += '<odoo>\n\n'

        # Generate Models XML
        if models:
            xml_content += '    <!-- ============================================ -->\n'
            xml_content += '    <!-- MODELS                                       -->\n'
            xml_content += '    <!-- ============================================ -->\n\n'
            xml_content += '    <!-- TODO: Model XML generation not yet implemented -->\n'
            xml_content += f'    <!-- Found {len(models)} models -->\n\n'
            # for model in models:
            #     xml_content += model._generate_model_xml()
            #     xml_content += '\n'

        # Generate Views XML
        if views:
            xml_content += '    <!-- ============================================ -->\n'
            xml_content += '    <!-- VIEWS                                        -->\n'
            xml_content += '    <!-- ============================================ -->\n\n'
            xml_content += '    <!-- TODO: View XML generation not yet implemented -->\n'
            xml_content += f'    <!-- Found {len(views)} views -->\n\n'
            # for view in views:
            #     view_xml = view._generate_view_xml()
            #     xml_content += f'    <record id="{view.name.lower().replace(" ", "_").replace(".", "_")}" model="ir.ui.view">\n'
            #     xml_content += f'        <field name="name">{view.name}</field>\n'
            #     xml_content += f'        <field name="model">{view.model_id.model}</field>\n'
            #     xml_content += f'        <field name="arch" type="xml">\n'
            #     xml_content += view_xml
            #     xml_content += '        </field>\n'
            #     xml_content += '    </record>\n\n'

        # Generate Actions XML
        if actions:
            xml_content += '    <!-- ============================================ -->\n'
            xml_content += '    <!-- ACTIONS                                      -->\n'
            xml_content += '    <!-- ============================================ -->\n\n'
            xml_content += '    <!-- TODO: Action XML generation not yet implemented -->\n'
            xml_content += f'    <!-- Found {len(actions)} actions -->\n\n'
            # for action in actions:
            #     xml_content += action._generate_action_xml()
            #     xml_content += '\n'

        # Generate Menus XML
        if menus:
            xml_content += '    <!-- ============================================ -->\n'
            xml_content += '    <!-- MENUS                                        -->\n'
            xml_content += '    <!-- ============================================ -->\n\n'
            for menu in menus.sorted(lambda m: len(m.parent_path or ''), reverse=False):
                menu_id = menu.name.lower().replace(' ', '_').replace('.', '_')
                xml_content += f'    <menuitem id="{menu_id}"\n'
                xml_content += f'              name="{menu.name}"\n'
                if menu.parent_id:
                    parent_id = menu.parent_id.name.lower().replace(' ', '_').replace('.', '_')
                    xml_content += f'              parent="{parent_id}"\n'
                if menu.action_id:
                    action_id = menu.action_id.name.lower().replace(' ', '_').replace('.', '_')
                    xml_content += f'              action="{action_id}"\n'
                xml_content += f'              sequence="{menu.sequence}"/>\n\n'

        xml_content += '</odoo>\n'

        # Return action to show XML in code viewer
        return {
            'type': 'ir.actions.act_window',
            'name': f'Export XML - {self.name}',
            'res_model': 'itx.moduler.code.viewer',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_code': xml_content,
                'default_language': 'xml',
                'default_title': f'{self.name} - Complete Module Export'
            }
        }

    def action_view_snapshot_models(self):
        """Open workspace models"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Models - {self.name}',
            'res_model': 'itx.moduler.model',
            'view_mode': 'list,form',
            'domain': [('module_id', '=', self.id)],
            'context': {'default_module_id': self.id}
        }

    def action_view_snapshot_views(self):
        """Open workspace views"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Views - {self.name}',
            'res_model': 'itx.moduler.view',
            'view_mode': 'list,form',
            'domain': [('module_id', '=', self.id)],
            'context': {'default_module_id': self.id}
        }

    def action_view_snapshot_menus(self):
        """Open workspace menus"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Menus - {self.name}',
            'res_model': 'itx.moduler.menu',
            'view_mode': 'list,form',
            'domain': [('module_id', '=', self.id)],
            'context': {'default_module_id': self.id}
        }

    def action_view_snapshot_actions(self):
        """Open workspace actions"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Actions - {self.name}',
            'res_model': 'itx.moduler.action.window',
            'view_mode': 'list,form',
            'domain': [('module_id', '=', self.id)],
            'context': {'default_module_id': self.id}
        }

    @api.model
    def action_open_add_module_wizard(self):
        """Open the Add Module to Workspace wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Module to Workspace',
            'res_model': 'itx.moduler.add.module.wizard',
            'view_mode': 'form',
            'target': 'new',
        }


class ItxModulerModuleDependency(models.Model):
    _inherit = 'ir.module.module.dependency'
    _name = 'itx.moduler.module.dependency'
    _description = 'ITX Moduler Module Dependency'

    module_id = fields.Many2one(
        'itx.moduler.module',
        'Module',
        ondelete='cascade'
    )

    depend_id = fields.Many2one(
        'ir.module.module',
        'Dependency',
        compute=None
    )


class ItxModulerPyClass(models.Model):
    _name = 'itx.moduler.pyclass'
    _description = 'ITX Moduler Python Class'

    name = fields.Char(
        string='Class name',
        help='Class name',
        required=True
    )

    module = fields.Char(
        string='Class path',
        help='Class path'
    )