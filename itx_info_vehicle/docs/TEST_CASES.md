# Test Cases - ITX Info Vehicle

**Document Type:** Test Data Documentation
**Created:** 2026-03-31
**Purpose:** อธิบาย test cases ที่สร้างเพื่อแสดงการออกแบบระบบ

---

## 1. Vehicle Variants (10 Records)

### 1.1 Toyota Hilux Vigo - แสดง: 1 Generation มีหลาย Body Type

| Variant | Body Type | Engine | Transmission | Drive |
|---------|-----------|--------|--------------|-------|
| Vigo 3.0 G Double Cab | **Double Cab** | 1KD-FTV (3.0L) | Auto | 4WD |
| Vigo 2.5 E Double Cab | **Double Cab** | 2KD-FTV (2.5L) | Manual | RWD |
| Vigo 2.5 E Extra Cab | **Extra Cab** | 2KD-FTV (2.5L) | Manual | RWD |
| Vigo 2.5 J Single Cab | **Single Cab** | 2KD-FTV (2.5L) | Manual | RWD |

**Design Point:** Generation เดียวกัน (Vigo Gen 2 Champ) มี 3 body types ต่างกัน

### 1.2 Toyota Fortuner - แสดง: SUV ทุก variant เป็น body เดียวกัน

| Variant | Body Type | Engine | Transmission | Drive |
|---------|-----------|--------|--------------|-------|
| Fortuner 2.8 V 4WD | SUV | 1GD-FTV (2.8L) | Auto | 4WD |
| Fortuner 2.4 G | SUV | 2GD-FTV (2.4L) | Auto | RWD |

**Design Point:** SUV ทุก variant ใช้ body type เดียวกัน

### 1.3 Honda Civic FD - แสดง: รถเก๋ง + เครื่อง Honda

| Variant | Body Type | Engine | Transmission | Drive |
|---------|-----------|--------|--------------|-------|
| Civic 1.8 S i-VTEC | Sedan | R18A (1.8L) | Auto | FWD |
| Civic 1.8 E i-VTEC | Sedan | R18A (1.8L) | Auto | FWD |
| Civic 2.0 EL i-VTEC | Sedan | K20A (2.0L) | Auto | FWD |

**Design Point:** รถเก๋ง Sedan + engine lookup จาก mgr.engine

### 1.4 Isuzu D-Max Gen 3 - แสดง: รถกระบะ Isuzu

| Variant | Body Type | Engine | Transmission | Drive |
|---------|-----------|--------|--------------|-------|
| D-Max 1.9 V-Cross 4WD | Double Cab | RZ4E (1.9L) | Auto | 4WD |
| D-Max 3.0 Hi-Lander | Extra Cab | 4JJ1 (3.0L) | Auto | RWD |

**Design Point:** แบรนด์อื่น + engine lookup

---

## 2. Demo Vehicle Parts (16 Records)

### Test Case 1: ซ้าย/ขวา ต่างกัน

**Design Point:** `name` เป็นส่วนหนึ่งของ unique key

| Part | Name | Origin | Condition | OEM Part No | Price |
|------|------|--------|-----------|-------------|-------|
| ไฟหน้า Vigo | **ไฟหน้าซ้าย** | OEM | Like New | 81170-0K440 | 4,500 |
| ไฟหน้า Vigo | **ไฟหน้าขวา** | OEM | Like New | 81130-0K440 | 4,500 |

**ผลลัพธ์:** 2 records ต่างกัน เพราะ `name` ต่างกัน (ซ้าย vs ขวา)

---

### Test Case 2: Condition ต่างกัน = ราคาต่างกัน

**Design Point:** `condition` เป็นส่วนหนึ่งของ unique key + กำหนดราคา

| Part | Name | Origin | Condition | Price | หมายเหตุ |
|------|------|--------|-----------|-------|---------|
| กันชนหน้า Vigo | กันชนหน้า | OEM | **Like New** | **8,500** | สภาพดีมาก |
| กันชนหน้า Vigo | กันชนหน้า | OEM | **Good** | **5,500** | ใช้งานได้ดี |
| กันชนหน้า Vigo | กันชนหน้า | OEM | **Fair** | **2,500** | ต้องซ่อม |

**ผลลัพธ์:** 3 records ต่างกัน เพราะ `condition` ต่างกัน → ราคาต่างกัน

---

### Test Case 3: Part Origin ต่างกัน (OEM vs Aftermarket)

**Design Point:** `part_origin` เป็นส่วนหนึ่งของ unique key + กำหนดราคา

| Part | Name | Origin | Condition | Price | หมายเหตุ |
|------|------|--------|-----------|-------|---------|
| หน้ากระจัง Vigo | หน้ากระจังตัวนอก | **OEM** | Like New | **3,200** | แท้ |
| หน้ากระจัง Vigo | หน้ากระจังตัวนอก | **Aftermarket** | New | **950** | เทียม |

**ผลลัพธ์:** 2 records ต่างกัน เพราะ `origin` ต่างกัน → ราคาต่างกันมาก

---

### Test Case 4: ไม่มี OEM Part Number (NULL)

**Design Point:** `oem_part_number` เป็น optional - พนักงานกรอกทีหลังได้

