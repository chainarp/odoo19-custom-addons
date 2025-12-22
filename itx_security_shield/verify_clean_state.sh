#!/bin/bash
# Verify itx_helloworld is in clean state

ADDON_PATH="/home/chainarp/PycharmProjects/odoo19/custom_addons/itx_helloworld"

echo "════════════════════════════════════════════════════════"
echo "  VERIFY: itx_helloworld Clean State"
echo "════════════════════════════════════════════════════════"
echo ""

# Check 1: Not obfuscated
echo "Check 1: Obfuscation Status"
echo "─────────────────────────────────────"
if [ -d "$ADDON_PATH/pyarmor_runtime_000000" ]; then
    echo "❌ FAIL: Addon is OBFUSCATED (not clean)"
    echo "   Found: pyarmor_runtime_000000/"
    echo ""
    echo "Action needed: Restore from backup or git"
    exit 1
else
    echo "✅ PASS: Not obfuscated (clean)"
fi
echo ""

# Check 2: No hard dependency yet
echo "Check 2: Dependency Status"
echo "─────────────────────────────────────"
if grep -q "itx_security_shield" "$ADDON_PATH/__manifest__.py"; then
    echo "⚠️  WARNING: itx_security_shield already in depends"
    echo "   (May be intentional, or from previous test)"
else
    echo "✅ PASS: No itx_security_shield dependency (clean)"
fi
echo ""

# Check 3: No imports from itx_security_shield
echo "Check 3: Import Status"
echo "─────────────────────────────────────"
if grep -q "itx_security_shield" "$ADDON_PATH/__init__.py"; then
    echo "⚠️  WARNING: Imports from itx_security_shield found"
    echo "   (Not clean)"
else
    echo "✅ PASS: No imports from itx_security_shield (clean)"
fi
echo ""

# Check 4: Source code is readable
echo "Check 4: Source Code Readability"
echo "─────────────────────────────────────"
if head -5 "$ADDON_PATH/__init__.py" | grep -q "pyarmor"; then
    echo "❌ FAIL: __init__.py is obfuscated (not clean)"
    exit 1
else
    echo "✅ PASS: Source code is readable (clean)"
fi
echo ""

# Check 5: File sizes (clean should be small)
echo "Check 5: File Sizes"
echo "─────────────────────────────────────"
INIT_SIZE=$(stat -f%z "$ADDON_PATH/__init__.py" 2>/dev/null || stat -c%s "$ADDON_PATH/__init__.py" 2>/dev/null)
MODEL_SIZE=$(stat -f%z "$ADDON_PATH/models/models.py" 2>/dev/null || stat -c%s "$ADDON_PATH/models/models.py" 2>/dev/null)

echo "  __init__.py: $INIT_SIZE bytes"
echo "  models.py: $MODEL_SIZE bytes"

if [ "$INIT_SIZE" -lt 500 ]; then
    echo "  ✅ __init__.py: Small (clean)"
else
    echo "  ⚠️  __init__.py: Large (may be obfuscated)"
fi

if [ "$MODEL_SIZE" -lt 2000 ]; then
    echo "  ✅ models.py: Small (clean)"
else
    echo "  ⚠️  models.py: Large (may be obfuscated)"
fi
echo ""

echo "════════════════════════════════════════════════════════"
echo "  RESULT"
echo "════════════════════════════════════════════════════════"
echo ""

if [ ! -d "$ADDON_PATH/pyarmor_runtime_000000" ] && [ "$INIT_SIZE" -lt 500 ]; then
    echo "✅ CLEAN STATE CONFIRMED"
    echo ""
    echo "Ready for hard dependency testing!"
    echo ""
    echo "Next steps:"
    echo "  1. ./implement_hard_dependency.sh"
    echo "  2. ./obfuscate_addon.sh itx_helloworld"
    echo "  3. ./test_hard_dependency.sh"
    echo ""
else
    echo "⚠️  NOT CLEAN"
    echo ""
    echo "Please restore from:"
    echo "  - Backup: cp -r itx_helloworld.backup_original itx_helloworld"
    echo "  - Git: git checkout itx_helloworld/"
    echo "  - ZIP: unzip itx_helloworld_clean.zip"
    echo ""
fi
