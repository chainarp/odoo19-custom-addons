# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Import from itx_security_shield (will fail if not present)
from odoo.addons.itx_security_shield.lib.verifier import get_hardware_info, get_fingerprint

import os
import logging

_logger = logging.getLogger(__name__)


class ItxHelloWorld(models.Model):
    _name = 'itx.helloworld'
    _description = 'ITX Hello World Test Model'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    value = fields.Integer(string='Value', default=0)
    value2 = fields.Float(
        string='Value Percentage',
        compute="_compute_value_pc",
        store=True
    )
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)

    # SQL Constraint: Value must be non-negative
    _value_non_negative = models.Constraint(
        'CHECK(value >= 0)',
        'Value must be non-negative (>= 0)!',
    )

    # New field: Show current hardware fingerprint (requires itx_security_shield)
    hardware_info = fields.Text(
        string='Hardware Info',
        compute='_compute_hardware_info',
        store=False,
        help='Hardware fingerprint from ITX Security Shield'
    )

    @api.depends('value')
    def _compute_value_pc(self):
        """Compute value percentage"""
        for record in self:
            record.value2 = float(record.value) / 100 if record.value else 0.0

    @api.constrains('name')
    def _check_name_length(self):
        """Python Constraint: Name must be at least 3 characters"""
        for record in self:
            if record.name and len(record.name) < 3:
                raise ValidationError('Name must be at least 3 characters long!')

    def _compute_hardware_info(self):
        """Show hardware fingerprint (requires itx_security_shield)"""
        # This REQUIRES itx_security_shield to work
        hw_fp = get_hardware_info()

        for record in self:
            record.hardware_info = (
                f"CPU: {hw_fp.get('cpu_model', 'Unknown')}\n"
                f"Cores: {hw_fp.get('cpu_cores', 'Unknown')}\n"
                f"Machine ID: {hw_fp.get('machine_id', 'Unknown')[:16]}...\n"
                f"MAC Address: {hw_fp.get('mac_address', 'Unknown')}"
            )

    @api.model
    def create(self, vals):
        """Create record"""
        return super().create(vals)

    def write(self, vals):
        """Update record"""
        return super().write(vals)

    def unlink(self):
        """Delete record"""
        return super().unlink()

    @api.model
    def _register_hook(self):
        """Verify security shield on model registration"""
        super()._register_hook()

        try:
            # Test that itx_security_shield is working
            hw_fp = get_hardware_info()
            _logger.info(f"✅ {self._name} loaded with itx_security_shield protection")
            _logger.info(f"   Hardware: {hw_fp.get('cpu_model', 'Unknown')}")
        except Exception as e:
            _logger.critical(f"❌ {self._name} failed to verify itx_security_shield: {e}")
            raise
