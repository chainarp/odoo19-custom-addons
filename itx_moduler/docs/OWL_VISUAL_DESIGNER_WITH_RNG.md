# Owl 2.x Visual Designer + RNG Schema Integration

**Date:** 2025-12-16
**Status:** Future Planning (Phase 4)
**Version:** 1.0

---

## 🎯 Chainarp's Insight

> "xsd จะช่วยเราตอนเราใช้ owl2.x สร้าง view อย่างมาก พี่คลอดว่ามั๊ย"

**คำตอบ: ถูกต้อง 100%!** RNG Schema จะทำให้ Visual Designer **powerful มหาศาล!**

---

## 💡 Why RNG Schema is Perfect for Visual Designer

### Traditional Visual Designers (Without Schema)

```
Problem 1: ไม่รู้ว่า attributes ไหนใช้ได้บ้าง
→ แสดง property panel แบบ generic
→ User อาจใส่ attribute ที่ไม่ valid

Problem 2: ไม่รู้ว่า element ไหนซ้อนกันได้
→ User สามารถ drag-drop แบบผิดๆ ได้
→ ต้อง validate ทีหลัง (error หลัง save)

Problem 3: ไม่มี auto-complete
→ User ต้องจำ syntax เอง
→ ไม่มีการ suggest
```

### Visual Designer + RNG Schema (Smart!)

```
✅ Solution 1: รู้ attributes ทุกตัวที่ valid
→ Property panel แสดงแค่ที่ใช้ได้
→ Auto-complete attributes
→ ป้องกัน typo

✅ Solution 2: รู้ structure ที่ valid
→ Drag-drop ได้แค่ element ที่ valid
→ Real-time validation
→ Error ก่อนที่จะ save

✅ Solution 3: Smart suggestions
→ Auto-suggest based on context
→ Show examples
→ Guide user
```

---

## 🏗️ Architecture: Owl + RNG Parser

### 1. RNG Parser Service

```javascript
// static/src/services/rng_parser_service.js
import { registry } from "@web/core/registry";

export class RNGParserService {
    constructor(env) {
        this.env = env;
        this.schemas = {};
    }

    async loadSchema(viewType) {
        // Load RNG schema for view type
        const response = await fetch(`/itx_moduler/rng/${viewType}`);
        const rngXML = await response.text();

        // Parse RNG to JSON structure
        this.schemas[viewType] = this.parseRNG(rngXML);
        return this.schemas[viewType];
    }

    parseRNG(rngXML) {
        // Convert RNG XML to usable JSON
        // Example output:
        return {
            elements: {
                'button': {
                    attributes: [
                        {name: 'name', type: 'string', required: false},
                        {name: 'type', type: 'string', required: false},
                        {name: 'string', type: 'string', required: false},
                        {name: 'class', type: 'string', required: false},
                        {name: 'invisible', type: 'expression', required: false},
                        // NO 'attrs' - not in RNG!
                    ],
                    children: ['span', 'i'],  // Allowed child elements
                },
                'field': {
                    attributes: [
                        {name: 'name', type: 'string', required: true},
                        {name: 'widget', type: 'enum', values: ['char', 'text', 'many2one', ...], required: false},
                        {name: 'invisible', type: 'expression', required: false},
                        {name: 'readonly', type: 'expression', required: false},
                        {name: 'required', type: 'expression', required: false},
                    ],
                    children: [],
                },
            },
        };
    }

    getValidAttributes(elementType) {
        return this.schemas.list?.elements[elementType]?.attributes || [];
    }

    canContainChild(parentType, childType) {
        const allowedChildren = this.schemas.list?.elements[parentType]?.children;
        return allowedChildren?.includes(childType) ?? false;
    }

    validateElement(elementType, attributes) {
        const validAttrs = this.getValidAttributes(elementType);
        const errors = [];

        // Check for invalid attributes
        for (const attr in attributes) {
            if (!validAttrs.find(v => v.name === attr)) {
                errors.push(`Invalid attribute '${attr}' for element '${elementType}'`);
            }
        }

        // Check required attributes
        for (const validAttr of validAttrs) {
            if (validAttr.required && !(validAttr.name in attributes)) {
                errors.push(`Missing required attribute '${validAttr.name}'`);
            }
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }
}

registry.category("services").add("rng_parser", {
    start(env) {
        return new RNGParserService(env);
    },
});
```

---