| Part | Name | Origin | Condition | OEM Part No | Price |
|------|------|--------|-----------|-------------|-------|
| กระจกมองข้าง Vigo | กระจกมองข้างซ้าย | OEM | Good | **(ว่าง)** | 1,800 |
| กระจกมองข้าง Vigo | กระจกมองข้างขวา | OEM | Good | **(ว่าง)** | 1,800 |

**ผลลัพธ์:** สร้าง record ได้โดยไม่ต้องกรอก OEM Part No → เติมทีหลัง

---

### Test Case 5: Body Type เฉพาะ

**Design Point:** อะไหล่บางชิ้นใช้ได้เฉพาะ body type บางประเภท

| Part | Name | Variant (Body Type) | หมายเหตุ |
|------|------|---------------------|---------|
| ประตูแคป Vigo | ประตูแคปซ้าย | Vigo 2.5E **Extra Cab** | เฉพาะ Extra Cab เท่านั้น |
| ฝาท้ายกระบะ Vigo | ฝาปิดท้ายกระบะ | Vigo 2.5J **Single Cab** | เฉพาะ Pickup |

**ผลลัพธ์:** แสดงว่า variant (+ body_type) สำคัญสำหรับอะไหล่บางชิ้น

---

### Test Case 6: รถ Sedan (Honda Civic FD)

**Design Point:** แสดงอะไหล่รถเก๋ง + เครื่อง Honda

| Part | Name | Vehicle | Engine | Price |
|------|------|---------|--------|-------|
| ฝากระโปรง Civic | ฝากระโปรงหน้า | Civic FD 1.8S | R18A | 7,500 |
| ไฟท้าย Civic | ไฟท้ายซ้าย | Civic FD 1.8S | R18A | 2,800 |

---

### Test Case 7: รถ SUV (Toyota Fortuner)

**Design Point:** แสดงอะไหล่ SUV

| Part | Name | Vehicle | Engine | Price |
|------|------|---------|--------|-------|
| กันชนหลัง Fortuner | กันชนหลัง | Fortuner 2.8V | 1GD-FTV | 9,500 |

---

### Test Case 8: ชิ้นส่วนใหญ่ (เครื่องยนต์/เกียร์)

**Design Point:** อะไหล่ราคาสูง + engine_id

| Part | Name | Vehicle | Category | Price |
|------|------|---------|----------|-------|
| เครื่อง Vigo | เครื่องยนต์ 1KD-FTV ทั้งลูก | Vigo 3.0G | เครื่องยนต์ทั้งลูก | 85,000 |
| เกียร์ Civic | เกียร์ออโต้ทั้งลูก | Civic FD 1.8S | เกียร์ออโต้ | 35,000 |

---

## 3. Unique Key Summary

```
Unique Key = variant_id + part_category_id + name + part_origin + condition + oem_part_number
```

| Field | Required | ตัวอย่างที่แสดง |
|-------|----------|----------------|
| `itx_variant_id` | ✅ | Test Case 5, 6, 7 |
| `itx_part_category_id` | ✅ | ทุก test case |
| `name` | ✅ | **Test Case 1** (ซ้าย/ขวา) |
| `itx_part_origin` | ✅ | **Test Case 3** (OEM/Aftermarket) |
| `itx_condition` | ✅ | **Test Case 2** (Like New/Good/Fair) |
| `itx_oem_part_number` | ❌ Optional | **Test Case 4** (NULL ได้) |

---

## 4. Price Matrix Example

### กันชนหน้า Vigo Champ

| Origin | Condition | Price | Cost |
|--------|-----------|-------|------|
| OEM | Like New | 8,500 | 4,500 |
| OEM | Good | 5,500 | 2,800 |
| OEM | Fair | 2,500 | 1,000 |
| Aftermarket | New | 1,500 | 700 |

**สูตรราคา:** OEM + Like New = ราคาสูงสุด, Aftermarket + Fair = ราคาต่ำสุด

---

## 5. Workflow ตัวอย่าง

### Workflow: รับซากรถ Vigo Champ เข้าคลัง

```
1. พนักงานรับซากรถ Vigo Champ 3.0G Double Cab ปี 2010

2. แกะอะไหล่ทีละชิ้น:

   ชิ้นที่ 1: ไฟหน้าซ้าย
   - name: "ไฟหน้าซ้าย" ✅ (รู้ทันที)
   - variant: Vigo 3.0G Double Cab ✅
   - category: ไฟหน้า ✅
   - origin: OEM ✅
   - condition: Like New ✅ (ดูสภาพ)
   - OEM Part No: (ว่างไว้ก่อน)
   → สร้าง Product ได้เลย!

   ชิ้นที่ 2: กันชนหน้า
   - name: "กันชนหน้า" ✅
   - variant: Vigo 3.0G Double Cab ✅
   - category: กันชนหน้า ✅
   - origin: OEM ✅
   - condition: Good ✅ (มีรอยขีดข่วนเล็กน้อย)
   → สร้าง Product ได้เลย!

3. ทีหลัง (มีเวลา):
   - เปิดหนังสืออะไหล่
   - เติม OEM Part Number
```

---

*Document created: 2026-03-31*
