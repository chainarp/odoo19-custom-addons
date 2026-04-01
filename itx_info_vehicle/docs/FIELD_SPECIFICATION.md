# Field Specification - ITX Info Vehicle

## Document Version

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03 | Claude/ITX | Initial specification for Prototype A (Odoo 19) |

---

## 1. itx.info.vehicle.brand (ยี่ห้อรถยนต์)

**Technical Name:** `itx_info_vehicle_brand`
**Description:** Master data for vehicle brands/manufacturers

### Fields

| # | Field Name | Type | Size | Required | Index | Stored | Default | Description |
|---|------------|------|------|----------|-------|--------|---------|-------------|
| 1 | `code` | Char | 50 | Yes | Yes | Yes | - | รหัสยี่ห้อตามตลาด เช่น `HONDA`, `TOYOTA` |
| 2 | `name` | Char | 100 | Yes | Yes | Yes | - | ชื่อยี่ห้อ เช่น `Honda`, `Toyota` |
| 3 | `description` | Text | - | No | No | Yes | - | คำอธิบายเพิ่มเติม |
| 4 | `abbr` | Char | 10 | Yes | Yes | Yes | auto | ตัวย่อสำหรับ Internal Ref เช่น `HON` |
| 5 | `country_id` | Many2one | - | No | No | Yes | - | ประเทศผู้ผลิต → `res.country` |
| 6 | `logo` | Image | - | No | No | Yes | - | โลโก้ยี่ห้อ |
| 7 | `active` | Boolean | - | No | No | Yes | True | สถานะใช้งาน |
| 8 | `model_ids` | One2many | - | No | No | No | - | รุ่นทั้งหมด → `itx.info.vehicle.model` |
| 9 | `model_count` | Integer | - | No | No | No | computed | จำนวนรุ่น |

### Constraints

```python
_sql_constraints = [
    ('code_uniq', 'UNIQUE(code)', 'Brand code must be unique!'),
    ('abbr_uniq', 'UNIQUE(abbr)', 'Brand abbreviation must be unique!'),
]
```

### Computed Fields

```python
@api.depends('model_ids')
def _compute_model_count(self):
    for rec in self:
        rec.model_count = len(rec.model_ids)

@api.onchange('name')
def _onchange_name_set_abbr(self):
    """Auto-generate abbr from name (first 3 uppercase chars)"""
    if self.name and not self.abbr:
        self.abbr = self.name[:3].upper()
```

---

## 2. itx.info.vehicle.model (รุ่นรถยนต์)

**Technical Name:** `itx_info_vehicle_model`
**Description:** Vehicle model/series under each brand

### Fields

| # | Field Name | Type | Size | Required | Index | Stored | Default | Description |
|---|------------|------|------|----------|-------|--------|---------|-------------|
| 1 | `code` | Char | 50 | Yes | Yes | Yes | - | รหัสรุ่นตามตลาด เช่น `CIVIC`, `ACCORD` |
| 2 | `name` | Char | 100 | Yes | Yes | Yes | - | ชื่อรุ่น เช่น `Civic`, `Accord` |
| 3 | `description` | Text | - | No | No | Yes | - | คำอธิบายเพิ่มเติม |
| 4 | `abbr` | Char | 10 | Yes | Yes | Yes | auto | ตัวย่อ เช่น `CIV`, `ACD` |
| 5 | `brand_id` | Many2one | - | Yes | Yes | Yes | - | ยี่ห้อ → `itx.info.vehicle.brand` |
| 6 | `body_type` | Selection | - | No | No | Yes | - | ประเภทตัวถัง |
| 7 | `active` | Boolean | - | No | No | Yes | True | สถานะใช้งาน |
| 8 | `generation_ids` | One2many | - | No | No | No | - | Generations → `itx.info.vehicle.generation` |
| 9 | `generation_count` | Integer | - | No | No | No | computed | จำนวน Generation |
| 10 | `full_name` | Char | 200 | No | Yes | Yes | computed | ชื่อเต็ม เช่น `Honda Civic` |

### Selection Values - body_type