## 🎨 Owl Components with RNG Integration

### 2. Visual View Designer Component

```javascript
// static/src/components/visual_designer/visual_designer.js
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class VisualViewDesigner extends Component {
    setup() {
        this.rngParser = useService("rng_parser");
        this.state = useState({
            viewType: 'list',
            elements: [],
            selectedElement: null,
            schema: null,
        });

        // Load RNG schema for current view type
        this.loadSchema();
    }

    async loadSchema() {
        this.state.schema = await this.rngParser.loadSchema(this.state.viewType);
    }

    onElementDragStart(ev, elementType) {
        ev.dataTransfer.setData("elementType", elementType);
    }

    onElementDrop(ev, targetElement) {
        const elementType = ev.dataTransfer.getData("elementType");

        // ✅ VALIDATE USING RNG!
        if (!this.rngParser.canContainChild(targetElement.type, elementType)) {
            this.env.services.notification.add(
                `Cannot add ${elementType} inside ${targetElement.type}`,
                { type: 'warning' }
            );
            return;
        }

        // Add element
        this.addElement(targetElement, elementType);
    }

    addElement(parent, elementType) {
        const newElement = {
            id: Date.now(),
            type: elementType,
            attributes: {},
            children: [],
        };

        parent.children.push(newElement);
        this.selectElement(newElement);
    }

    selectElement(element) {
        this.state.selectedElement = element;

        // Load valid attributes from RNG
        this.state.validAttributes = this.rngParser.getValidAttributes(element.type);
    }
}
```

---

### 3. Property Panel (Smart Auto-Complete)

```javascript
// static/src/components/property_panel/property_panel.js
import { Component } from "@odoo/owl";

export class PropertyPanel extends Component {
    setup() {
        this.rngParser = useService("rng_parser");
    }

    get validAttributes() {
        if (!this.props.selectedElement) return [];

        // ✅ GET VALID ATTRIBUTES FROM RNG!
        return this.rngParser.getValidAttributes(
            this.props.selectedElement.type
        );
    }

    onAttributeChange(attrName, value) {
        const element = this.props.selectedElement;
        element.attributes[attrName] = value;

        // ✅ REAL-TIME VALIDATION!
        const validation = this.rngParser.validateElement(
            element.type,
            element.attributes
        );

        if (!validation.valid) {
            // Show errors
            this.showValidationErrors(validation.errors);
        }
    }

    renderAttributeInput(attr) {
        // Render different input types based on RNG schema
        switch (attr.type) {
            case 'string':
                return html`<input type="text"
                    value="${this.props.selectedElement.attributes[attr.name] || ''}"
                    placeholder="${attr.name}"
                    @change="${(ev) => this.onAttributeChange(attr.name, ev.target.value)}"
                />`;

            case 'expression':
                return html`<ExpressionEditor
                    value="${this.props.selectedElement.attributes[attr.name] || ''}"
                    onChange="${(val) => this.onAttributeChange(attr.name, val)}"
                />`;

            case 'enum':
                return html`<select
                    @change="${(ev) => this.onAttributeChange(attr.name, ev.target.value)}">
                    <option value="">-- Select ${attr.name} --</option>
                    ${attr.values.map(v => html`<option value="${v}">${v}</option>`)}
                </select>`;
        }
    }
}

PropertyPanel.template = "itx_moduler.PropertyPanel";
PropertyPanel.props = {
    selectedElement: Object,
};
```

---

### 4. Expression Editor (with Syntax Validation)

