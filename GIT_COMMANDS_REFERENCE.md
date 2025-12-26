# Git Commands Reference - ITX Custom Addons

## 🚀 Setup Repository (ครั้งแรกเท่านั้น)

```bash
# 1. ไปที่ directory ที่ต้องการ
cd /home/chainarp/PycharmProjects/odoo19/custom_addons

# 2. สร้าง git repository
git init

# 3. สร้าง .gitignore (optional - กรองไฟล์ที่ไม่ต้องการ track)
nano .gitignore

# 4. เพิ่มไฟล์ทั้งหมดเข้า staging
git add .

# 5. Commit ครั้งแรก
git commit -m "feat: Initial commit - ITX Moduler Suite"

# 6. เชื่อมต่อกับ GitHub
git remote add origin https://TOKEN@github.com/USERNAME/REPO.git

# 7. Push ครั้งแรก
git push -u origin master
```

---

## 📝 การทำงานประจำวัน (Daily Workflow)

### 1. ตรวจสอบสถานะ
```bash
# ดูไฟล์ที่เปลี่ยนแปลง
git status

# ดูการแก้ไขโดยละเอียด
git diff                    # ไฟล์ที่ยังไม่ add
git diff --staged           # ไฟล์ที่ add แล้ว
```

### 2. เพิ่มไฟล์เข้า Staging
```bash
# เพิ่มทุกไฟล์
git add .

# เพิ่มเฉพาะไฟล์/โฟลเดอร์
git add itx_moduler/
git add itx_moduler/models/itx_moduler_module.py

# เพิ่มเฉพาะไฟล์ที่แก้ไข (ไม่รวมไฟล์ใหม่)
git add -u
```

### 3. Commit (บันทึกการเปลี่ยนแปลง)
```bash
# Commit แบบสั้น (1 บรรทัด)
git commit -m "fix: แก้บัค Python Constraints"

# Commit แบบมี description
git commit -m "$(cat <<'EOF'
feat: เพิ่มฟีเจอร์ import Python Constraints

- เพิ่มการ import จาก model registry
- ดึง source code ด้วย inspect.getsource()
- บันทึกลง itx.moduler.server.constraint
EOF
)"

# Commit แบบละเอียด (เปิด editor)
git commit
# (จะเปิด editor ให้พิมพ์ commit message)
```

### 4. Push ขึ้น GitHub
```bash
# Push (ครั้งแรกใช้ -u)
git push -u origin master

# ครั้งต่อไปใช้แค่
git push
```

### 5. Pull จาก GitHub (ดึงการเปลี่ยนแปลงล่าสุด)
```bash
# ดึงและ merge อัตโนมัติ
git pull

# หรือ ดึงและ rebase
git pull --rebase
```

---

## 📜 ดู History

```bash
# ดูประวัติแบบสั้น
git log --oneline

# ดูประวัติแบบละเอียด
git log

# ดูประวัติแบบ graph (สวยงาม)
git log --oneline --graph --all

# ดูประวัติเฉพาะไฟล์
git log itx_moduler/models/itx_moduler_module.py

# ดู commit ล่าสุด
git show

# ดู commit ที่เจาะจง
git show 82270d1
```

---

## 🔄 Undo / แก้ไข

### ยกเลิกการแก้ไขไฟล์ (ก่อน add)
```bash
# ยกเลิกการแก้ไขไฟล์เดียว (ระวัง! จะหายถาวร)
git checkout -- file.py

# ยกเลิกการแก้ไขทุกไฟล์
git checkout -- .
```

### ยกเลิกการ add (หลัง add แต่ก่อน commit)
```bash
# ยกเลิกการ add ไฟล์เดียว
git reset HEAD file.py

# ยกเลิกการ add ทุกไฟล์
git reset HEAD .
```

### ยกเลิก Commit
```bash
# ยกเลิก commit ล่าสุด (เก็บการแก้ไขไว้)
git reset --soft HEAD~1

# ยกเลิก commit ล่าสุด (ลบการแก้ไข - ระวัง!)
git reset --hard HEAD~1

# แก้ไข commit message ล่าสุด
git commit --amend -m "commit message ใหม่"
```

---

## 🌿 Branch (แยกงาน)

```bash
# ดู branch ทั้งหมด
git branch
git branch -a              # รวม remote branches

# สร้าง branch ใหม่
git branch feature/new-feature

# เปลี่ยนไปใช้ branch
git checkout feature/new-feature

# สร้างและเปลี่ยนไปใช้ทันที
git checkout -b fix/bug-123

# Merge branch กลับเข้า master
git checkout master
git merge feature/new-feature

# ลบ branch
git branch -d feature/new-feature
git branch -D feature/new-feature  # บังคับลบ
```

---

## 🔗 Remote (GitHub/GitLab)

```bash
# ดู remote ที่เชื่อมต่อ
git remote -v

# เพิ่ม remote
git remote add origin https://github.com/user/repo.git

# เปลี่ยน URL ของ remote
git remote set-url origin https://TOKEN@github.com/user/repo.git

# ลบ remote
git remote remove origin
```

---

## 🛠️ คำสั่งอื่นๆ ที่มีประโยชน์

