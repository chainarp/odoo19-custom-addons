#!/bin/bash

################################################################################
# Script: obfuscate_addon.sh
# Description: Obfuscate Odoo addon with PyArmor
# Usage: ./obfuscate_addon.sh <addon_name>
# Example: ./obfuscate_addon.sh itx_helloworld
#
# Author: ITX Corporation (with Claude Code)
# Date: 2025-12-04
# Updated: Added sys.path fix for pyarmor_runtime_000000 import
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_error() { print_message "$RED" "❌ ERROR: $1"; }
print_success() { print_message "$GREEN" "✅ $1"; }
print_warning() { print_message "$YELLOW" "⚠️  $1"; }
print_info() { print_message "$BLUE" "ℹ️  $1"; }

# Check if addon name provided
if [ -z "$1" ]; then
    print_error "Addon name not provided!"
    echo "Usage: $0 <addon_name>"
    echo "Example: $0 itx_helloworld"
    exit 1
fi

ADDON_NAME=$1
ADDON_PATH="/home/chainarp/PycharmProjects/odoo19/custom_addons/${ADDON_NAME}"
BACKUP_PATH="/home/chainarp/PycharmProjects/odoo19/custom_addons/backups/${ADDON_NAME}_backup_$(date +%Y%m%d_%H%M%S)"
OBFUSCATED_PATH="/home/chainarp/PycharmProjects/odoo19/custom_addons/${ADDON_NAME}_obfuscated"
VENV_PATH="/home/chainarp/PycharmProjects/odoo19/.venv"

print_info "Starting PyArmor obfuscation for addon: ${ADDON_NAME}"
echo ""

################################################################################
# Step 1: Validate addon exists
################################################################################
print_info "Step 1: Validating addon..."

if [ ! -d "$ADDON_PATH" ]; then
    print_error "Addon directory not found: $ADDON_PATH"
    exit 1
fi

if [ ! -f "$ADDON_PATH/__manifest__.py" ]; then
    print_error "__manifest__.py not found in addon!"
    exit 1
fi

print_success "Addon found: $ADDON_PATH"
echo ""

################################################################################
# Step 2: Backup original addon
################################################################################
print_info "Step 2: Creating backup..."

mkdir -p "$(dirname "$BACKUP_PATH")"
cp -r "$ADDON_PATH" "$BACKUP_PATH"

print_success "Backup created: $BACKUP_PATH"
echo ""

################################################################################
# Step 3: Activate virtual environment
################################################################################
print_info "Step 3: Activating virtual environment..."

if [ ! -d "$VENV_PATH" ]; then
    print_error "Virtual environment not found: $VENV_PATH"
    exit 1
fi

source "$VENV_PATH/bin/activate"
print_success "Virtual environment activated"
echo ""

################################################################################
# Step 4: Check PyArmor installation
################################################################################
print_info "Step 4: Checking PyArmor..."

if ! command -v pyarmor &> /dev/null; then
    print_warning "PyArmor not found. Installing..."
    pip install pyarmor
fi

PYARMOR_VERSION=$(pyarmor --version 2>&1 | head -1)
print_success "PyArmor installed: $PYARMOR_VERSION"
echo ""

################################################################################
# Step 5: Obfuscate addon with PyArmor
################################################################################
print_info "Step 5: Obfuscating addon with PyArmor..."

cd "$(dirname "$ADDON_PATH")"

# Remove old obfuscated version if exists
if [ -d "$OBFUSCATED_PATH" ]; then
    print_warning "Removing old obfuscated version..."
    rm -rf "$OBFUSCATED_PATH"
fi

# Run PyArmor
print_info "Running: pyarmor gen --output ${ADDON_NAME}_obfuscated ${ADDON_NAME}"
pyarmor gen --output "${ADDON_NAME}_obfuscated" "${ADDON_NAME}"

print_success "PyArmor obfuscation completed"
echo ""

################################################################################
# Step 6: Restore __manifest__.py (CRITICAL!)
################################################################################
print_info "Step 6: Restoring __manifest__.py..."
print_warning "Odoo requires __manifest__.py to be non-obfuscated!"

# Copy original __manifest__.py back
cp "$ADDON_PATH/__manifest__.py" "$OBFUSCATED_PATH/${ADDON_NAME}/__manifest__.py"

# Verify it's not obfuscated
if grep -q "pyarmor" "$OBFUSCATED_PATH/${ADDON_NAME}/__manifest__.py"; then
    print_error "__manifest__.py still obfuscated! Manual intervention needed."
    exit 1
fi

print_success "__manifest__.py restored (non-obfuscated)"
echo ""

################################################################################
# Step 7: Copy non-Python files (XML, CSV, etc.)
################################################################################
print_info "Step 7: Copying non-Python files..."

# Copy demo/ if exists
if [ -d "$ADDON_PATH/demo" ]; then
    cp -r "$ADDON_PATH/demo" "$OBFUSCATED_PATH/${ADDON_NAME}/"
    print_success "Copied: demo/"
fi

# Copy security/ if exists
if [ -d "$ADDON_PATH/security" ]; then
    cp -r "$ADDON_PATH/security" "$OBFUSCATED_PATH/${ADDON_NAME}/"
    print_success "Copied: security/"
fi

# Copy views/ if exists
if [ -d "$ADDON_PATH/views" ]; then
    cp -r "$ADDON_PATH/views" "$OBFUSCATED_PATH/${ADDON_NAME}/"
    print_success "Copied: views/"
fi

