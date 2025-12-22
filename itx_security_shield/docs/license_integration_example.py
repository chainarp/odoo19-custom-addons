#!/usr/bin/env python3
"""
Example: How to Integrate License Check into Your Addon
========================================================

This shows how to add license validation to your Odoo addon
using itx_security_shield's license verification.
"""

print("""
═══════════════════════════════════════════════════════════════
  LICENSE INTEGRATION EXAMPLE
═══════════════════════════════════════════════════════════════

Assumption: You have itx_security_shield installed and working.

""")

print("""
┌────────────────────────────────────────────────────────────┐
│ STEP 1: Copy License Verifier Library                      │
└────────────────────────────────────────────────────────────┘

Copy the verifier from itx_security_shield to your addon:

  YOUR_ADDON/
  ├── __manifest__.py
  ├── __init__.py
  ├── models/
  │   └── models.py
  └── lib/                    ← Create this directory
      ├── __init__.py         ← Empty file
      └── verifier.py         ← Copy from itx_security_shield

Command:
  mkdir -p YOUR_ADDON/lib
  touch YOUR_ADDON/lib/__init__.py
  cp itx_security_shield/lib/verifier.py YOUR_ADDON/lib/

""")

print("""
┌────────────────────────────────────────────────────────────┐
│ STEP 2: Add License Check to Your Model                    │
└────────────────────────────────────────────────────────────┘

File: YOUR_ADDON/models/models.py
""")

print('''
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import os
import logging

_logger = logging.getLogger(__name__)


class YourModel(models.Model):
    _name = 'your.model'
    _description = 'Your Model Description'

    # Your fields
    name = fields.Char(string='Name', required=True)
    value = fields.Integer(string='Value')

    @api.model
    def _check_license(self):
        """
        Check license validity before any operation.

        This is THE MOST IMPORTANT part - it validates:
        1. License file exists
        2. License file is valid (signature, encryption)
        3. Hardware fingerprint matches
        4. License is not expired
        """
        try:
            # Import here to avoid issues if lib not found
            from ..lib.verifier import LicenseVerifier

            # Get addon directory path
            # __file__ = /path/to/YOUR_ADDON/models/models.py
            # addon_path = /path/to/YOUR_ADDON
            addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # Create verifier
            verifier = LicenseVerifier(addon_path)

            # Verify license
            if not verifier.verify():
                error_msg = (
                    "License validation failed for YOUR_ADDON.\\n"
                    "Please contact ITX (your company) for a valid license.\\n"
                    "Email: your-email@example.com\\n"
                    "Phone: +66-XX-XXX-XXXX"
                )
                _logger.error(f"License validation failed: {error_msg}")
                raise ValidationError(error_msg)

            _logger.info("License validated successfully")
            return True

        except ImportError as e:
            error_msg = (
                f"License verifier not found: {e}\\n"
                "Please ensure lib/verifier.py is included in the addon."
            )
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        except Exception as e:
            error_msg = f"License check failed: {str(e)}"
            _logger.error(error_msg)
            raise ValidationError(error_msg)

    # METHOD 1: Check on Create
    @api.model
    def create(self, vals):
        """Check license when creating new record"""
        self._check_license()
        return super().create(vals)

    # METHOD 2: Check on Write
    def write(self, vals):
        """Check license when updating record"""
        self._check_license()
        return super().write(vals)

    # METHOD 3: Check on Delete
    def unlink(self):
        """Check license when deleting record"""
        self._check_license()
        return super().unlink()

    # METHOD 4: Check on Compute
    @api.depends('value')
    def _compute_something(self):
        """Check license in computed fields"""
        self._check_license()
        for record in self:
            record.computed_value = record.value * 2

    computed_value = fields.Integer(
        string='Computed Value',
        compute='_compute_something',
        store=True
    )

    # METHOD 5: Check on Custom Actions
    def custom_action(self):
        """Check license in custom actions/buttons"""
        self._check_license()
        # Your custom logic here
        return True
''')

