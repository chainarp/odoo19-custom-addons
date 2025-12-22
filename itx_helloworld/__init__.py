# -*- coding: utf-8 -*-
from . import models
from . import controllers

# Import directly from itx_security_shield (will fail if not installed)
from odoo.addons.itx_security_shield.lib.verifier import get_hardware_info, get_fingerprint

def _verify_security_shield():
    """Verify itx_security_shield is properly installed and functioning"""
    import sys
    import logging
    _logger = logging.getLogger(__name__)

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
        hw_fp = get_hardware_info()
        if not hw_fp or 'cpu_model' not in hw_fp:
            raise ValueError("Hardware fingerprint function not working")
    except Exception as e:
        raise RuntimeError(
            f"itx_security_shield is installed but not functioning correctly: {e}"
        )

    # Check 3: License crypto module available
    try:
        from odoo.addons.itx_security_shield.tools import license_crypto
        # Just check that the module can be imported
        _logger.info("✅ itx_security_shield crypto module available")
    except ImportError:
        raise RuntimeError("itx_security_shield crypto module not found")

    return True

# Run verification on module load
_verify_security_shield()