```javascript
// static/src/components/expression_editor/expression_editor.js
import { Component, useState } from "@odoo/owl";

export class ExpressionEditor extends Component {
    setup() {
        this.state = useState({
            value: this.props.value || '',
            errors: [],
        });
    }

    onValueChange(newValue) {
        this.state.value = newValue;

        // ✅ VALIDATE EXPRESSION SYNTAX!
        this.validateExpression(newValue);

        // Notify parent
        this.props.onChange(newValue);
    }

    validateExpression(expr) {
        // Parse expression
        // Example: "state == 'draft' and partner_id"

        const errors = [];

        // Check Python syntax
        try {
            // Could use a Python AST parser
            // Or simple regex validation
            if (!this.isValidPythonExpression(expr)) {
                errors.push("Invalid Python expression");
            }
        } catch (e) {
            errors.push(e.message);
        }

        // Check field references
        const fieldNames = this.extractFieldNames(expr);
        for (const field of fieldNames) {
            if (!this.isValidField(field)) {
                errors.push(`Unknown field: ${field}`);
            }
        }

        this.state.errors = errors;
    }

    isValidPythonExpression(expr) {
        // Basic validation
        // Real implementation would use proper parser
        const dangerousKeywords = ['import', 'exec', 'eval', '__'];
        return !dangerousKeywords.some(kw => expr.includes(kw));
    }

    extractFieldNames(expr) {
        // Extract field names from expression
        // "state == 'draft' and partner_id" → ['state', 'partner_id']
        const matches = expr.match(/\b[a-z_][a-z0-9_]*\b/gi);
        return matches || [];
    }

    isValidField(fieldName) {
        // Check if field exists in current model
        // Would query from context
        return true; // Simplified
    }
}

ExpressionEditor.template = "itx_moduler.ExpressionEditor";
ExpressionEditor.props = {
    value: String,
    onChange: Function,
};
```

---

## 🎯 Real-World Example: User Creates Button

### Without RNG (Traditional)

```
User: Drag "Button" to form
Designer: ✅ Added

User: Opens property panel
Designer: Shows generic text inputs:
  - Name: [         ]
  - Type: [         ]
  - String: [         ]
  - ... (user doesn't know what else is valid)

User: Types "attrs={'invisible': ...}"
Designer: ✅ Saved (no validation)

User: Clicks "Save"
Designer: ✅ Saved to database

User: Tries to install module
Odoo: ❌ ERROR: "attrs not allowed since Odoo 17"
User: 😭 Frustrated, goes back to edit
```

### With RNG Schema (Smart!)

```
User: Drag "Button" to form
Designer: ✅ Added

User: Opens property panel
Designer: 📋 Shows ONLY valid attributes from RNG:
  ✅ name (string)
  ✅ type (select: object, action)
  ✅ string (string)
  ✅ class (string)
  ✅ invisible (expression editor)
  ✅ readonly (expression editor)
  ❌ attrs (NOT IN LIST - doesn't exist in RNG!)

User: Selects "invisible" attribute
Designer: 🎨 Opens Expression Editor
  - Syntax highlighting
  - Field auto-complete
  - Real-time validation

User: Types "state == 'draft'"
Designer: ✅ Valid! Shows green checkmark

User: Types "state === 'draft'" (wrong syntax)
Designer: ❌ Invalid! Shows error: "Use '==' not '==='"

User: Clicks "Save"
Designer: ✅ Validates entire view using RNG
         ✅ All valid!
         ✅ Saved

User: Installs module
Odoo: ✅ SUCCESS!
User: 😊 Happy!
```

---

## 🚀 Advanced Features Enabled by RNG

### 1. **Drag-Drop Validation**

```javascript
// Only allow valid drops
onDragOver(ev, targetElement) {
    const elementType = ev.dataTransfer.getData("elementType");

    if (this.rngParser.canContainChild(targetElement.type, elementType)) {
        ev.preventDefault(); // Allow drop
        targetElement.classList.add('drop-valid');
    } else {
        // Prevent drop
        targetElement.classList.add('drop-invalid');
    }
}
```

**User Experience:**
- Green highlight = valid drop zone
- Red highlight = invalid drop zone
- Can't drop button inside field (RNG says no!)

---

### 2. **Context-Aware Auto-Complete**

```javascript
// Smart attribute suggestions
getAttributeSuggestions(element, partialInput) {
    const validAttrs = this.rngParser.getValidAttributes(element.type);

    // Filter based on what user typed
    return validAttrs
        .filter(attr => attr.name.startsWith(partialInput))
        .map(attr => ({
            label: attr.name,
            detail: attr.type,
            required: attr.required,
            documentation: this.getAttributeDoc(attr.name),
        }));
}
```

**User Experience:**
- Type "inv" → suggests "invisible"
- Shows type (expression)
- Shows documentation
- Marks required attributes with ⭐

---

### 3. **Template Library (Pre-validated)**

```javascript
// All templates validated against RNG
const BUTTON_TEMPLATES = [
    {
        name: "Confirm Button",
        validated: true, // ✅ Checked against RNG
        xml: `<button name="action_confirm"
                      type="object"
                      string="Confirm"
                      class="btn-primary"
                      invisible="state != 'draft'"/>`
    },
    {
        name: "Cancel Button",
        validated: true,
        xml: `<button name="action_cancel"
                      type="object"
                      string="Cancel"
                      invisible="state == 'done'"/>`
    },
];
```

