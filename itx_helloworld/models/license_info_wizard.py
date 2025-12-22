# -*- coding: utf-8 -*-
from odoo import models, fields, api
import os
import logging

_logger = logging.getLogger(__name__)


class LicenseInfoWizard(models.TransientModel):
    _name = 'itx.license.info.wizard'
    _description = 'License Information Viewer'

    # License Information
    license_status = fields.Char(string='License Status', readonly=True)
    customer_name = fields.Char(string='Customer Name', readonly=True)
    po_number = fields.Char(string='PO Number', readonly=True)
    licensed_addons = fields.Text(string='Licensed Addons', readonly=True)
    max_instances = fields.Integer(string='Max Instances', readonly=True)
    expiry_date = fields.Date(string='Expiry Date', readonly=True)
    license_fingerprint = fields.Char(string='License Fingerprint', readonly=True)

    # Hardware Information
    cpu_model = fields.Char(string='CPU Model', readonly=True)
    cpu_cores = fields.Integer(string='CPU Cores', readonly=True)
    machine_id = fields.Char(string='Machine ID', readonly=True)
    mac_address = fields.Char(string='MAC Address', readonly=True)
    dmi_uuid = fields.Char(string='DMI UUID', readonly=True)
    disk_uuid = fields.Char(string='Disk UUID', readonly=True)
    current_fingerprint = fields.Char(string='Current Fingerprint', readonly=True)
    is_docker = fields.Boolean(string='Running in Docker', readonly=True)
    is_vm = fields.Boolean(string='Running in VM', readonly=True)

    # Display fields
    license_valid = fields.Boolean(string='License Valid', readonly=True, compute='_compute_license_valid', store=False)
    error_message = fields.Text(string='Error', readonly=True)

    @api.depends('license_status')
    def _compute_license_valid(self):
        for wizard in self:
            wizard.license_valid = 'Valid' in (wizard.license_status or '')

    @api.model
    def default_get(self, fields_list):
        """Load license and hardware info when wizard opens"""
        res = super().default_get(fields_list)

        try:
            # Import here to avoid issues
            from odoo.addons.itx_security_shield.lib.verifier import get_hardware_info, get_fingerprint
            from odoo.addons.itx_security_shield.tools.license_crypto import load_license_file

            # Get hardware info
            hw_info = get_hardware_info()
            fingerprint = get_fingerprint()

            # Update hardware fields
            res.update({
                'cpu_model': hw_info.get('cpu_model', 'Unknown'),
                'cpu_cores': hw_info.get('cpu_cores', 0),
                'machine_id': hw_info.get('machine_id', 'Unknown')[:32],
                'mac_address': hw_info.get('mac_address', 'Unknown'),
                'dmi_uuid': hw_info.get('dmi_uuid', 'Unknown')[:32],
                'disk_uuid': hw_info.get('disk_uuid', 'Unknown')[:32],
                'current_fingerprint': fingerprint[:32] + '...',
                'is_docker': hw_info.get('is_docker', False),
                'is_vm': hw_info.get('is_vm', False),
            })

            # Try to load license file from itx_security_shield
            shield_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'itx_security_shield'
            )
            license_path = os.path.join(shield_path, 'production.lic')

            if os.path.exists(license_path):
                try:
                    license_data = load_license_file(license_path)

                    # Get hardware fingerprint from first registered instance (if any)
                    license_hw_fingerprint = None
                    if license_data.registered_instances:
                        # Get fingerprint from first active instance
                        for inst in license_data.registered_instances:
                            if inst.get('status') == 'active':
                                license_hw_fingerprint = inst.get('hardware_fingerprint')
                                break
                        # If no active instance, get from first instance
                        if not license_hw_fingerprint and license_data.registered_instances:
                            license_hw_fingerprint = license_data.registered_instances[0].get('hardware_fingerprint')

                    # Update license fields
                    res.update({
                        'customer_name': license_data.customer_name or 'N/A',
                        'po_number': license_data.po_number or 'N/A',
                        'licensed_addons': ', '.join(license_data.licensed_addons) if license_data.licensed_addons else 'All Addons',
                        'max_instances': license_data.max_instances or 1,
                        'expiry_date': license_data.expiry_date,
                        'license_fingerprint': (license_hw_fingerprint[:32] + '...') if license_hw_fingerprint else 'Not bound to hardware',
                    })

                    # Check if license is valid
                    if license_hw_fingerprint:
                        if license_hw_fingerprint == fingerprint:
                            res['license_status'] = 'Valid ✓'
                        else:
                            res['license_status'] = 'Invalid - Hardware Mismatch ✗'
                    else:
                        # No hardware binding yet (multi-instance license)
                        res['license_status'] = 'Valid ✓ (Not yet bound to hardware)'

                except Exception as e:
                    _logger.error(f"Failed to load license: {e}")
                    res['license_status'] = 'Error Loading License'
                    res['error_message'] = str(e)
            else:
                res['license_status'] = 'No License File Found'
                res['error_message'] = f'License file not found at: {license_path}'

        except Exception as e:
            _logger.error(f"Error in license info wizard: {e}")
            import traceback
            traceback.print_exc()
            res['license_status'] = 'Error'
            res['error_message'] = str(e)

        return res

    def action_close(self):
        """Close the wizard"""
        return {'type': 'ir.actions.act_window_close'}

    def action_refresh(self):
        """Refresh license information"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
        }
