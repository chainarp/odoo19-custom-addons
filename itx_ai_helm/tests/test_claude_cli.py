# itx_ai_helm/tests/test_claude_cli.py

"""
Test script for Claude CLI interface
Run this after installing the module:
python3 test_claude_cli.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.claude_cli_interface import get_claude_cli
import time


def test_claude_cli():
    print("Testing Claude CLI Interface...")

    # Get singleton instance
    cli = get_claude_cli()

    # Test 1: Start CLI
    print("\n1. Starting Claude CLI...")
    if cli.start_cli():
        print("✓ CLI started successfully")
    else:
        print("✗ Failed to start CLI")
        return

    # Test 2: Check status
    print("\n2. Checking status...")
    status = cli.get_status()
    print(f"Status: {status}")

    # Test 3: Send simple command
    print("\n3. Sending test command...")
    result = cli.send_command("Create a simple Python hello world function")
    print(f"Response status: {result['status']}")
    if result['status'] == 'success':
        print(f"Output preview: {result['output'][:200]}...")
        if result['code_blocks']:
            print(f"Found {len(result['code_blocks'])} code blocks")

    # Test 4: Generate Odoo model
    print("\n4. Testing Odoo model generation...")
    specs = {
        'name': 'test.model',
        'fields': ['name (char)', 'active (boolean)', 'date (date)'],
        'description': 'Test model for Claude CLI'
    }
    result = cli.generate_odoo_component('model', specs)
    print(f"Model generation status: {result['status']}")

    # Test 5: Stop CLI
    print("\n5. Stopping CLI...")
    cli.stop_cli()
    print("✓ CLI stopped")

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    test_claude_cli()