**User Experience:**
- Library of pre-built elements
- All guaranteed to be valid
- One-click insert
- Customize after insert

---

### 4. **Live Preview with Validation Status**

```javascript
// Real-time view rendering
renderPreview() {
    const xml = this.generateXML();

    // ✅ Validate with RNG first!
    const validation = this.rngParser.validateXML('list', xml);

    if (validation.valid) {
        // Render preview
        this.showPreview(xml);
        this.showValidationBadge('✅ Valid');
    } else {
        // Show errors in preview
        this.showValidationErrors(validation.errors);
        this.showValidationBadge('❌ Invalid');
    }
}
```

**User Experience:**
- Live preview updates as you design
- Green badge = all valid
- Red badge = has errors
- Click to see detailed errors

---

## 📊 Benefits Summary

| Feature | Without RNG | With RNG |
|---------|-------------|----------|
| **Attribute Discovery** | User must know/guess | Auto-show valid attributes |
| **Error Detection** | After save/install | Real-time, as you type |
| **Drag-Drop** | Any combination | Only valid structures |
| **Auto-Complete** | Generic/none | Context-aware, smart |
| **Learning Curve** | Steep (must read docs) | Guided (UI teaches you) |
| **Error Recovery** | Fix after failure | Prevent before save |
| **Code Quality** | Depends on user skill | Always valid |

---

## 🎯 Implementation Phases

### Phase 1: RNG Parser (Foundation)
```
1. Create RNG parser service (JavaScript)
2. Parse RNG XML to JSON schema
3. Provide query methods (getValidAttributes, etc.)
4. Add HTTP endpoint to serve RNG files
```

### Phase 2: Basic Visual Designer
```
5. Drag-drop canvas (Owl component)
6. Element palette (buttons, fields, etc.)
7. Property panel (basic)
8. Real-time validation
```

### Phase 3: Smart Features
```
9. Auto-complete for attributes
10. Expression editor with validation
11. Context-aware suggestions
12. Drop zone validation
```

### Phase 4: Advanced UX
```
13. Template library
14. Live preview
15. Undo/redo
16. Copy/paste with validation
```

---

## 💡 Why This is Revolutionary

### Traditional Visual Designers:
```
User → Design → Save → Test → ERROR → Fix → Repeat
```
**Problem:** Trial and error, frustrating, time-consuming

### RNG-Powered Visual Designer:
```
User → Design (with real-time guidance) → Save → ✅ Works!
```
**Benefit:** Guided creation, immediate feedback, always valid

---

## 🔮 Future: AI + RNG Schema

```javascript
// AI-assisted design with RNG validation
async generateViewWithAI(prompt) {
    // Ask Claude to generate view
    const aiXML = await claudeAPI.generateView(prompt);

    // ✅ Validate with RNG
    const validation = this.rngParser.validateXML('form', aiXML);

    if (!validation.valid) {
        // Ask Claude to fix based on RNG errors
        const fixedXML = await claudeAPI.fixXML(aiXML, validation.errors);

        // Validate again
        const revalidation = this.rngParser.validateXML('form', fixedXML);

        if (revalidation.valid) {
            return fixedXML;
        }
    }

    return aiXML;
}
```

**Result:** AI generates code → RNG validates → Auto-fix → Perfect code

---

## 🎯 Conclusion

**Chainarp's insight is 100% correct!**

RNG Schema will make Owl 2.x Visual Designer:
1. **Smarter** - Knows what's valid
2. **Safer** - Prevents errors before they happen
3. **Faster** - No trial-and-error
4. **Better** - Guides user to success

**This is the secret sauce for WOW effect! 🎉**

---

**Document Version:** 1.0
**Created:** 2025-12-16
**Author:** Claude Sonnet 4.5 (inspired by Chainarp)
**Status:** 🔮 Future Vision - Phase 4

---

## Related Documents

- [XML_VALIDATION_STRATEGY.md](./XML_VALIDATION_STRATEGY.md) - RNG validation basics
- [VISION_AND_WORKFLOW.md](./VISION_AND_WORKFLOW.md) - Overall architecture
- [VERSION_COMPATIBILITY_STRATEGY.md](./VERSION_COMPATIBILITY_STRATEGY.md) - Version handling
