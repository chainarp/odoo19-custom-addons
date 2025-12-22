#!/bin/bash
# Script: Make itx_helloworld require itx_security_shield (Hard Dependency)

set -e

ADDON_PATH="/home/chainarp/PycharmProjects/odoo19/custom_addons/itx_helloworld"

echo "════════════════════════════════════════════════════════"
echo "  Adding Hard Dependency: itx_security_shield"
echo "════════════════════════════════════════════════════════"
echo ""

# Backup first
echo "📦 Step 1: Creating backup..."
cp -r "$ADDON_PATH" "$ADDON_PATH.backup_before_dependency"
echo "   ✅ Backup created: $ADDON_PATH.backup_before_dependency"
echo ""

# Step 2: Update __manifest__.py
echo "📝 Step 2: Updating __manifest__.py..."

# Check if itx_security_shield already in depends
if grep -q "itx_security_shield" "$ADDON_PATH/__manifest__.py"; then
    echo "   ⚠️  itx_security_shield already in depends"
else
    # Add to depends
    sed -i "s/'depends': \[/'depends': ['itx_security_shield', /" "$ADDON_PATH/__manifest__.py"
    echo "   ✅ Added itx_security_shield to depends"
fi
echo ""

# Step 3: Update __init__.py
echo "📝 Step 3: Adding runtime checks to __init__.py..."

cat > "$ADDON_PATH/__init__.py" << 'EOF'
# -*- coding: utf-8 -*-
from . import models

# Import directly from itx_security_shield (will fail if not installed)
from odoo.addons.itx_security_shield.models.hardware_fingerprint import get_hardware_fingerprint
from odoo.addons.itx_security_shield.lib.verifier import LicenseVerifier
from odoo.addons.itx_security_shield.tools.license_crypto import verify_signature

def _verify_security_shield():
    """Verify itx_security_shield is properly installed and functioning"""
    import sys

    # Check 1: Module exists in Odoo addons
    if 'odoo.addons.itx_security_shield' not in sys.modules:
        try:
            import odoo.addons.itx_security_shield
        except ImportError:
            raise ImportError(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  MISSING DEPENDENCY\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "  ITX Hello World requires:\n"
                "    • itx_security_shield (not found)\n"
                "\n"
                "  Please install itx_security_shield first.\n"
                "  Contact: your-email@example.com\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )

    # Check 2: Core functions are available
    try:
        hw_fp = get_hardware_fingerprint()
        if not hw_fp or 'cpu_model' not in hw_fp:
            raise ValueError("Hardware fingerprint function not working")
    except Exception as e:
        raise RuntimeError(
            f"itx_security_shield is installed but not functioning correctly: {e}"
        )

    # Check 3: License crypto functions available
    from odoo.addons.itx_security_shield.tools import license_crypto
    if not hasattr(license_crypto, 'verify_signature'):
        raise RuntimeError("itx_security_shield crypto module is incomplete")

    return True

# Run verification on module load
_verify_security_shield()
EOF

echo "   ✅ Updated __init__.py with runtime checks"
echo ""

# Step 4: Update models.py
echo "📝 Step 4: Adding deep integration to models.py..."

cat > "$ADDON_PATH/models/models.py" << 'EOF'
# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Import from itx_security_shield (will fail if not present)
from odoo.addons.itx_security_shield.models.hardware_fingerprint import get_hardware_fingerprint
from odoo.addons.itx_security_shield.lib.verifier import LicenseVerifier

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

    # New field: Show current hardware fingerprint (requires itx_security_shield)
    hardware_info = fields.Text(
        string='Hardware Info',
        compute='_compute_hardware_info',
        store=False,
        help='Hardware fingerprint from ITX Security Shield'
    )

    @api.depends('value')
    def _compute_value_pc(self):
        """Compute value percentage - WITH license check"""
        # Check license first (requires itx_security_shield)
        self._check_license()

        for record in self:
            record.value2 = float(record.value) / 100 if record.value else 0.0

    def _compute_hardware_info(self):
        """Show hardware fingerprint (requires itx_security_shield)"""
        # This REQUIRES itx_security_shield to work
        hw_fp = get_hardware_fingerprint()

        for record in self:
            record.hardware_info = (
                f"CPU: {hw_fp.get('cpu_model', 'Unknown')}\n"
                f"Cores: {hw_fp.get('cpu_cores', 'Unknown')}\n"
                f"Machine ID: {hw_fp.get('machine_id', 'Unknown')[:16]}...\n"
                f"MAC Address: {hw_fp.get('mac_address', 'Unknown')}"
            )

    @api.model
    def _check_license(self):
        """Check license using itx_security_shield"""
        try:
            addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # This REQUIRES itx_security_shield to work
            verifier = LicenseVerifier(addon_path)

            if not verifier.verify():
                raise ValidationError(
                    "License validation failed.\n"
                    "Please contact ITX for a valid license.\n"
                    "Email: your-email@example.com"
                )

            _logger.info("✅ License validated successfully")

        except Exception as e:
            _logger.error(f"❌ License check failed: {e}")
            raise

    @api.model
    def create(self, vals):
        """Check license before creating"""
        self._check_license()
        return super().create(vals)

    def write(self, vals):
        """Check license before updating"""
        self._check_license()
        return super().write(vals)

    def unlink(self):
        """Check license before deleting"""
        self._check_license()
        return super().unlink()

    @api.model
    def _register_hook(self):
        """Verify security shield on model registration"""
        super()._register_hook()

        try:
            # Test that itx_security_shield is working
            hw_fp = get_hardware_fingerprint()
            _logger.info(f"✅ {self._name} loaded with itx_security_shield protection")
            _logger.info(f"   Hardware: {hw_fp.get('cpu_model', 'Unknown')}")
        except Exception as e:
            _logger.critical(f"❌ {self._name} failed to verify itx_security_shield: {e}")
            raise
EOF

echo "   ✅ Updated models.py with deep integration"
echo ""

# Step 5: Update views to show hardware info
echo "📝 Step 5: Adding hardware info to form view..."

# Backup original view
cp "$ADDON_PATH/views/views.xml" "$ADDON_PATH/views/views.xml.backup"

# Add hardware_info field to form view (after description)
sed -i 's|<field name="description"/>|<field name="description"/>\n                        <field name="hardware_info" readonly="1"/>|' "$ADDON_PATH/views/views.xml"

echo "   ✅ Added hardware_info field to form view"
echo ""

echo "════════════════════════════════════════════════════════"
echo "  ✅ DONE! Hard dependency implemented"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Changes made:"
echo "  1. ✅ Added itx_security_shield to depends in __manifest__.py"
echo "  2. ✅ Added runtime checks in __init__.py"
echo "  3. ✅ Added deep integration in models.py"
echo "  4. ✅ Added hardware_info field to form view"
echo ""
echo "Next steps:"
echo "  1. Test without itx_security_shield (should fail)"
echo "  2. Install itx_security_shield (should work)"
echo "  3. Obfuscate: ./obfuscate_addon.sh itx_helloworld"
echo ""
echo "Backup location: $ADDON_PATH.backup_before_dependency"
echo ""
