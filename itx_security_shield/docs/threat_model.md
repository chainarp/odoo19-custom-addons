# Threat Scenarios: วิธีที่ลูกค้าอาจขโมย Addon

## Scenario 1: Copy Files ไปเครื่องอื่น
```
ลูกค้า A (จ่ายเงิน):
  Server A → มี itx_helloworld + license.lic

ลูกค้า B (ไม่จ่ายเงิน):
  1. ขอ source code จากลูกค้า A
  2. Copy addon ไปติดตั้งบน Server B
  3. ใช้งานฟรี ❌
```

## Scenario 2: Backup Database แล้ว Restore
```
ลูกค้า A:
  1. Backup Odoo database (มี addon ติดตั้งแล้ว)
  2. ขาย/แจก backup ให้คนอื่น
  3. คนอื่น restore → ใช้ addon ฟรี ❌
```

## Scenario 3: Clone VM/Container
```
ลูกค้า A:
  1. Clone entire VM/Docker container
  2. Run บนเครื่องใหม่
  3. Addon ทำงาน (ถ้าไม่มีการป้องกัน) ❌
```

## Scenario 4: Reverse Engineer
```
ลูกค้า A:
  1. อ่าน Python source code
  2. เข้าใจ business logic
  3. เขียนใหม่เอง
  4. ใช้ฟรี ❌
```

## Scenario 5: Share License File
```
ลูกค้า A:
  1. มี license.lic (ถูกต้อง)
  2. แชร์ license file ให้คนอื่น
  3. คนอื่นเอาไปใช้ ❌
```

## Scenario 6: Crack/Bypass License Check
```
ลูกค้า A:
  1. แก้ไข license check code
  2. Bypass validation
  3. ใช้งานโดยไม่มี license ❌
```

