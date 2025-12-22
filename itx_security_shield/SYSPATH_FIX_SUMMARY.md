# sys.path Fix Summary for PyArmor + Odoo

**วันที่:** 2025-12-04  
**ปัญหา:** ModuleNotFoundError: No module named 'pyarmor_runtime_000000'  
**วิธีแก้:** sys.path fix (Dynamic path injection)

---

## 🎯 คำตอบคำถาม

### 1. sys.path เป็น Dynamic หรือ Fixed?

**✅ เป็น Dynamic!**

```python
__addon_dir__ = os.path.dirname(os.path.abspath(__file__))
#                                                 ↑
#                                        __file__ = runtime path
```

**ทดสอบ:**
| สถานการณ์ | ผลลัพธ์ |
|-----------|--------|
| เปลี่ยนชื่อ directory | ✅ ทำงานได้ |
| ย้าย directory ไปที่อื่น | ✅ ทำงานได้ |
| Copy ไปเครื่องอื่น | ✅ ทำงานได้ |

**เหตุผล:**
- ใช้ `__file__` variable = path ของไฟล์ **ณ เวลาที่ Python รัน**
- คำนวณ path **ใหม่ทุกครั้ง** ไม่ใช่ hardcode

---

## 📝 ไฟล์ที่ถูก Update

### 1. `obfuscate_addon.sh`

**เพิ่ม Step 9:** Inject sys.path fix into __init__.py

```bash
# Step 9: Inject sys.path fix
SYSPATH_FIX="# ========== sys.path fix for Odoo addon ==========
import sys
import os
__addon_dir__ = os.path.dirname(os.path.abspath(__file__))
if __addon_dir__ not in sys.path:
    sys.path.insert(0, __addon_dir__)
# =================================================="

# Inject into obfuscated __init__.py
echo "$FIRST_LINE" > "$INIT_FILE"
echo "$SYSPATH_FIX" >> "$INIT_FILE"
echo "$REST_CONTENT" >> "$INIT_FILE"
```

**Features:**
- ✅ Automatic injection
- ✅ Verification check
- ✅ Error handling

---

### 2. `PYARMOR_GUIDE.md`

**เพิ่ม/อัพเดท:**

1. **Step 9 ใน "ขั้นตอนการทำงาน"**
   - อธิบาย sys.path fix
   - แสดงโค้ดที่ inject
   - อธิบายว่าทำไมต้องมี

2. **Problem 1: ModuleNotFoundError**
   - อัพเดทสาเหตุ (เพิ่ม "ไม่มี sys.path fix")
   - เพิ่มวิธีตรวจสอบ sys.path fix
   - แสดง diagram การทำงาน
   - เน้นว่า Dynamic path ทำงานได้แม้เปลี่ยนชื่อ/ย้าย

---

## 🔧 วิธีทดสอบ Dynamic Path

### Test 1: เปลี่ยนชื่อ directory

```bash
# ก่อน
/path/custom_addons/itx_helloworld/

# หลัง - เปลี่ยนชื่อ
mv /path/custom_addons/itx_helloworld /path/custom_addons/itx_hello_new

# ทดสอบ
# 1. Update Apps List ใน Odoo
# 2. Activate addon
# ✅ ต้องทำงานได้ปกติ
```

### Test 2: ย้าย directory

```bash
# ก่อน
/home/user/odoo19/custom_addons/itx_helloworld/

# หลัง - ย้าย
mv /home/user/odoo19/custom_addons/itx_helloworld /opt/odoo/addons/

# แก้ addons_path ใน odoo.conf
# ทดสอบ
# ✅ ต้องทำงานได้ปกติ
```

---

## 📚 Reference: sys.path Fix Code

```python
# ========== sys.path fix for Odoo addon ==========
import sys
import os

# Get addon directory (dynamic - calculated at runtime)
__addon_dir__ = os.path.dirname(os.path.abspath(__file__))

# Add to sys.path if not already there
if __addon_dir__ not in sys.path:
    sys.path.insert(0, __addon_dir__)
# ==================================================
```

**การทำงาน:**

1. `__file__` = `/path/to/addon/__init__.py` (runtime)
2. `os.path.abspath(__file__)` = absolute path
3. `os.path.dirname(...)` = `/path/to/addon/`
4. `sys.path.insert(0, ...)` = เพิ่มเข้า sys.path อันดับแรก

**ผลลัพธ์:**

```python
sys.path = [
    '/path/to/addon/',              # ← เพิ่มเข้ามา (priority 0)
    '/usr/lib/python3.12/',
    '/home/user/.local/lib/',
    ...
]

# Python จะหา pyarmor_runtime_000000 ใน sys.path ตามลำดับ
# → เจอที่ /path/to/addon/pyarmor_runtime_000000/ ทันที! ✅
```

---

## 🚀 Quick Start

### ใช้งาน Script (Automatic)

```bash
cd /home/chainarp/PycharmProjects/odoo19/custom_addons/itx_security_shield

# Obfuscate addon
./obfuscate_addon.sh itx_helloworld

# Script จะ inject sys.path fix อัตโนมัติใน Step 9
```

### ตรวจสอบผลลัพธ์

```bash
# ดู __init__.py
head -10 /path/to/addon/__init__.py

# ต้องเห็น:
# 1. PyArmor header (บรรทัดที่ 1)
# 2. sys.path fix (บรรทัดที่ 2-7)
# 3. from pyarmor_runtime_000000 import __pyarmor__ (บรรทัดที่ 9)
```

### ทดสอบใน Odoo

```bash
# 1. Update Apps List
# 2. Search addon
# 3. Install/Activate
# ✅ ควรทำงานได้โดยไม่มี ModuleNotFoundError
```

---

## 📞 หากมีปัญหา

### ตรวจสอบ Checklist

- [ ] pyarmor_runtime_000000/ อยู่ใน addon directory
- [ ] __init__.py มี sys.path fix (บรรทัดที่ 2-7)
- [ ] __manifest__.py ไม่ถูก obfuscate
- [ ] Restart Odoo server แล้ว
- [ ] Update Apps List แล้ว

### Debug Command

```bash
# 1. ตรวจสอบ structure
tree -L 2 /path/to/addon/

# 2. ตรวจสอบ sys.path fix
grep -A 5 "sys.path.insert" /path/to/addon/__init__.py

# 3. ตรวจสอบ runtime
ls -la /path/to/addon/pyarmor_runtime_000000/

# 4. ดู Odoo log
tail -100 /path/to/odoo/log/odoo.log | grep -i "error\|module"
```

---

**สรุป:**
- ✅ sys.path fix เป็น **Dynamic**
- ✅ Script inject **อัตโนมัติ**
- ✅ ทำงานได้แม้ **เปลี่ยนชื่อ/ย้าย**
- ✅ Documentation **ครบถ้วน**