```bash
# ดู config ทั้งหมด
git config --list

# ตั้งชื่อและอีเมล
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# ดูขนาด repository
git count-objects -vH

# ทำความสะอาด (ลบไฟล์ที่ไม่ track)
git clean -fd              # ลบไฟล์และโฟลเดอร์
git clean -fdn             # ดูว่าจะลบอะไรบ้าง (ไม่ลบจริง)

# Stash (เก็บการแก้ไขไว้ชั่วคราว)
git stash                  # เก็บ
git stash list             # ดูรายการ
git stash pop              # นำกลับมาใช้
git stash drop             # ลบทิ้ง
```

---

## 📖 Commit Message Best Practices

### รูปแบบที่แนะนำ:
```
<type>: <subject>

<body>

<footer>
```

### Types:
- `feat`: ฟีเจอร์ใหม่
- `fix`: แก้บัค
- `docs`: เอกสาร
- `style`: จัด format code (ไม่เปลี่ยนลอจิก)
- `refactor`: ปรับโครงสร้างโค้ด
- `test`: เพิ่ม/แก้ test
- `chore`: งานบ้านงานครัว (build, dependencies)
- `perf`: ปรับปรุงประสิทธิภาพ

### ตัวอย่าง:
```bash
git commit -m "feat: เพิ่มระบบ import Python Constraints"
git commit -m "fix: แก้ไข Groups หายหลัง uninstall"
git commit -m "docs: อัปเดตเอกสาร README"
git commit -m "refactor: ปรับโครงสร้าง action_import_snapshots"
```

---

## 🎯 Workflow ที่แนะนำ

### การแก้ไขโค้ดปกติ:
```bash
# 1. ตรวจสอบสถานะ
git status

# 2. ดูการเปลี่ยนแปลง
git diff

# 3. Add และ Commit
git add .
git commit -m "fix: แก้บัค XYZ"

# 4. Push
git push
```

### การทำฟีเจอร์ใหม่ (ใช้ branch):
```bash
# 1. สร้าง branch ใหม่
git checkout -b feature/new-thing

# 2. แก้ไขโค้ด
# ... edit files ...

# 3. Commit
git add .
git commit -m "feat: เพิ่มฟีเจอร์ ABC"

# 4. Push branch
git push -u origin feature/new-thing

# 5. เมื่อเสร็จแล้ว merge กลับ master
git checkout master
git merge feature/new-thing
git push

# 6. ลบ branch
git branch -d feature/new-thing
```

---

## 💡 Tips & Tricks

### 1. Alias (ลัดคำสั่ง)
```bash
# ตั้ง alias
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.lg "log --oneline --graph --all"

# ใช้งาน
git st        # แทน git status
git lg        # แทน git log --oneline --graph --all
```

### 2. .gitignore ตัวอย่าง
```
# Python
__pycache__/
*.py[cod]
*.so

# Odoo
*.pyc
*.pyo

# Backups
*.tar.gz
*.zip
backups/

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

### 3. ดู commit ที่ยังไม่ push
```bash
git log origin/master..HEAD
```

### 4. ค้นหา commit ที่มีคำว่า "bug"
```bash
git log --grep="bug"
```

### 5. ดูว่าใครแก้บรรทัดไหน
```bash
git blame file.py
```

---

## 🆘 แก้ปัญหาที่พบบ่อย

### 1. Merge Conflict
```bash
# เมื่อเจอ conflict ขณะ pull/merge:
# 1. เปิดไฟล์ที่ conflict แก้ไข
# 2. หาส่วนที่ขัดแย้ง:
#    <<<<<<< HEAD
#    โค้ดของคุณ
#    =======
#    โค้ดจาก remote
#    >>>>>>>
# 3. แก้ไขให้ถูกต้อง ลบ marker ทิ้ง
# 4. Add และ commit
git add .
git commit -m "fix: แก้ merge conflict"
```

### 2. Push ถูกปฏิเสธ (remote มีการเปลี่ยนแปลง)
```bash
# ต้อง pull ก่อน
git pull --rebase
git push
```

### 3. Commit ผิดไฟล์
```bash
# ยกเลิก commit ล่าสุด แต่เก็บการแก้ไข
git reset --soft HEAD~1

# แก้ไข add เฉพาะไฟล์ที่ต้องการ
git add correct_file.py

# Commit ใหม่
git commit -m "fix: แก้ถูกต้อง"
```

---

## 📚 คำสั่งที่ใช้ใน Session นี้

```bash
# 1. Setup repository
cd /home/chainarp/PycharmProjects/odoo19/custom_addons
git init

# 2. สร้าง .gitignore
nano .gitignore

# 3. Add files
git add .

# 4. Commit
git commit -m "feat: Snapshot Architecture implementation..."

# 5. เชื่อม GitHub
git remote add origin https://github.com/chainarp/odoo19-custom-addons.git

# 6. อัปเดต remote URL ด้วย token
git remote set-url origin https://TOKEN@github.com/chainarp/odoo19-custom-addons.git

# 7. Push
git push -u origin master

# 8. ดู history
git log --oneline --graph --all
```

---

**เขียนโดย:** Claude Code
**วันที่:** 2025-12-22
**สำหรับ:** ITX Custom Addons Development

สามารถกลับมาดูไฟล์นี้ได้ทุกเมื่อครับ! 🚀