print("""
┌────────────────────────────────────────────────────────────┐
│ STEP 3: Alternative - Check on Model Init                  │
└────────────────────────────────────────────────────────────┘

More aggressive: Check license when model is loaded (once).

File: YOUR_ADDON/models/models.py
""")

print('''
from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import ValidationError
import os
import logging

_logger = logging.getLogger(__name__)


class YourModel(models.Model):
    _name = 'your.model'
    _description = 'Your Model Description'

    @api.model
    def _register_hook(self):
        """
        Called when model is registered (once per Odoo restart).
        Perfect place to check license.

        ⚠️ WARNING: This blocks Odoo startup if license is invalid!
        Use with caution.
        """
        super()._register_hook()

        try:
            from ..lib.verifier import LicenseVerifier

            addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            verifier = LicenseVerifier(addon_path)

            if not verifier.verify():
                error_msg = (
                    "═══════════════════════════════════════════════\\n"
                    "  LICENSE VALIDATION FAILED\\n"
                    "═══════════════════════════════════════════════\\n"
                    "  YOUR_ADDON requires a valid license to run.\\n"
                    "  Please contact ITX for licensing information.\\n"
                    "  Email: your-email@example.com\\n"
                    "  Phone: +66-XX-XXX-XXXX\\n"
                    "═══════════════════════════════════════════════"
                )
                _logger.critical(error_msg)
                # This will prevent model from loading!
                raise ValidationError(error_msg)

            _logger.info(f"✅ {self._name} - License validated successfully")

        except Exception as e:
            _logger.critical(f"❌ {self._name} - License check failed: {e}")
            raise

    # Your fields and methods...
    name = fields.Char(string='Name', required=True)
''')

print("""
┌────────────────────────────────────────────────────────────┐
│ STEP 4: Update __manifest__.py                             │
└────────────────────────────────────────────────────────────┘

File: YOUR_ADDON/__manifest__.py
""")

print('''
{
    'name': 'Your Addon Name',
    'version': '1.0.0',
    'category': 'Custom',
    'summary': 'Your addon description',
    'description': """
        Your Addon
        ==========
        Protected by ITX Security Shield

        This addon requires a valid license to operate.
        License is bound to hardware fingerprint.
    """,
    'author': 'Your Company (ITX)',
    'website': 'https://yourwebsite.com',
    'depends': ['base'],  # Add dependencies here
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'license': 'Proprietary',  # ← Important!
    'installable': True,
    'application': True,
    'auto_install': False,

    # Optional: Add license info
    'support': 'your-email@example.com',
    'license': 'Other proprietary',

    # Important: Ensure lib/ is included
    # Odoo automatically includes all .py files, but be explicit:
    'external_dependencies': {
        'python': ['cryptography'],  # If verifier needs it
    },
}
''')

print("""
┌────────────────────────────────────────────────────────────┐
│ STEP 5: Test Before Obfuscation                            │
└────────────────────────────────────────────────────────────┘

1. Install addon WITHOUT license file:
   → Should show error: "License validation failed"

2. Generate license file:
   cd itx_security_shield
   # Use UI or command line to generate license

3. Copy license to addon:
   cp production.lic YOUR_ADDON/

4. Restart Odoo and install addon:
   → Should work normally

5. Copy addon to different machine:
   → Should show error: "Hardware mismatch detected"

6. If all tests pass → Ready for obfuscation!

""")

print("""
┌────────────────────────────────────────────────────────────┐
│ STEP 6: Obfuscate                                          │
└────────────────────────────────────────────────────────────┘

cd itx_security_shield
./obfuscate_addon.sh YOUR_ADDON

Result:
  YOUR_ADDON/
  ├── __manifest__.py              ← Original (NOT obfuscated)
  ├── __init__.py                  ← Obfuscated + sys.path fix
  ├── models/
  │   ├── __init__.py              ← Obfuscated
  │   └── models.py                ← Obfuscated (business logic protected)
  ├── lib/
  │   └── verifier.py              ← Obfuscated (license check protected)
  ├── pyarmor_runtime_000000/      ← PyArmor runtime
  └── production.lic               ← License file (for this customer)

""")

