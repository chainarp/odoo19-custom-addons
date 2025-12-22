# XML Validation Strategy for ITX Moduler

**Date:** 2025-12-16
**Status:** Implementation Plan
**Version:** 1.0

---

## 🎯 The Problem We Just Found

**Issue:** AI generated XML with **deprecated `attrs` syntax**
```xml
<!-- ❌ WRONG (Odoo 16-) -->
<button attrs="{'invisible': [('field', '=', 0)]}"/>

<!-- ✅ CORRECT (Odoo 17+) -->
<button invisible="field == 0"/>
```

**Result:** Module upgrade failed with `ParseError`

---

## 💡 Solution: Use Odoo's Built-in XML Validation

### What Odoo Provides

**Odoo has RelaxNG (RNG) Schema files for validation!**

Location: `/odoo/addons/base/rng/`

```
base/rng/
├── common.rng          # Common rules (invisible, readonly, etc.)
├── list_view.rng       # List/Tree view schema
├── form_view.rng       # Form view schema (if exists)
├── kanban_view.rng     # Kanban view schema
├── calendar_view.rng   # Calendar view schema
├── graph_view.rng      # Graph view schema
├── pivot_view.rng      # Pivot view schema
├── search_view.rng     # Search view schema
└── activity_view.rng   # Activity view schema
```

**What is RelaxNG?**
- XML schema language (alternative to XSD)
- More flexible and readable than XSD
- Validates XML structure, attributes, and content

---

## 🏗️ How Odoo Uses It

### In `odoo/tools/view_validation.py`:

```python
def _relaxng_validator(view_type):
    """ Return a validator for the given view type. """
    if view_type not in _relaxng_cache:
        with tools.file_open(os.path.join('base', 'rng', '%s_view.rng' % view_type)) as frng:
            try:
                relaxng_doc = etree.parse(frng)
                _relaxng_cache[view_type] = etree.RelaxNG(relaxng_doc)
            except Exception:
                _logger.exception('Failed to load RelaxNG XML schema for views validation')
    return _relaxng_cache.get(view_type)
```

**Odoo automatically validates views during:**
- Module installation
- Module upgrade
- View creation/update

---

## 🔧 Implementation for ITX Moduler

### Phase 1: Add Pre-Export Validation (NOW)

**Before generating ZIP, validate all XMLs:**

```python
# models/itx_moduler_module.py

from lxml import etree
from odoo import tools
import os

class ItxModulerModule(models.Model):
    _name = 'itx.moduler.module'

    def _validate_view_xml(self, view_type, xml_string):
        """
        Validate view XML against Odoo's RelaxNG schema

        :param view_type: 'list', 'form', 'kanban', etc.
        :param xml_string: XML string to validate
        :return: (is_valid, error_message)
        """
        try:
            # Load RelaxNG schema
            rng_path = os.path.join('base', 'rng', f'{view_type}_view.rng')
            with tools.file_open(rng_path) as frng:
                relaxng_doc = etree.parse(frng)
                relaxng = etree.RelaxNG(relaxng_doc)

            # Parse XML to validate
            xml_doc = etree.fromstring(xml_string)

            # Validate
            if relaxng.validate(xml_doc):
                return (True, None)
            else:
                error_log = relaxng.error_log
                return (False, str(error_log))

        except Exception as e:
            return (False, str(e))

    def action_validate_all_xml(self):
        """Validate all views before export"""
        self.ensure_one()

        errors = []

        for view in self.view_ids:
            is_valid, error_msg = self._validate_view_xml(
                view.type,
                view.arch_db
            )

            if not is_valid:
                errors.append({
                    'view': view.name,
                    'type': view.type,
                    'error': error_msg
                })

        if errors:
            # Show validation errors to user
            error_message = "XML Validation Failed:\n\n"
            for err in errors:
                error_message += f"View: {err['view']} ({err['type']})\n"
                error_message += f"Error: {err['error']}\n\n"

            raise UserError(error_message)

        return True

    def action_export_addon(self):
        """Export addon (with validation)"""
        self.ensure_one()

        # Validate before export
        self.action_validate_all_xml()

        # If validation passes, proceed with export
        # ... existing export logic ...
```

---

### Phase 2: Real-Time Validation in GUI (Future)

**When SA edits view XML in UI:**

```python
class ItxModulerView(models.Model):
    _name = 'itx.moduler.view'

    arch_db = fields.Text(string='View Architecture')

    @api.constrains('arch_db', 'type')
    def _check_arch_validity(self):
        """Validate XML on save"""
        for view in self:
            if view.arch_db and view.type:
                is_valid, error_msg = view.module_id._validate_view_xml(
                    view.type,
                    view.arch_db
                )

                if not is_valid:
                    raise ValidationError(
                        f"Invalid XML for {view.type} view:\n{error_msg}"
                    )
```

---

### Phase 3: AI-Generated XML Validation (Future)

**When Claude generates XML:**

```python
def ai_generate_view(self, prompt):
    """Ask Claude to generate view XML"""

    # Get XML from Claude API
    xml_code = claude_api.generate_view(prompt)

    # Validate BEFORE saving
    is_valid, error_msg = self._validate_view_xml('form', xml_code)

    if not is_valid:
        # Ask Claude to fix
        fixed_xml = claude_api.fix_xml(xml_code, error_msg)

        # Validate again
        is_valid, error_msg = self._validate_view_xml('form', fixed_xml)

        if not is_valid:
            # Still invalid - ask human
            raise UserError(
                f"AI couldn't generate valid XML.\n"
                f"Error: {error_msg}\n"
                f"Please review manually."
            )

        xml_code = fixed_xml

    # Save validated XML
    return xml_code
```