```python
BODY_TYPE_SELECTION = [
    ('sedan', 'Sedan'),
    ('hatchback', 'Hatchback'),
    ('suv', 'SUV'),
    ('crossover', 'Crossover'),
    ('pickup', 'Pickup Truck'),
    ('van', 'Van/MPV'),
    ('coupe', 'Coupe'),
    ('convertible', 'Convertible'),
    ('wagon', 'Wagon'),
    ('truck', 'Truck'),
    ('other', 'Other'),
]
```

### Constraints

```python
_sql_constraints = [
    ('code_brand_uniq', 'UNIQUE(code, brand_id)', 'Model code must be unique per brand!'),
    ('abbr_brand_uniq', 'UNIQUE(abbr, brand_id)', 'Model abbreviation must be unique per brand!'),
]
```

### Computed Fields

```python
@api.depends('brand_id', 'name')
def _compute_full_name(self):
    for rec in self:
        if rec.brand_id and rec.name:
            rec.full_name = f"{rec.brand_id.name} {rec.name}"
        else:
            rec.full_name = rec.name or ''
```

---

## 3. itx.info.vehicle.generation (ยุค/Generation)

**Technical Name:** `itx_info_vehicle_generation`
**Description:** Generation/year range of a vehicle model

### Fields

| # | Field Name | Type | Size | Required | Index | Stored | Default | Description |
|---|------------|------|------|----------|-------|--------|---------|-------------|
| 1 | `code` | Char | 50 | Yes | Yes | Yes | - | รหัสตามตลาด เช่น `FD1`, `FB7` |
| 2 | `name` | Char | 100 | Yes | Yes | Yes | - | ชื่อ เช่น `Gen 8 (FD) 2006-2011` |
| 3 | `description` | Text | - | No | No | Yes | - | คำอธิบายเพิ่มเติม |
| 4 | `abbr` | Char | 10 | Yes | Yes | Yes | auto | ตัวย่อ เช่น `FD`, `FB` |
| 5 | `model_id` | Many2one | - | Yes | Yes | Yes | - | สังกัดรุ่น → `itx.info.vehicle.model` |
| 6 | `chassis_code` | Char | 50 | No | Yes | Yes | - | รหัสแชสซี เช่น `FD1/FD2` |
| 7 | `year_start` | Integer | - | No | No | Yes | - | ปีเริ่มผลิต เช่น `2006` |
| 8 | `year_end` | Integer | - | No | No | Yes | 0 | ปีสิ้นสุด (0 = ยังผลิตอยู่) |
| 9 | `active` | Boolean | - | No | No | Yes | True | สถานะใช้งาน |
| 10 | `variant_ids` | One2many | - | No | No | No | - | Variants → `itx.info.vehicle.variant` |
| 11 | `variant_count` | Integer | - | No | No | No | computed | จำนวน Variant |
| 12 | `brand_id` | Many2one | - | No | Yes | Yes | related | ยี่ห้อ (related) |
| 13 | `full_name` | Char | 255 | No | Yes | Yes | computed | ชื่อเต็ม |

### Constraints

```python
_sql_constraints = [
    ('code_model_uniq', 'UNIQUE(code, model_id)', 'Generation code must be unique per model!'),
]

@api.constrains('year_start', 'year_end')
def _check_year_range(self):
    for rec in self:
        if rec.year_start and rec.year_end and rec.year_end != 0:
            if rec.year_end < rec.year_start:
                raise ValidationError('Year end must be greater than or equal to year start!')
```

### Computed Fields

```python
brand_id = fields.Many2one(
    'itx.info.vehicle.brand',
    related='model_id.brand_id',
    store=True,
    string='Brand'
)

@api.depends('model_id', 'name')
def _compute_full_name(self):
    for rec in self:
        if rec.model_id and rec.model_id.full_name and rec.name:
            rec.full_name = f"{rec.model_id.full_name} {rec.name}"
        else:
            rec.full_name = rec.name or ''
```

---

## 4. itx.info.vehicle.variant (รุ่นย่อย/Trim)

