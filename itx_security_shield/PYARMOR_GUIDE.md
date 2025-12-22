# PyArmor Obfuscation Guide for Odoo Addons

**คู่มือการ obfuscate Odoo addon ด้วย PyArmor**

---

## 📋 สารบัญ

1. [ภาพรวม](#ภาพรวม)
2. [ข้อกำหนดเบื้องต้น](#ข้อกำหนดเบื้องต้น)
3. [วิธีใช้งาน Script](#วิธีใช้งาน-script)
4. [ขั้นตอนการทำงาน](#ขั้นตอนการทำงาน)
5. [ปัญหาที่พบบ่อยและวิธีแก้](#ปัญหาที่พบบ่อยและวิธีแก้)
6. [ข้อจำกัดของ PyArmor กับ Odoo](#ข้อจำกัดของ-pyarmor-กับ-odoo)
7. [แนวทางทดแทน](#แนวทางทดแทน)

---

## ภาพรวม

### PyArmor คืออะไร?

PyArmor เป็นเครื่องมือสำหรับ **obfuscate (เข้ารหัส)** Python code เพื่อ:
- 🔒 ป้องกัน reverse engineering
- 🔒 ซ่อน source code
- 🔒 ป้องกันการคัดลอก

### การทำงานของ PyArmor

```
Python source (.py)
    ↓
PyArmor obfuscation
    ├─ Compile to bytecode
    ├─ Encrypt bytecode
    ├─ Add runtime loader
    └─ Generate runtime files
    ↓
Obfuscated files
    ├─ __init__.py (encrypted)
    ├─ models/*.py (encrypted)
    └─ pyarmor_runtime_000000/
        └─ pyarmor_runtime.so
```

---

## ข้อกำหนดเบื้องต้น

### 1. Python Virtual Environment

```bash
# ตรวจสอบว่ามี venv หรือยัง
ls /home/chainarp/PycharmProjects/odoo19/.venv

# ถ้าไม่มี ให้สร้าง
python3 -m venv /home/chainarp/PycharmProjects/odoo19/.venv
```

### 2. PyArmor

```bash
# Activate venv
source /home/chainarp/PycharmProjects/odoo19/.venv/bin/activate

# Install PyArmor
pip install pyarmor

# ตรวจสอบ version
pyarmor --version
# Expected: Pyarmor 9.x.x
```

### 3. Backup Addon

```bash
# สร้าง backup directory
mkdir -p /home/chainarp/PycharmProjects/odoo19/custom_addons/backups

# Backup addon manually (optional)
cp -r custom_addons/your_addon custom_addons/backups/your_addon_backup
```

---

## วิธีใช้งาน Script

### Basic Usage

```bash
cd /home/chainarp/PycharmProjects/odoo19/custom_addons/itx_security_shield

# Obfuscate addon
./obfuscate_addon.sh <addon_name>

# Example
./obfuscate_addon.sh itx_helloworld
```

### ผลลัพธ์

```
ℹ️  Starting PyArmor obfuscation for addon: itx_helloworld

ℹ️  Step 1: Validating addon...
✅ Addon found: /home/chainarp/PycharmProjects/odoo19/custom_addons/itx_helloworld

ℹ️  Step 2: Creating backup...
✅ Backup created: .../backups/itx_helloworld_backup_20241204_001234

ℹ️  Step 3: Activating virtual environment...
✅ Virtual environment activated

ℹ️  Step 4: Checking PyArmor...
✅ PyArmor installed: Pyarmor 9.2.1

ℹ️  Step 5: Obfuscating addon with PyArmor...
✅ PyArmor obfuscation completed

ℹ️  Step 6: Restoring __manifest__.py...
⚠️  Odoo requires __manifest__.py to be non-obfuscated!
✅ __manifest__.py restored (non-obfuscated)

ℹ️  Step 7: Copying non-Python files...
✅ Copied: demo/
✅ Copied: security/
✅ Copied: views/

ℹ️  Step 8: Moving pyarmor_runtime into addon...
⚠️  This is necessary for Odoo to import the runtime!
✅ pyarmor_runtime_000000 moved into addon

ℹ️  Step 9: Injecting sys.path fix into __init__.py...
⚠️  This fixes ModuleNotFoundError for pyarmor_runtime_000000!
✅ sys.path fix injected into __init__.py
✅ Verification passed: sys.path fix found in __init__.py

ℹ️  Step 10: Replacing original addon...
⚠️  This will replace the original addon with the obfuscated version!
Continue? (y/N): y
✅ Original addon replaced with obfuscated version

ℹ️  Step 11: Cleaning Python cache...
✅ Python cache cleaned

✅ ═══════════════════════════════════════════════════════════
✅   PyArmor Obfuscation Completed Successfully!
✅ ═══════════════════════════════════════════════════════════

Done! 🎉
```

---

## ขั้นตอนการทำงาน

### Step 1: Validate Addon
- เช็คว่า addon directory มีอยู่
- เช็คว่ามี `__manifest__.py`

### Step 2: Backup
- สร้าง backup ของ addon เดิม
- บันทึกไว้ที่ `backups/` พร้อม timestamp

### Step 3: Activate Virtual Environment
- เปิดใช้งาน venv ที่มี PyArmor

### Step 4: Check PyArmor
- ตรวจสอบว่า PyArmor ติดตั้งแล้วหรือยัง
- ถ้ายัง → ติดตั้งอัตโนมัติ

### Step 5: Obfuscate with PyArmor
- รัน `pyarmor gen` เพื่อ obfuscate
- สร้าง `addon_obfuscated/` directory

### Step 6: Restore `__manifest__.py` ⚠️ **สำคัญ!**
- Copy `__manifest__.py` เดิมกลับมา
- เพราะ Odoo ต้องการไฟล์ปกติ (ไม่ใช่ bytecode)
- ถ้าไม่ทำ → Odoo จะมองไม่เห็น addon!

### Step 7: Copy Non-Python Files
- Copy ไฟล์ XML, CSV ที่ PyArmor ไม่ได้ copy
- รวม: `demo/`, `security/`, `views/`, `data/`, `static/`

### Step 8: Move `pyarmor_runtime` Into Addon
- ย้าย `pyarmor_runtime_000000/` เข้าไปใน addon
- จำเป็นเพื่อให้ Python import ได้

### Step 9: Inject sys.path Fix ⚠️ **สำคัญมาก!**
- เพิ่ม sys.path fix ลงใน `__init__.py` (หลัง obfuscate)
- แก้ปัญหา `ModuleNotFoundError: pyarmor_runtime_000000`
- **Dynamic path** - ทำงานได้แม้เปลี่ยนชื่อ directory หรือย้ายตำแหน่ง

**โค้ดที่ inject:**
```python
# ========== sys.path fix for Odoo addon ==========
import sys
import os
__addon_dir__ = os.path.dirname(os.path.abspath(__file__))
if __addon_dir__ not in sys.path:
    sys.path.insert(0, __addon_dir__)
# ==================================================
```

**ทำไมต้องมี?**
- Odoo โหลด addon แบบ isolated namespace
- Python ไม่รู้ว่า `pyarmor_runtime_000000/` อยู่ใน addon directory
- sys.path fix เพิ่ม addon directory เข้า `sys.path` ก่อน import runtime

### Step 10: Replace Original Addon
- ลบ addon เดิม
- แทนที่ด้วย obfuscated version

### Step 11: Clean Cache
- ลบ `__pycache__/`
- ลบ `*.pyc` files

---

## ปัญหาที่พบบ่อยและวิธีแก้

### ❌ Problem 1: `ModuleNotFoundError: No module named 'pyarmor_runtime_000000'`

**สาเหตุ:**
1. `pyarmor_runtime_000000` ไม่อยู่ใน addon directory
2. **Python ไม่รู้ว่า runtime อยู่ใน addon** (Odoo isolated namespace)
3. ไม่มี sys.path fix ใน `__init__.py`

**✅ วิธีแก้ (Automatic - Script ทำให้แล้ว):**

Script จะ inject sys.path fix ลงใน `__init__.py` อัตโนมัติในขั้นตอนที่ 9

**ตรวจสอบว่า sys.path fix มีอยู่หรือไม่:**
```bash
head -10 custom_addons/your_addon/__init__.py
```

**ต้องเห็นโค้ดนี้:**
```python
# Pyarmor 9.2.1 (trial), 000000, non-profits, 2025-12-04T11:43:42.005092
# ========== sys.path fix for Odoo addon ==========
import sys
import os
__addon_dir__ = os.path.dirname(os.path.abspath(__file__))
if __addon_dir__ not in sys.path:
    sys.path.insert(0, __addon_dir__)
# ==================================================
from pyarmor_runtime_000000 import __pyarmor__
```

**📋 Manual Fix (ถ้า script ไม่ได้ inject):**

1. เปิดไฟล์ obfuscated `__init__.py`
2. เพิ่มโค้ด sys.path fix **หลังบรรทัดแรก** (PyArmor header)
3. **ก่อน** `from pyarmor_runtime_000000 import __pyarmor__`

**🔑 ทำไม sys.path fix ถึงสำคัญ?**

```
ไม่มี sys.path fix:
Python หา pyarmor_runtime_000000:
  ✗ /usr/lib/python3.12/
  ✗ /home/user/.local/lib/
  ✗ /path/to/odoo/
  ✗ ไม่มี /path/to/addon/  ← ไม่รู้ว่าต้องหาในนี้!
→ ModuleNotFoundError

มี sys.path fix:
sys.path.insert(0, '/path/to/addon/')
Python หา pyarmor_runtime_000000:
  ✓ /path/to/addon/pyarmor_runtime_000000/  ← เจอแล้ว!
→ Import สำเร็จ ✅
```

**โครงสร้างที่ถูกต้อง:**
```
your_addon/
├── __init__.py                    (obfuscated + sys.path fix)
├── __manifest__.py                (NOT obfuscated!)
├── models/                        (obfuscated)
├── controllers/                   (obfuscated)
├── pyarmor_runtime_000000/        ← ต้องอยู่ในนี้!
│   ├── __init__.py
│   └── pyarmor_runtime.so
└── ...
```

**🎯 Dynamic Path:**
- sys.path fix คำนวณ path **ใหม่ทุกครั้งที่รัน**
- ใช้ `__file__` variable (runtime path)
- ✅ **ทำงานได้แม้เปลี่ยนชื่อ directory หรือย้ายที่**

---

### ❌ Problem 2: `SyntaxError: invalid syntax` in `__manifest__.py`

**สาเหตุ:**
- `__manifest__.py` ถูก obfuscate
- Odoo ใช้ `ast.literal_eval()` ซึ่งไม่รองรับ bytecode

**วิธีแก้:**
```bash
# Restore __manifest__.py จาก backup
cp backups/your_addon_backup/__manifest__.py custom_addons/your_addon/

# ตรวจสอบว่าไม่มี pyarmor code
head -5 custom_addons/your_addon/__manifest__.py
# ต้องเห็น: {
#     'name': "Your Addon",
#     ...
# }
# ไม่ใช่: # Pyarmor 9.2.1...
#        from pyarmor_runtime_000000 import __pyarmor__
```

---

### ❌ Problem 3: Addon ไม่ปรากฏใน Apps List

**สาเหตุ:**
- Odoo cache
- หรือ `__manifest__.py` ถูก obfuscate

**วิธีแก้:**
```bash
# 1. ลบ __pycache__
find custom_addons/your_addon -type d -name "__pycache__" -exec rm -rf {} +

# 2. Restart Odoo
pkill -f odoo-bin
cd /home/chainarp/PycharmProjects/odoo19
source .venv/bin/activate
./odoo-bin -c odoo.conf

# 3. Update Apps List ใน Odoo UI
# Settings → Apps → Update Apps List
```

---

### ❌ Problem 4: ขาดไฟล์ XML/CSV

**สาเหตุ:**
- PyArmor obfuscate เฉพาะ `.py` files
- ไฟล์อื่นไม่ถูก copy

**วิธีแก้:**
```bash
# Copy จาก backup
cp -r backups/your_addon_backup/demo custom_addons/your_addon/
cp -r backups/your_addon_backup/security custom_addons/your_addon/
cp -r backups/your_addon_backup/views custom_addons/your_addon/
```

---

## ข้อจำกัดของ PyArmor กับ Odoo

### 🔴 ปัญหาหลัก

| ปัญหา | รายละเอียด |
|-------|-----------|
| **Import Path Conflict** | Odoo load addon แบบ isolated namespace ทำให้ PyArmor runtime import ไม่ได้ |
| **`__manifest__.py` Restriction** | ต้องไม่ obfuscate เพราะ Odoo parse แบบ static |
| **Complexity** | ต้องจัดการหลายขั้นตอน (restore manifest, copy files, move runtime) |
| **Maintenance** | Update addon ลำบาก ต้อง obfuscate ใหม่ทุกครั้ง |

### ⚠️ ข้อจำกัดอื่นๆ

1. **Trial Version Limitations:**
   - PyArmor trial มี watermark
   - ไม่มี advanced features
   - Trial license หมดอายุ

2. **Platform Dependency:**
   - `pyarmor_runtime.so` เป็น binary ต่าง platform
   - Linux → Linux เท่านั้น
   - ต้อง compile ใหม่สำหรับ Windows/Mac

3. **Performance:**
   - Obfuscated code ช้ากว่าปกติเล็กน้อย
   - Runtime overhead ~5-10%

---

## แนวทางทดแทน

### 🎯 แนะนำสำหรับ Odoo Addons

| วิธี | ข้อดี | ข้อเสีย | ความเหมาะสม |
|------|-------|---------|-------------|
| **1. License Management** | ✅ ไม่ต้อง obfuscate<br>✅ ใช้งานง่าย<br>✅ Maintenance ง่าย | ⚠️ Code อ่านได้ | ⭐⭐⭐⭐⭐ **แนะนำ!** |
| **2. Cython** | ✅ Compile to C<br>✅ Reverse ยาก<br>✅ เร็วขึ้น | ⚠️ ต้อง compile ต่าง platform | ⭐⭐⭐⭐ |
| **3. Nuitka** | ✅ Compile to binary<br>✅ Reverse ยากมาก | ⚠️ ซับซ้อน<br>⚠️ File ขนาดใหญ่ | ⭐⭐⭐ |
| **4. Python Bytecode** | ✅ ง่ายมาก | ❌ Reverse ได้ง่าย | ⭐⭐ |
| **5. PyArmor** | ✅ Obfuscate ดี | ❌ ปัญหากับ Odoo<br>❌ ซับซ้อน | ⭐ |

---

### วิธีที่ 1: License Management (แนะนำที่สุด!) ⭐

**ไม่ต้อง obfuscate แต่ใช้ license validation แทน**

```python
# itx_security_shield ใช้วิธีนี้อยู่แล้ว!

# 1. C Library (libintegrity.so) - Reverse ยาก
# 2. RSA-4096 + AES-256-GCM encryption
# 3. Hardware fingerprint binding
# 4. License validation on startup

# ข้อดี:
✅ Python code อ่านได้ (ไม่มีปัญหา)
✅ Logic สำคัญอยู่ใน C library (ป้องกันได้ดี)
✅ Hardware binding ป้องกัน copy license
✅ Maintenance ง่าย ไม่ต้อง obfuscate ใหม่
```

**Focus ที่:**
- ✅ ปรับปรุง C library (anti-debug, code signing)
- ✅ File integrity check
- ✅ Online license validation
- ❌ **ไม่ต้อง** obfuscate Python

---

### วิธีที่ 2: Cython

**Compile Python → C → .so**

```bash
# Install Cython
pip install Cython

# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        ["models/models.py", "controllers/controllers.py"],
        compiler_directives={'language_level': "3"}
    )
)
EOF

# Compile
python setup.py build_ext --inplace

# ผลลัพธ์: models.so, controllers.so
```

**ข้อดี:**
- ✅ Compile เป็น C extension
- ✅ Reverse ยากกว่า Python bytecode
- ✅ เร็วขึ้น 20-40%

**ข้อเสีย:**
- ⚠️ ต้อง compile ต่าง platform
- ⚠️ Debug ยากขึ้น

---

### วิธีที่ 3: Nuitka

**Compile Python → Binary**

```bash
# Install Nuitka
pip install nuitka

# Compile module
nuitka --module models/models.py

# ผลลัพธ์: models.cpython-312-x86_64-linux-gnu.so
```

**ข้อดี:**
- ✅ Compile เป็น native binary
- ✅ Reverse ยากที่สุด
- ✅ เร็วขึ้นมาก

**ข้อเสีย:**
- ⚠️ ซับซ้อน ต้อง configure เยอะ
- ⚠️ File ขนาดใหญ่
- ⚠️ Compile ช้า

---

## 📝 Best Practices

### ✅ ควรทำ:

1. **Backup ก่อนเสมอ**
   ```bash
   cp -r your_addon backups/your_addon_backup_$(date +%Y%m%d)
   ```

2. **ทดสอบก่อน deploy**
   ```bash
   # Test ใน development environment ก่อน
   ./odoo-bin -c odoo.conf --test-enable --stop-after-init -u your_addon
   ```

3. **Version control**
   ```bash
   git tag v1.0-obfuscated
   git push --tags
   ```

4. **เก็บ clean version**
   ```bash
   # เก็บ clean source ไว้ต่อพัฒนา
   # Deploy แค่ obfuscated version
   ```

### ❌ ไม่ควรทำ:

1. **Obfuscate __manifest__.py** → Odoo จะมองไม่เห็น addon
2. **ลืม copy XML/CSV files** → Views, security จะหาย
3. **ลืม backup** → ถ้าเกิดปัญหาจะกู้ไม่ได้
4. **Deploy โดยไม่ทดสอบ** → อาจมี import error ใน production

---

## 📚 เอกสารเพิ่มเติม

### PyArmor Documentation
- https://pyarmor.readthedocs.io/
- https://github.com/dashingsoft/pyarmor

### Odoo Development
- https://www.odoo.com/documentation/19.0/developer/
- https://www.odoo.com/documentation/19.0/developer/reference/backend/module.html

### Alternative Tools
- Cython: https://cython.org/
- Nuitka: https://nuitka.net/
- py2exe: https://www.py2exe.org/

---

## 🆘 Support

หากพบปัญหา:

1. **เช็ค log:**
   ```bash
   tail -f odoo.log | grep -i error
   ```

2. **Restore จาก backup:**
   ```bash
   rm -rf custom_addons/your_addon
   cp -r backups/your_addon_backup custom_addons/your_addon
   ```

3. **ลอง obfuscate ใหม่:**
   ```bash
   ./obfuscate_addon.sh your_addon
   ```

---

**สร้างเมื่อ:** 2024-12-04
**เวอร์ชัน:** 1.0.0
**ผู้เขียน:** ITX Corporation (with Claude Code)
