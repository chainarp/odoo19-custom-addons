# itx_ai_helm/tests/test_claude_cli_simple.py

# !/usr/bin/env python3
"""
Simple test for Claude CLI interface
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.claude_cli_interface import get_claude_cli
import json


def test_claude_cli():
    print("=" * 60)
    print("Testing Claude CLI Interface")
    print("=" * 60)

    # Get instance
    cli = get_claude_cli()

    # Test 1: Check status
    print("\n1. Checking Claude CLI status...")
    status = cli.get_status()
    print(f"   CLI Available: {status['cli_available']}")
    if status['cli_path']:
        print(f"   CLI Path: {status['cli_path']}")
    print(f"   Workspace: {status['workspace_base']}")

    if not status['cli_available']:
        print("\n❌ Claude CLI not found. Please install it first.")
        print("   Visit: https://docs.claude.com/claude-code")
        return

    # Test 2: Simple command
    print("\n2. Testing simple Python generation...")
    result = cli.execute_command(
        "Create a simple Python function that calculates factorial of a number"
    )

    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        print(f"   Output length: {len(result['output'])} chars")
        if result['code_blocks']:
            print(f"   Code blocks found: {len(result['code_blocks'])}")
            for i, block in enumerate(result['code_blocks'], 1):
                print(f"   - Block {i}: {block['language']}")
    else:
        print(f"   Error: {result.get('error', result.get('errors'))}")

    # Test 3: Generate Odoo model
    print("\n3. Testing Odoo model generation...")
    specs = {
        'name': 'test.product',
        'fields': ['name', 'price', 'quantity'],
        'description': 'Simple product model for testing'
    }

    result = cli.generate_odoo_component('model', specs)
    print(f"   Status: {result['status']}")
    if result['status'] == 'success':
        if result['code_blocks']:
            print(f"   Generated {len(result['code_blocks'])} code blocks")
        if result['generated_files']:
            print(f"   Files created: {', '.join(result['generated_files'])}")

    print("\n✅ Testing completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_claude_cli()