**Technical Name:** `itx_info_vehicle_variant`
**Description:** Specific variant/trim level of a generation

### Fields

| # | Field Name | Type | Size | Required | Index | Stored | Default | Description |
|---|------------|------|------|----------|-------|--------|---------|-------------|
| 1 | `code` | Char | 50 | Yes | Yes | Yes | - | รหัสตามตลาด เช่น `1.8S-IVTEC` |
| 2 | `name` | Char | 100 | Yes | Yes | Yes | - | ชื่อ เช่น `1.8 S i-VTEC` |
| 3 | `description` | Text | - | No | No | Yes | - | คำอธิบายเพิ่มเติม |
| 4 | `abbr` | Char | 10 | Yes | Yes | Yes | auto | ตัวย่อ เช่น `1.8S` |
| 5 | `generation_id` | Many2one | - | Yes | Yes | Yes | - | สังกัด Generation |
| 6 | `engine_code` | Char | 30 | No | Yes | Yes | - | รหัสเครื่องยนต์ เช่น `R18A`, `K20A` |
| 7 | `engine_displacement` | Float | - | No | No | Yes | - | ความจุเครื่องยนต์ (ลิตร) เช่น `1.8` |
| 8 | `fuel_type` | Selection | - | No | No | Yes | - | ประเภทเชื้อเพลิง |
| 9 | `transmission` | Selection | - | No | No | Yes | - | ประเภทเกียร์ |
| 10 | `drive_type` | Selection | - | No | No | Yes | - | ระบบขับเคลื่อน |
| 11 | `active` | Boolean | - | No | No | Yes | True | สถานะใช้งาน |
| 12 | `brand_id` | Many2one | - | No | Yes | Yes | related | ยี่ห้อ (related) |
| 13 | `model_id` | Many2one | - | No | Yes | Yes | related | รุ่น (related) |
| 14 | `full_name` | Char | 255 | No | Yes | Yes | computed | ชื่อเต็ม |

### Selection Values

```python
FUEL_TYPE_SELECTION = [
    ('gasoline', 'Gasoline (เบนซิน)'),
    ('diesel', 'Diesel (ดีเซล)'),
    ('hybrid', 'Hybrid'),
    ('phev', 'Plug-in Hybrid'),
    ('ev', 'Electric (EV)'),
    ('lpg', 'LPG'),
    ('cng', 'CNG'),
    ('other', 'Other'),
]

TRANSMISSION_SELECTION = [
    ('manual', 'Manual (MT)'),
    ('auto', 'Automatic (AT)'),
    ('cvt', 'CVT'),
    ('dct', 'Dual Clutch (DCT)'),
    ('amt', 'Automated Manual (AMT)'),
    ('other', 'Other'),
]

DRIVE_TYPE_SELECTION = [
    ('ff', 'FF (Front-wheel Drive)'),
    ('fr', 'FR (Rear-wheel Drive)'),
    ('awd', 'AWD (All-wheel Drive)'),
    ('4wd', '4WD (Four-wheel Drive)'),
    ('rr', 'RR (Rear Engine, Rear Drive)'),
    ('mr', 'MR (Mid Engine, Rear Drive)'),
]
```

### Constraints

```python
_sql_constraints = [
    ('code_gen_uniq', 'UNIQUE(code, generation_id)', 'Variant code must be unique per generation!'),
]

@api.constrains('engine_displacement')
def _check_engine_displacement(self):
    for rec in self:
        if rec.engine_displacement and rec.engine_displacement <= 0:
            raise ValidationError('Engine displacement must be greater than 0!')
```

### Computed Fields

```python
brand_id = fields.Many2one(
    'itx.info.vehicle.brand',
    related='generation_id.model_id.brand_id',
    store=True,
)

model_id = fields.Many2one(
    'itx.info.vehicle.model',
    related='generation_id.model_id',
    store=True,
)

@api.depends('generation_id', 'name')
def _compute_full_name(self):
    for rec in self:
        if rec.generation_id and rec.generation_id.full_name and rec.name:
            rec.full_name = f"{rec.generation_id.full_name} {rec.name}"
        else:
            rec.full_name = rec.name or ''
```

