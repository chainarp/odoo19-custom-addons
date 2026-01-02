#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for ITX AI Helm - Context Memory (Spoke 1)

This tests:
1. Creating AI Project
2. Adding entries to Log Book
3. Searching Log Book
4. Context versioning

Run with: odoo shell -c odoo.conf -d database_name < test_helm_context.py
"""

# Test 1: Create AI Project
print("=" * 60)
print("TEST 1: Create AI Project")
print("=" * 60)

Project = env['itx.ai.project']
project = Project.create({
    'name': 'Test Helm Project',
    'domain_type': 'odoo_dev',
    'description': 'Testing Context Memory functionality',
})
print(f"✓ Created project: {project.name} (ID: {project.id})")

# Test 2: Get default domain
print("\n" + "=" * 60)
print("TEST 2: Get Default Domain")
print("=" * 60)

Domain = env['itx.ai.domain']
odoo_domain = Domain.search([('code', '=', 'odoo_dev')], limit=1)
if odoo_domain:
    print(f"✓ Found domain: {odoo_domain.name}")
    print(f"  Description: {odoo_domain.description}")

    # Show logbook sections
    Section = env['itx.ai.logbook.section']
    sections = Section.search([('domain_id', '=', odoo_domain.id)])
    print(f"\n  Logbook Sections ({len(sections)}):")
    for section in sections:
        print(f"    - {section.icon} {section.name}")
else:
    print("✗ Domain not found - might not be created yet")

# Test 3: Add entries to Context/Log Book
print("\n" + "=" * 60)
print("TEST 3: Add Entries to Log Book")
print("=" * 60)

Context = env['itx.ai.context']

# Get or create project-level context
project_context = Context.search([
    ('project_id', '=', project.id),
    ('context_type', '=', 'project'),
], limit=1)

if not project_context:
    project_context = Context.create({
        'domain_id': odoo_domain.id if odoo_domain else False,
        'project_id': project.id,
        'context_type': 'project',
        'context_data': {'entries': []},
    })
    print(f"✓ Created project context (ID: {project_context.id})")
else:
    print(f"✓ Found existing project context (ID: {project_context.id})")

# Add test entries
test_entries = [
    {
        'type': 'decision',
        'title': 'Use fields.Json instead of fields.Serialized',
        'content': 'Odoo 19 deprecated fields.Serialized. Must use fields.Json for all JSON storage.',
        'tags': ['odoo19', 'compatibility', 'fields'],
        'section': 'odoo_knowledge',
    },
    {
        'type': 'decision',
        'title': 'View type changed from tree to list',
        'content': 'Odoo 19 renamed <tree> to <list> in view architecture. view_mode should use "list,form" not "tree,form".',
        'tags': ['odoo19', 'views', 'compatibility'],
        'section': 'odoo_knowledge',
    },
    {
        'type': 'architecture',
        'title': 'ITX AI Helm - 10 Spokes Design',
        'content': 'Framework uses Ship\'s Wheel metaphor with 10 spokes for AI conversation control. Spoke 1 is Context Memory (Log Book).',
        'tags': ['architecture', 'design', 'helm'],
        'section': 'architecture',
    },
]

result = project_context.add_entry(test_entries[0])
print(f"✓ Added entry 1: {test_entries[0]['title']}")

result = project_context.add_entry(test_entries[1])
print(f"✓ Added entry 2: {test_entries[1]['title']}")

result = project_context.add_entry(test_entries[2])
print(f"✓ Added entry 3: {test_entries[2]['title']}")

print(f"\nTotal entries in context: {project_context.entry_count}")

# Test 4: Search Log Book
print("\n" + "=" * 60)
print("TEST 4: Search Log Book")
print("=" * 60)

# Search by tag
search_results = project_context.search_logbook(['odoo19'])
print(f"\n✓ Search for 'odoo19' tag:")
print(f"  Found {len(search_results)} entries")
for entry in search_results:
    print(f"    - {entry.get('title')}")

# Search by section
search_results = project_context.search_logbook([], section='odoo_knowledge')
print(f"\n✓ Search for 'odoo_knowledge' section:")
print(f"  Found {len(search_results)} entries")
for entry in search_results:
    print(f"    - {entry.get('title')}")

# Test 5: Context Versioning
print("\n" + "=" * 60)
print("TEST 5: Context Versioning")
print("=" * 60)

old_version = project_context.version
print(f"Current version: {old_version}")

new_context = project_context.create_new_version()
print(f"✓ Created new version: {new_context.version}")
print(f"  Old context active: {project_context.active_version}")
print(f"  New context active: {new_context.active_version}")
print(f"  Entry count in new version: {new_context.entry_count}")

# Summary
print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"✓ Project ID: {project.id}")
print(f"✓ Context ID: {project_context.id}")
print(f"✓ Total entries: {project_context.entry_count}")
print(f"✓ Latest version: {new_context.version}")
print("\nAll tests completed successfully!")

# Cleanup (optional - comment out to keep test data)
# print("\n[Cleanup: Deleting test project...]")
# project.unlink()
# print("✓ Cleanup complete")
