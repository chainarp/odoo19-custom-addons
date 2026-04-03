# Session Notes - 2026-04-03

## สิ่งที่ต้อง Implement (ตอนเย็น)

---

### 1. สร้าง Model: `itx.info.vehicle.template.part`

```python
_name = 'itx.info.vehicle.template.part'

Fields:
- code (Char, required, unique)
- name (Char, required) - ชื่อไทย ชัดเจนในตัวเอง
- name_en (Char) - ชื่ออังกฤษ
- abbr (Char, required) - for Internal Reference
- desc (Text) - อธิบายบริบท
- category_id (Many2one → part.category, optional)
- active (Boolean)
```

**Data:** ~80 รายการ จาก `docs/PART_NAME_REFERENCE.md`

---

### 2. สร้าง Model: `itx.info.vehicle.template.bom`

```python
_name = 'itx.info.vehicle.template.bom'

Fields:
- body_type_id (Many2one → mgr.body.type, required)
- part_category_id (Many2one → part.category, required)
- part_template_id (Many2one → template.part, required)
- qty (Integer, default=1) ✓
- sequence (Integer, default=10) ✓
# is_optional - ข้ามไปก่อน

UK: UNIQUE(body_type_id, part_template_id)
```

**Data:** จาก Excel แบบประเมินซากรถยนต์.xlsx (7 body types)

---

### 3. Update: `product_template.py`

**เปลี่ยนแปลง:**
- เพิ่ม `itx_part_name_id` (Many2one → template.part)
- ลบ SQL constraint เดิม
- ใช้ Python constraint แทน

**UK ใหม่ (เฉพาะ vehicle part):**
```python
@api.constrains(...)
def _check_vehicle_part_unique(self):
    if not rec.itx_is_vehicle_part:
        continue  # General product = Odoo ปกติ 100%

    # Check UK: spec_id + part_name_id + origin + condition
```

**Logic:**
- `itx_is_vehicle_part = True` → UK ทำงาน
- `itx_is_vehicle_part = False` → Odoo original (ขาย furniture ได้)

---

### 4. Update Views

- `product_template_views.xml` - ใช้ `itx_part_name_id` แทน free text name
- สร้าง views สำหรับ `template.part` และ `template.bom`

---

## Design Decisions (ยืนยันแล้ว)

| หัวข้อ | ตัดสินใจ |
|--------|----------|
| Part Name | Master table ไม่ใช่ free text |
| ซ้าย/ขวา | แยกคนละ record |
| UK สำหรับ Vehicle Part | spec + part_name + origin + condition |
| UK สำหรับ General Product | ไม่มี (Odoo ปกติ) |
| oem_part_number | ไม่อยู่ใน UK, เป็น info อย่างเดียว |
| part_category | ไม่อยู่ใน UK |
| BOM qty | มี (default=1) |
| BOM sequence | มี |
| BOM is_optional | ข้ามไปก่อน |

---

## Files ที่เกี่ยวข้อง

```
docs/PART_NAME_REFERENCE.md   ← รายการอะไหล่ ~80 ชิ้น (cleaned)
docs/MODULE_SUMMARY.md        ← สรุป module
/home/chainarp/Downloads/แบบประเมินซากรถยนต์.xlsx  ← Excel จาก user
```

---

## Git Status

```
Last commit: d035896 - docs: Add MODULE_SUMMARY.md
Branch: master
Remote: https://github.com/chainarp/odoo19-custom-addons.git
```

---

## Next Session Commands

```bash
# Activate venv
source /home/chainarp/PycharmProjects/odoo19/.venv/bin/activate
cd /home/chainarp/PycharmProjects/odoo19/custom_addons/itx_info_vehicle

# After implement, upgrade module
python3 /home/chainarp/PycharmProjects/odoo19/odoo/odoo-bin \
  -c /home/chainarp/PycharmProjects/odoo19/odoo.conf \
  -d odoo19_new -u itx_info_vehicle --stop-after-init
```

---

**พร้อม implement ตอนเย็นครับ!**