# Copy data/ if exists
if [ -d "$ADDON_PATH/data" ]; then
    cp -r "$ADDON_PATH/data" "$OBFUSCATED_PATH/${ADDON_NAME}/"
    print_success "Copied: data/"
fi

# Copy static/ if exists
if [ -d "$ADDON_PATH/static" ]; then
    cp -r "$ADDON_PATH/static" "$OBFUSCATED_PATH/${ADDON_NAME}/"
    print_success "Copied: static/"
fi

echo ""

################################################################################
# Step 8: Move pyarmor_runtime into addon
################################################################################
print_info "Step 8: Moving pyarmor_runtime into addon..."
print_warning "This is necessary for Odoo to import the runtime!"

if [ -d "$OBFUSCATED_PATH/pyarmor_runtime_000000" ]; then
    mv "$OBFUSCATED_PATH/pyarmor_runtime_000000" "$OBFUSCATED_PATH/${ADDON_NAME}/"
    print_success "pyarmor_runtime_000000 moved into addon"
else
    print_error "pyarmor_runtime_000000 not found!"
    exit 1
fi

echo ""

################################################################################
# Step 9: Inject sys.path fix into __init__.py (CRITICAL!)
################################################################################
print_info "Step 9: Injecting sys.path fix into __init__.py..."
print_warning "This fixes ModuleNotFoundError for pyarmor_runtime_000000!"

INIT_FILE="$OBFUSCATED_PATH/${ADDON_NAME}/__init__.py"

# Check if __init__.py exists and is obfuscated
if [ ! -f "$INIT_FILE" ]; then
    print_error "__init__.py not found!"
    exit 1
fi

if ! grep -q "pyarmor" "$INIT_FILE"; then
    print_warning "__init__.py is not obfuscated, skipping sys.path fix"
else
    # Read the obfuscated __init__.py
    OBFUSCATED_CONTENT=$(cat "$INIT_FILE")

    # Create sys.path fix header
    SYSPATH_FIX="# ========== sys.path fix for Odoo addon ==========
import sys
import os
__addon_dir__ = os.path.dirname(os.path.abspath(__file__))
if __addon_dir__ not in sys.path:
    sys.path.insert(0, __addon_dir__)
# =================================================="

    # Get the first line (PyArmor header)
    FIRST_LINE=$(head -1 "$INIT_FILE")

    # Get everything after the first line
    REST_CONTENT=$(tail -n +2 "$INIT_FILE")

    # Reconstruct with sys.path fix
    echo "$FIRST_LINE" > "$INIT_FILE"
    echo "$SYSPATH_FIX" >> "$INIT_FILE"
    echo "$REST_CONTENT" >> "$INIT_FILE"

    print_success "sys.path fix injected into __init__.py"

    # Verify the fix
    if grep -q "sys.path.insert" "$INIT_FILE"; then
        print_success "Verification passed: sys.path fix found in __init__.py"
    else
        print_error "Verification failed: sys.path fix not found!"
        exit 1
    fi
fi

echo ""

################################################################################
# Step 10: Replace original addon with obfuscated version
################################################################################
print_info "Step 10: Replacing original addon..."
print_warning "This will replace the original addon with the obfuscated version!"

read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Cancelled. Obfuscated addon saved at: $OBFUSCATED_PATH"
    exit 0
fi

# Remove original
rm -rf "$ADDON_PATH"

# Move obfuscated version
mv "$OBFUSCATED_PATH/${ADDON_NAME}" "$ADDON_PATH"

# Remove temp obfuscated directory
rm -rf "$OBFUSCATED_PATH"

print_success "Original addon replaced with obfuscated version"
echo ""

################################################################################
# Step 11: Clean up Python cache
################################################################################
print_info "Step 11: Cleaning Python cache..."

find "$ADDON_PATH" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$ADDON_PATH" -name "*.pyc" -delete 2>/dev/null || true

print_success "Python cache cleaned"
echo ""

################################################################################
# Summary
################################################################################
print_success "═══════════════════════════════════════════════════════════"
print_success "  PyArmor Obfuscation Completed Successfully!"
print_success "═══════════════════════════════════════════════════════════"
echo ""
print_info "Addon location: $ADDON_PATH"
print_info "Backup location: $BACKUP_PATH"
echo ""
print_warning "⚠️  IMPORTANT NOTES:"
echo "1. Test the addon thoroughly in Odoo before deploying!"
echo "2. Update Apps List in Odoo (Settings → Apps → Update Apps List)"
echo "3. If you encounter import errors, see troubleshooting below"
echo ""
print_info "📋 Troubleshooting:"
echo "   - ModuleNotFoundError: pyarmor_runtime_000000"
echo "     → Solution: sys.path fix is automatically injected in Step 9"
echo "     → Verify: Check __init__.py contains 'sys.path.insert'"
echo "     → Verify: pyarmor_runtime_000000/ is inside the addon directory"
echo ""
echo "   - SyntaxError in __manifest__.py"
echo "     → Check that __manifest__.py is NOT obfuscated"
echo "     → This is handled automatically in Step 6"
echo ""
echo "   - Addon not visible in Apps List"
echo "     → Restart Odoo server"
echo "     → Clear browser cache and refresh"
echo ""
print_info "✨ Key Features:"
echo "   ✅ Automatic sys.path fix (dynamic, works after rename/move)"
echo "   ✅ __manifest__.py preservation (Odoo requirement)"
echo "   ✅ Non-Python files copied (XML, CSV, static files)"
echo "   ✅ Complete backup before obfuscation"
echo ""
print_success "Done! 🎉"