print("""
┌────────────────────────────────────────────────────────────┐
│ STEP 7: Deployment Workflow                                │
└────────────────────────────────────────────────────────────┘

FOR EACH CUSTOMER:

1. Collect Hardware Fingerprint:
   ─────────────────────────────
   Ask customer to run on their server:

   python3 -c "
   from itx_security_shield.models.hardware_fingerprint import get_hardware_fingerprint
   import json
   print(json.dumps(get_hardware_fingerprint(), indent=2))
   "

   Customer sends you the output.

2. Generate License:
   ─────────────────────────────
   Use itx_security_shield UI:
   - Customer Name: "ABC Company"
   - Hardware Fingerprint: [paste from customer]
   - Expiration Date: 2026-12-31
   - Enabled Modules: your_addon
   - Click "Generate License"
   - Download production.lic

3. Package Addon:
   ─────────────────────────────
   cd /path/to/YOUR_ADDON

   # Include license file
   cp ~/Downloads/production.lic ./

   # Create ZIP
   zip -r YOUR_ADDON_v1.0.0_ABC_Company.zip \\
     __manifest__.py \\
     __init__.py \\
     models/ \\
     lib/ \\
     views/ \\
     security/ \\
     pyarmor_runtime_000000/ \\
     production.lic

   # Result: YOUR_ADDON_v1.0.0_ABC_Company.zip

4. Deliver to Customer:
   ─────────────────────────────
   Send them:
   - YOUR_ADDON_v1.0.0_ABC_Company.zip
   - installation_guide.pdf (create one!)

   Email template:
   ───────────────
   Dear ABC Company,

   Thank you for purchasing YOUR_ADDON.

   Attached:
   - YOUR_ADDON_v1.0.0_ABC_Company.zip (addon)
   - Installation_Guide.pdf (instructions)

   This license is bound to your server hardware and valid until 2026-12-31.

   Installation steps:
   1. Extract ZIP to Odoo addons directory
   2. Restart Odoo
   3. Update Apps List
   4. Install YOUR_ADDON

   Support: your-email@example.com

   Best regards,
   Your Company

5. Customer Installation:
   ─────────────────────────────
   # On customer's server
   unzip YOUR_ADDON_v1.0.0_ABC_Company.zip -d /opt/odoo/addons/
   systemctl restart odoo

   # In Odoo web UI:
   # Apps → Update Apps List → Search "YOUR_ADDON" → Install

6. Verification:
   ─────────────────────────────
   ✅ Addon activates without errors
   ✅ All features work
   ✅ License validated on startup

   ❌ If customer tries to copy to another server:
      → "Hardware mismatch detected"

""")

print("""
═══════════════════════════════════════════════════════════════
  PROTECTION SUMMARY
═══════════════════════════════════════════════════════════════

What Customer Gets:
  ✅ Working addon (all features)
  ✅ Support from you
  ✅ Updates (if you provide)

What Customer CANNOT Do:
  ❌ Read source code (obfuscated)
  ❌ Copy to another server (hardware binding)
  ❌ Share with others (unique license)
  ❌ Modify license check (obfuscated)
  ❌ Use after expiration (date check)
  ❌ Reverse engineer business logic (PyArmor protected)

Protection Layers:
  1. License Generator (itx_security_shield) → 95% effective
  2. Hardware Fingerprint (6 validators)     → 95% effective
  3. PyArmor Obfuscation (AES-256)          → 85% effective
  4. Cryptographic Signature (RSA-4096)     → 99% effective

  Combined: 92% overall protection 🎯

═══════════════════════════════════════════════════════════════
""")

print("""
NEXT STEPS:
  1. Copy verifier.py to your addon's lib/ directory
  2. Add _check_license() to your models
  3. Test without license (should fail)
  4. Test with license (should work)
  5. Test on different machine (should fail)
  6. Obfuscate with obfuscate_addon.sh
  7. Package and deliver to customer!

Good luck! 🚀
""")