---

## 5. itx.info.vehicle.part.category (ประเภทอะไหล่)

**Technical Name:** `itx_info_vehicle_part_category`
**Description:** Hierarchical part categories for vehicle parts

### Fields

| # | Field Name | Type | Size | Required | Index | Stored | Default | Description |
|---|------------|------|------|----------|-------|--------|---------|-------------|
| 1 | `code` | Char | 50 | Yes | Yes | Yes | - | รหัสประเภท เช่น `ENGINE`, `TRANS` |
| 2 | `name` | Char | 100 | Yes | Yes | Yes | - | ชื่อประเภท เช่น `เครื่องยนต์` |
| 3 | `description` | Text | - | No | No | Yes | - | คำอธิบายเพิ่มเติม |
| 4 | `abbr` | Char | 10 | Yes | Yes | Yes | auto | ตัวย่อ เช่น `ENG` |
| 5 | `parent_id` | Many2one | - | No | Yes | Yes | - | ประเภทแม่ (hierarchy) |
| 6 | `child_ids` | One2many | - | No | No | No | - | ประเภทย่อย |
| 7 | `complete_name` | Char | 255 | No | Yes | Yes | computed | ชื่อเต็ม path |
| 8 | `parent_path` | Char | - | No | Yes | Yes | - | Materialized path |
| 9 | `active` | Boolean | - | No | No | Yes | True | สถานะใช้งาน |

### Special Attributes

```python
_parent_store = True
_parent_name = 'parent_id'
```

### Constraints

```python
_sql_constraints = [
    ('code_uniq', 'UNIQUE(code)', 'Part category code must be unique!'),
    ('abbr_uniq', 'UNIQUE(abbr)', 'Part category abbreviation must be unique!'),
]

@api.constrains('parent_id')
def _check_parent_recursion(self):
    if not self._check_recursion():
        raise ValidationError('Error! You cannot create recursive categories.')
```

### Computed Fields

```python
@api.depends('name', 'parent_id.complete_name')
def _compute_complete_name(self):
    for rec in self:
        if rec.parent_id:
            rec.complete_name = f"{rec.parent_id.complete_name} / {rec.name}"
        else:
            rec.complete_name = rec.name
```

---

## 6. product.template (Inherit)

**Technical Name:** `product_template` (inherit)
**Description:** Extend product template with vehicle part fields

### New Fields

| # | Field Name | Type | Size | Required | Index | Stored | Default | Description |
|---|------------|------|------|----------|-------|--------|---------|-------------|
| 1 | `itx_is_vehicle_part` | Boolean | - | No | Yes | Yes | False | เปิดใช้งาน Vehicle Part mode |
| 2 | `itx_brand_id` | Many2one | - | No | Yes | Yes | - | ยี่ห้อรถ |
| 3 | `itx_model_id` | Many2one | - | No | Yes | Yes | - | รุ่นรถ |
| 4 | `itx_generation_id` | Many2one | - | No | Yes | Yes | - | Generation |
| 5 | `itx_variant_id` | Many2one | - | No | Yes | Yes | - | Variant |
| 6 | `itx_part_category_id` | Many2one | - | No | Yes | Yes | - | ประเภทอะไหล่ |
| 7 | `itx_oem_part_number` | Char | 100 | No | Yes | Yes | - | OEM Part Number |
| 8 | `itx_condition_grade` | Selection | - | No | No | Yes | - | เกรดสภาพ |
| 9 | `itx_sequence` | Char | 10 | No | Yes | Yes | auto | Running number (แก้ได้) |

### Selection Values - itx_condition_grade

```python
CONDITION_GRADE_SELECTION = [
    ('A', 'A - Excellent (ดีมาก)'),
    ('B', 'B - Good (ดี)'),
    ('C', 'C - Fair (พอใช้)'),
    ('D', 'D - Poor (ต้องซ่อม)'),
]
```

### Domain Constraints