---

## 🎯 Benefits

### 1. **Catch Errors Early**
- Before module export
- Before installation
- During development

### 2. **Version-Specific Validation**
- RNG schemas match Odoo version
- Automatically detect deprecated syntax
- Prevent compatibility issues

### 3. **AI Safety Net**
- Validate AI-generated XML
- Automatic retry with error feedback
- Human intervention only when needed

### 4. **Better Developer Experience**
- Clear error messages
- Pinpoint exact issues
- Learn correct syntax

---

## 📋 RNG Schema Examples

### Common Attributes (from `common.rng`)

```xml
<!-- Odoo 17+ uses direct attribute, not attrs -->
<rng:optional><rng:attribute name="invisible"/></rng:optional>
<rng:optional><rng:attribute name="readonly"/></rng:optional>
<rng:optional><rng:attribute name="required"/></rng:optional>
<rng:optional><rng:attribute name="column_invisible"/></rng:optional>
```

**No `attrs` attribute in RNG = Not allowed!**

### Button Attributes

```xml
<rng:define name="button">
    <rng:element name="button">
        <rng:optional><rng:attribute name="name"/></rng:optional>
        <rng:optional><rng:attribute name="type"/></rng:optional>
        <rng:optional><rng:attribute name="string"/></rng:optional>
        <rng:optional><rng:attribute name="class"/></rng:optional>
        <rng:optional><rng:attribute name="invisible"/></rng:optional>
        <!-- NO attrs attribute! -->
    </rng:element>
</rng:define>
```

---

## 🔍 How to Check RNG Files

### Read Schema for View Type

```bash
# List view
cat /odoo/addons/base/rng/list_view.rng

# Form view (inherits from common)
cat /odoo/addons/base/rng/common.rng
```

### Validate XML Manually (Python)

```python
from lxml import etree
from odoo import tools

# Load schema
with tools.file_open('base/rng/list_view.rng') as f:
    relaxng = etree.RelaxNG(etree.parse(f))

# Your XML
xml = """
<list>
    <field name="name"/>
    <field name="date" invisible="state == 'draft'"/>
</list>
"""

# Validate
doc = etree.fromstring(xml)
if relaxng.validate(doc):
    print("✅ Valid!")
else:
    print("❌ Invalid!")
    print(relaxng.error_log)
```

---

## 🚀 Implementation Priority

### ✅ NOW (Quick Win)
1. Add `_validate_view_xml()` method to `itx.moduler.module`
2. Call validation before export
3. Show clear error messages

### ⏳ Phase 2 (After Jinja2)
4. Add validation to Jinja2 template rendering
5. Validate generated XML before writing to ZIP

### ⏳ Phase 3 (AI Integration)
6. Validate AI-generated XML
7. Auto-retry with error feedback
8. Human review if still fails

### ⏳ Phase 4 (Advanced)
9. Real-time validation in GUI
10. Syntax highlighting with error markers
11. Auto-suggest fixes based on RNG

---

## 💡 Key Insights

### Why This is Better Than Manual Checks

**Manual:**
```python
# ❌ Hard to maintain
if 'attrs' in xml_string:
    raise Error("Don't use attrs!")
```

**RNG Validation:**
```python
# ✅ Odoo's official rules
if not relaxng.validate(xml_doc):
    raise Error(relaxng.error_log)
```

### Version Migration Made Easy

When upgrading Odoo 19 → 20:
1. Odoo provides updated RNG schemas
2. We validate with new schemas
3. Errors show exactly what changed
4. Fix once in templates, apply to all

---

## 📊 Example Error Messages

### Before (Generic)
```
Error: Invalid XML
```

### After (With RNG Validation)
```
XML Validation Failed:

View: sale.order.form (form)
Error: Element button has extra content: attrs

Line 42: <button name="action_confirm" attrs="{'invisible': [('state', '!=', 'draft')]}"/>

Expected: Use 'invisible' attribute directly
Correct: <button name="action_confirm" invisible="state != 'draft'"/>
```

---

## 🔗 Related Files

**Odoo Core:**
- `/odoo/addons/base/rng/*.rng` - Schema definitions
- `/odoo/tools/view_validation.py` - Validation logic
- `/odoo/tools/xml_utils.py` - XML utilities

**ITX Moduler:**
- `models/itx_moduler_module.py` - Add validation methods
- `models/itx_moduler_view.py` - Add constraints
- `controllers/main.py` - Validate before export

---

## Next Steps

1. ✅ **Understand RNG schemas** (done - this document)
2. 🔄 **Implement validation method**
3. 🔄 **Add to export workflow**
4. ⏳ Test with various view types
5. ⏳ Document common validation errors
6. ⏳ Create error message guide

---

**Document Version:** 1.0
**Created:** 2025-12-16
**Author:** Claude Sonnet 4.5 (with Chainarp's insight)
**Status:** 📋 Ready for Implementation

---

## Summary

**คำถามของคุณ Chainarp:**
> "xml มันจะมี xsd ที่ใช้ validate xml ด้วยใช่หรือไม่ odoo มี xsd ตัวนี้ให้ใช้มั๊ยครับ"

**คำตอบ:**
✅ **ใช่ครับ!** Odoo ใช้ **RelaxNG (.rng)** แทน XSD (.xsd)
✅ มี schema สำหรับทุก view type
✅ ใช้ได้ทันทีผ่าน `lxml.etree.RelaxNG`
✅ เป็น official validation ของ Odoo

**ประโยชน์:**
- ป้องกัน syntax errors
- Catch deprecated attributes
- Version compatibility
- AI safety net

**Next:** Implement validation ใน ITX Moduler! 🚀