```python
itx_model_id = fields.Many2one(
    domain="[('brand_id', '=', itx_brand_id)]"
)
itx_generation_id = fields.Many2one(
    domain="[('model_id', '=', itx_model_id)]"
)
itx_variant_id = fields.Many2one(
    domain="[('generation_id', '=', itx_generation_id)]"
)
```

### Onchange Methods

```python
@api.onchange('itx_brand_id')
def _onchange_itx_brand_id(self):
    """Clear dependent fields when brand changes"""
    self.itx_model_id = False
    self.itx_generation_id = False
    self.itx_variant_id = False

@api.onchange('itx_model_id')
def _onchange_itx_model_id(self):
    """Clear dependent fields when model changes"""
    self.itx_generation_id = False
    self.itx_variant_id = False

@api.onchange('itx_generation_id')
def _onchange_itx_generation_id(self):
    """Clear variant when generation changes"""
    self.itx_variant_id = False
```

### Internal Reference Generation

```python
@api.depends('itx_brand_id', 'itx_model_id', 'itx_generation_id',
             'itx_variant_id', 'itx_part_category_id', 'itx_sequence')
def _compute_default_code(self):
    """Auto-generate internal reference from vehicle hierarchy"""
    for rec in self:
        if rec.itx_is_vehicle_part:
            parts = []
            if rec.itx_brand_id:
                parts.append(rec.itx_brand_id.abbr or '')
            if rec.itx_model_id:
                parts.append(rec.itx_model_id.abbr or '')
            if rec.itx_generation_id:
                parts.append(rec.itx_generation_id.abbr or '')
            if rec.itx_variant_id:
                parts.append(rec.itx_variant_id.abbr or '')
            if rec.itx_part_category_id:
                parts.append(rec.itx_part_category_id.abbr or '')
            if rec.itx_sequence:
                parts.append(rec.itx_sequence)

            rec.default_code = '-'.join(filter(None, parts))
```

### Sequence Generation

```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('itx_is_vehicle_part') and not vals.get('itx_sequence'):
            vals['itx_sequence'] = self.env['ir.sequence'].next_by_code(
                'itx.info.vehicle.part.sequence'
            ) or '00001'
    return super().create(vals_list)
```

---

## Sequence Configuration

### ir.sequence Data

```xml
<record id="seq_itx_vehicle_part" model="ir.sequence">
    <field name="name">Vehicle Part Sequence</field>
    <field name="code">itx.info.vehicle.part.sequence</field>
    <field name="prefix"></field>
    <field name="padding">5</field>
    <field name="number_next">1</field>
    <field name="number_increment">1</field>
</record>
```

---

## Abbreviation Auto-Generation Logic

```python
def _generate_abbr(self, name, code=None):
    """
    Generate abbreviation from name or code

    Priority:
    1. Extract from parentheses if exists: "Gen 8 (FD)" → "FD"
    2. Use code if provided: code="ENGINE" → "ENG"
    3. Take first 3-4 chars uppercase: "Honda" → "HON"

    Rules:
    - Max 10 characters
    - Uppercase
    - Remove spaces and special chars
    """
    import re

    # Try to extract from parentheses
    match = re.search(r'\(([^)]+)\)', name or '')
    if match:
        return match.group(1).upper()[:10]

    # Use code if provided
    if code:
        return code[:3].upper()

    # Take first 3 chars of name
    if name:
        # Remove non-alphanumeric, take first 3-4 chars
        clean = re.sub(r'[^a-zA-Z0-9]', '', name)
        return clean[:3].upper()

    return ''
```

---

## Summary Statistics

| Model | Total Fields | Required | Computed | Related |
|-------|-------------|----------|----------|---------|
| Brand | 9 | 3 | 1 | 0 |
| Model | 10 | 4 | 2 | 0 |
| Generation | 13 | 4 | 2 | 1 |
| Variant | 14 | 4 | 1 | 2 |
| Part Category | 9 | 3 | 1 | 0 |
| Product (inherit) | 9 | 0 | 1 | 0 |
| **Total** | **64** | **18** | **8** | **3** |
