# License Data Fields - Current vs Recommended

## Executive Summary

คำถาม: **"ใครของ ITX คือคน install addon ให้ลูกค้า"**

นี่คือข้อมูลสำคัญมากที่ขาดไปในโครงสร้าง license ปัจจุบัน ผมวิเคราะห์และพบว่ามีข้อมูลหลายอย่างที่ควรเพิ่มเพื่อ:

1. **Audit Trail** - รู้ว่าใครทำอะไร เมื่อไหร่
2. **Customer Support** - ติดต่อใครเมื่อมีปัญหา
3. **Business Intelligence** - วิเคราะห์ยอดขาย, ลูกค้า
4. **Compliance** - ตามกฎหมาย PDPA, GDPR
5. **Security** - ตรวจสอบการเข้าถึงที่ผิดปกติ

---

## 1. โครงสร้างปัจจุบัน (Current Structure)

### ✅ มีอยู่แล้ว (Already Implemented)

```python
@dataclass
class LicenseData:
    # ========================================================================
    # Customer Information
    # ========================================================================
    customer_name: str                 # ✅ ชื่อลูกค้า
    po_number: str = ""                # ✅ เลข PO
    contract_number: str = ""          # ✅ เลขสัญญา
    contact_email: str = ""            # ✅ อีเมล์ติดต่อ
    contact_phone: str = ""            # ✅ เบอร์โทรติดต่อ

    # ========================================================================
    # License Rights
    # ========================================================================
    licensed_addons: List[str]         # ✅ Addons ที่มีสิทธิ์
    max_instances: int = 1             # ✅ จำนวนเครื่องที่ติดตั้งได้
    concurrent_users: int = 0          # ✅ จำนวน user พร้อมกัน (0 = unlimited)

    # ========================================================================
    # Hardware Binding
    # ========================================================================
    registered_instances: List[Dict]   # ✅ เครื่องที่ติดตั้งแล้ว
        # - instance_id
        # - hardware_fingerprint
        # - machine_id
        # - hostname
        # - registered_date
        # - last_seen
        # - status

    # ========================================================================
    # Dates & Validity
    # ========================================================================
    issue_date: str                    # ✅ วันที่ออก license
    expiry_date: str                   # ✅ วันหมดอายุ
    grace_period_days: int = 30        # ✅ ระยะผ่อนผันหลังหมดอายุ
    maintenance_until: str = ""        # ✅ วันหมดอายุ maintenance

    # ========================================================================
    # License Metadata
    # ========================================================================
    license_version: str = "1.0"       # ✅ เวอร์ชัน license format
    license_type: str                  # ✅ commercial, trial, educational, development
    license_tier: str = "standard"     # ✅ starter, standard, professional, enterprise
    features: List[str]                # ✅ features พิเศษ

    # ========================================================================
    # Restrictions & Limits
    # ========================================================================
    max_database_size_gb: int = 0      # ✅ ขนาด DB สูงสุด (0 = unlimited)
    max_records_per_model: int = 0     # ✅ จำนวน records สูงสุด
    allowed_ip_ranges: List[str]       # ✅ IP ranges ที่อนุญาต

    # ========================================================================
    # Support & Updates
    # ========================================================================
    support_level: str = "standard"    # ✅ ระดับการ support
    support_email: str                 # ✅ อีเมล์ติดต่อ support
    update_url: str                    # ✅ URL สำหรับ update

    # ========================================================================
    # File Integrity
    # ========================================================================
    file_hashes: Dict[str, str]        # ✅ Hash ของไฟล์ (สำหรับ integrity check)

    # ========================================================================
    # Digital Signature
    # ========================================================================
    signature: str = ""                # ✅ Digital signature
    signature_algorithm: str           # ✅ อัลกอริทึมที่ใช้
```

### จุดแข็งของโครงสร้างปัจจุบัน:
- ✅ ครอบคลุมข้อมูลพื้นฐานครบถ้วน
- ✅ มี hardware binding สำหรับ multi-instance
- ✅ มีข้อมูล expiry และ grace period
- ✅ มี digital signature
- ✅ มี restrictions (DB size, IP ranges)

---

## 2. ข้อมูลที่ขาดหายไป (Missing Critical Fields)

### ❌ Priority 1: Audit Trail & Personnel (สำคัญมาก!)

**ปัญหา:** ไม่รู้ว่า **ใคร** เป็นคนทำอะไร

```python
# ❌ ข้อมูลเหล่านี้ไม่มีในโครงสร้างปัจจุบัน

# License Issuance (ใครเป็นคนสร้าง license?)
issued_by: str = ""                    # ❌ ชื่อพนักงาน ITX ที่สร้าง license
issued_by_email: str = ""              # ❌ อีเมล์พนักงาน
issued_by_employee_id: str = ""        # ❌ รหัสพนักงาน
issued_from_ip: str = ""               # ❌ IP ที่สร้าง license
issued_from_location: str = ""         # ❌ สถานที่ (Bangkok Office, Remote, etc.)

# Installation Personnel (ใครเป็นคนติดตั้ง? ← คำถามของคุณ!)
installed_by: str = ""                 # ❌ ชื่อพนักงาน/ช่าง ITX ที่ติดตั้ง
installed_by_email: str = ""           # ❌ อีเมล์ช่างติดตั้ง
installed_by_phone: str = ""           # ❌ เบอร์โทรช่างติดตั้ง
installation_date: str = ""            # ❌ วันที่ติดตั้งจริง (อาจต่างจาก issue_date)
installation_location: str = ""        # ❌ สถานที่ติดตั้ง (ที่ลูกค้า)
installation_notes: str = ""           # ❌ หมายเหตุการติดตั้ง

# X.509 Certificate Info (ถ้าใช้ cert signing)
signing_certificate_cn: str = ""       # ❌ CN จาก certificate (somchai@itx.local)
signing_certificate_serial: str = ""   # ❌ Serial number ของ cert
signing_timestamp: str = ""            # ❌ เวลาที่เซ็น (RFC3339 format)
```

**ทำไมสำคัญ?**
- 🔍 **Audit Trail:** รู้ว่าใครทำอะไร เมื่อไหร่ (สำคัญมากสำหรับองค์กร)
- 🛡️ **Security:** ตรวจจับการสร้าง license ที่ไม่ได้รับอนุญาต
- 📞 **Support:** ติดต่อช่างติดตั้งได้เลยเมื่อลูกค้ามีปัญหา
- 📊 **Performance Review:** ประเมินผลงานพนักงานแต่ละคน (ติดตั้งกี่ license, มีปัญหามั๊ย)
- ⚖️ **Legal:** หลักฐานในกรณีพิพาท (ใครเป็นคนติดตั้ง, เมื่อไหร่)

### ❌ Priority 2: Sales & Business Information

```python
# Sales Information
sales_person: str = ""                 # ❌ ชื่อ sales ที่ดูแลลูกค้า
sales_email: str = ""                  # ❌ อีเมล์ sales
sales_phone: str = ""                  # ❌ เบอร์โทร sales
sales_team: str = ""                   # ❌ ทีม sales (Bangkok, Chiang Mai, etc.)
sales_commission: float = 0.0          # ❌ Commission (ถ้าต้องการ)

# Reseller/Partner Information
reseller_name: str = ""                # ❌ ชื่อ reseller/partner (ถ้ามี)
reseller_contact: str = ""             # ❌ ผู้ติดต่อ reseller
reseller_email: str = ""               # ❌ อีเมล์ reseller
reseller_commission: float = 0.0       # ❌ Commission ของ reseller

# Financial Information
license_price: float = 0.0             # ❌ ราคา license
currency: str = "THB"                  # ❌ สกุลเงิน
payment_status: str = ""               # ❌ paid, pending, partial
payment_date: str = ""                 # ❌ วันที่จ่ายเงิน
invoice_number: str = ""               # ❌ เลขใบแจ้งหนี้
```

**ทำไมสำคัญ?**
- 💰 **Revenue Tracking:** ติดตามรายได้แต่ละ license
- 📊 **Sales Analytics:** วิเคราะห์ว่า sales คนไหนขายได้เยอะสุด
- 🤝 **Partner Management:** จัดการ reseller/partner
- 🧾 **Financial Audit:** เชื่อมโยงกับระบบบัญชี

### ❌ Priority 3: Customer Deployment Details

```python
# Deployment Environment
deployment_environment: str = ""       # ❌ production, staging, development, testing, demo
deployment_location: str = ""          # ❌ Thailand, Singapore, USA, etc.
deployment_region: str = ""            # ❌ Asia-Pacific, Europe, Americas
deployment_notes: str = ""             # ❌ หมายเหตุการ deploy
customer_server_hostname: str = ""     # ❌ ชื่อเซิร์ฟเวอร์ลูกค้า
customer_db_name: str = ""             # ❌ ชื่อ database
customer_odoo_version: str = ""        # ❌ Odoo version (19.0, 18.0, etc.)
customer_industry: str = ""            # ❌ อุตสาหกรรม (Manufacturing, Retail, etc.)
customer_company_size: str = ""        # ❌ ขนาดบริษัท (SME, Enterprise)
```

**ทำไมสำคัญ?**
- 🌍 **Geographic Analytics:** รู้ว่ามีลูกค้าในประเทศไหนบ้าง
- 🏭 **Industry Insights:** เข้าใจ use case แต่ละอุตสาหกรรม
- 🔧 **Technical Support:** รู้ว่าลูกค้าใช้ Odoo version อะไร (สำคัญตอน debug)
- 📈 **Market Segmentation:** วิเคราะห์ตลาด

### ❌ Priority 4: Compliance & Legal

```python
# Legal & Compliance
terms_accepted_date: str = ""          # ❌ วันที่ลูกค้ายอมรับข้อตกลง
terms_version: str = ""                # ❌ เวอร์ชันของข้อตกลง (v1.0, v2.0)
gdpr_compliant: bool = False           # ❌ สำหรับลูกค้า EU
pdpa_compliant: bool = False           # ❌ สำหรับลูกค้าไทย
data_residency_region: str = ""        # ❌ ข้อมูลต้องเก็บในภูมิภาคไหน
export_restrictions: List[str] = []    # ❌ ข้อจำกัดการส่งออก (สำหรับบางประเทศ)
compliance_notes: str = ""             # ❌ หมายเหตุด้านกฎหมาย
```

**ทำไมสำคัญ?**
- ⚖️ **Legal Protection:** ป้องกันปัญหาทางกฎหมาย
- 🇪🇺 **GDPR Compliance:** บังคับสำหรับลูกค้า EU
- 🇹🇭 **PDPA Compliance:** กฎหมายคุ้มครองข้อมูลไทย
- 🌏 **Data Residency:** บางประเทศห้ามเก็บข้อมูลข้ามประเทศ

### ❌ Priority 5: Activation & Usage History

```python
# Activation History
first_activation_date: str = ""        # ❌ วันที่ activate ครั้งแรก
last_activation_date: str = ""         # ❌ วันที่ activate ล่าสุด
activation_count: int = 0              # ❌ จำนวนครั้งที่ activate
last_validation_date: str = ""         # ❌ วันที่ validate ล่าสุด
validation_count: int = 0              # ❌ จำนวนครั้งที่ validate
last_heartbeat: str = ""               # ❌ วันเวลาที่ส่ง heartbeat ล่าสุด

# Usage Statistics (Optional - ถ้าต้องการ)
total_login_count: int = 0             # ❌ จำนวนครั้งที่ login
last_login_date: str = ""              # ❌ วันที่ login ล่าสุด
active_users_count: int = 0            # ❌ จำนวน active users ปัจจุบัน
database_size_mb: int = 0              # ❌ ขนาด database ปัจจุบัน
```

**ทำไมสำคัญ?**
- 📊 **Usage Analytics:** รู้ว่าลูกค้าใช้งานมากน้อยแค่ไหน
- 🚨 **Anomaly Detection:** ตรวจจับการใช้งานที่ผิดปกติ
- 💡 **Customer Health Score:** ประเมินว่าลูกค้ามีแนวโน้มต่ออายุมั๊ย
- 🎯 **Upsell Opportunities:** ลูกค้าใช้งานเกิน limit → เสนอ upgrade

### ❌ Priority 6: Customization & Integration

```python
# Customization Information
custom_modules: List[str] = []         # ❌ Modules ที่ customize พิเศษสำหรับลูกค้า
customization_level: str = ""          # ❌ none, light, moderate, heavy
customization_notes: str = ""          # ❌ รายละเอียดการ customize
customization_version: str = ""        # ❌ เวอร์ชันของ customization
customization_developer: str = ""      # ❌ developer ที่ทำ customization

# Integration Information
integrated_systems: List[str] = []     # ❌ ระบบที่ integrate (SAP, Salesforce, etc.)
integration_notes: str = ""            # ❌ รายละเอียดการ integrate
api_enabled: bool = False              # ❌ เปิดใช้ API มั๊ย
webhook_urls: List[str] = []           # ❌ Webhook URLs (ถ้ามี)
```

**ทำไมสำคัญ?**
- 🔧 **Technical Support:** รู้ว่าลูกค้ามีการ customize อะไรบ้าง
- 🔗 **Integration Support:** รู้ว่า integrate กับระบบไหน (ตอน troubleshoot)
- 📚 **Knowledge Base:** สร้าง knowledge base จาก customization patterns
- 💰 **Upsell:** เสนอ custom module ใหม่

### ❌ Priority 7: Technical Limits (เพิ่มเติม)

```python
# Advanced Limits
max_storage_gb: int = 0                # ❌ พื้นที่เก็บข้อมูลสูงสุด (0 = unlimited)
max_api_calls_per_day: int = 0         # ❌ จำนวน API calls ต่อวัน
max_email_sends_per_day: int = 0       # ❌ จำนวนอีเมล์ส่งได้ต่อวัน
max_report_exports_per_month: int = 0  # ❌ จำนวน report exports ต่อเดือน
max_sms_sends_per_month: int = 0       # ❌ จำนวน SMS ต่อเดือน
max_backup_count: int = 0              # ❌ จำนวน backup files ที่เก็บได้
bandwidth_limit_gb_per_month: int = 0  # ❌ Bandwidth สูงสุดต่อเดือน
```

**ทำไมสำคัญ?**
- 💸 **Cost Control:** จำกัดการใช้งานที่ทำให้เกิดค่าใช้จ่าย (API calls, SMS, email)
- ⚡ **Performance:** ป้องกันการใช้งานมากเกินไป
- 📊 **Tiered Pricing:** แยก tier ตาม usage limits

### ❌ Priority 8: Change History & Versioning

```python
# Change History
modification_history: List[Dict] = []  # ❌ ประวัติการแก้ไข license
    # - modified_date
    # - modified_by
    # - changes (what changed)
    # - reason
    # - approved_by
last_modified_by: str = ""             # ❌ ใครแก้ล่าสุด
last_modified_date: str = ""           # ❌ วันที่แก้ล่าสุด
license_renewal_count: int = 0         # ❌ จำนวนครั้งที่ต่ออายุ
previous_license_id: str = ""          # ❌ ID ของ license ก่อนหน้า (ถ้ามี)
```

**ทำไมสำคัญ?**
- 📜 **Audit Trail:** รู้ว่า license เปลี่ยนแปลงอะไรบ้าง
- 🔐 **Security:** ตรวจจับการแก้ไขที่ไม่ได้รับอนุญาต
- 📊 **Customer Journey:** ติดตาม lifecycle ของลูกค้า (trial → paid → renewal)

---

## 3. โครงสร้างใหม่ที่แนะนำ (Recommended Structure)

### 3.1 เพิ่มใน `license_format.py`

```python
#!/usr/bin/env python3
"""
ITX Security Shield - Enhanced License File Format
Version 2.0 with Audit Trail and Personnel Tracking
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime, date
import json


@dataclass
class PersonnelInfo:
    """Information about ITX personnel involved with license."""
    name: str                          # ชื่อพนักงาน
    email: str                         # อีเมล์
    employee_id: str = ""              # รหัสพนักงาน
    phone: str = ""                    # เบอร์โทร
    department: str = ""               # แผนก (Sales, Technical, Support)
    location: str = ""                 # สถานที่ทำงาน (Bangkok Office, Remote)

    def to_dict(self):
        return asdict(self)


@dataclass
class SalesInfo:
    """Sales and business information."""
    sales_person: PersonnelInfo = None
    reseller_name: str = ""
    reseller_contact: str = ""
    reseller_email: str = ""
    license_price: float = 0.0
    currency: str = "THB"
    payment_status: str = ""           # paid, pending, partial
    payment_date: str = ""
    invoice_number: str = ""
    sales_team: str = ""

    def to_dict(self):
        data = asdict(self)
        if self.sales_person:
            data['sales_person'] = self.sales_person.to_dict()
        return data


@dataclass
class DeploymentInfo:
    """Customer deployment environment details."""
    environment: str = ""              # production, staging, development, testing, demo
    location: str = ""                 # Thailand, Singapore, etc.
    region: str = ""                   # Asia-Pacific, Europe, Americas
    notes: str = ""
    server_hostname: str = ""
    db_name: str = ""
    odoo_version: str = ""
    industry: str = ""                 # Manufacturing, Retail, etc.
    company_size: str = ""             # SME, Enterprise

    def to_dict(self):
        return asdict(self)


@dataclass
class ComplianceInfo:
    """Legal and compliance information."""
    terms_accepted_date: str = ""
    terms_version: str = ""
    gdpr_compliant: bool = False
    pdpa_compliant: bool = False
    data_residency_region: str = ""
    export_restrictions: List[str] = field(default_factory=list)
    compliance_notes: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class UsageStats:
    """Usage statistics and activation history."""
    first_activation_date: str = ""
    last_activation_date: str = ""
    activation_count: int = 0
    last_validation_date: str = ""
    validation_count: int = 0
    last_heartbeat: str = ""
    total_login_count: int = 0
    last_login_date: str = ""
    active_users_count: int = 0
    database_size_mb: int = 0

    def to_dict(self):
        return asdict(self)


@dataclass
class TechnicalLimits:
    """Advanced technical usage limits."""
    max_storage_gb: int = 0
    max_api_calls_per_day: int = 0
    max_email_sends_per_day: int = 0
    max_report_exports_per_month: int = 0
    max_sms_sends_per_month: int = 0
    max_backup_count: int = 0
    bandwidth_limit_gb_per_month: int = 0

    def to_dict(self):
        return asdict(self)


@dataclass
class CustomizationInfo:
    """Customization and integration information."""
    custom_modules: List[str] = field(default_factory=list)
    customization_level: str = ""      # none, light, moderate, heavy
    customization_notes: str = ""
    customization_version: str = ""
    customization_developer: str = ""
    integrated_systems: List[str] = field(default_factory=list)
    integration_notes: str = ""
    api_enabled: bool = False
    webhook_urls: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class ChangeHistoryEntry:
    """Single change history entry."""
    modified_date: str
    modified_by: str
    changes: str                       # Description of changes
    reason: str
    approved_by: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class InstanceInfo:
    """Information about a registered instance."""
    instance_id: int
    hardware_fingerprint: str
    machine_id: str
    hostname: str
    registered_date: str
    last_seen: str
    status: str                        # active, inactive, revoked

    def to_dict(self):
        return asdict(self)


@dataclass
class LicenseData:
    """
    Enhanced license data structure with full audit trail.
    Version 2.0
    """

    # ========================================================================
    # Customer Information
    # ========================================================================
    customer_name: str
    po_number: str = ""
    contract_number: str = ""
    contact_email: str = ""
    contact_phone: str = ""

    # ========================================================================
    # License Rights
    # ========================================================================
    licensed_addons: List[str] = field(default_factory=list)
    max_instances: int = 1
    concurrent_users: int = 0

    # ========================================================================
    # Hardware Binding (Multi-Instance Support)
    # ========================================================================
    registered_instances: List[Dict] = field(default_factory=list)

    # ========================================================================
    # Dates & Validity
    # ========================================================================
    issue_date: str = ""
    expiry_date: str = ""
    grace_period_days: int = 30
    maintenance_until: str = ""

    # ========================================================================
    # License Metadata
    # ========================================================================
    license_version: str = "2.0"       # ← เปลี่ยนเป็น 2.0
    license_type: str = "commercial"
    license_tier: str = "standard"
    features: Dict = field(default_factory=dict)  # ← เปลี่ยนจาก List เป็น Dict

    # ========================================================================
    # Restrictions & Limits
    # ========================================================================
    max_database_size_gb: int = 0
    max_records_per_model: int = 0
    allowed_ip_ranges: List[str] = field(default_factory=list)

    # ========================================================================
    # Support & Updates
    # ========================================================================
    support_level: str = "standard"
    support_email: str = "support@itxcorp.com"
    update_url: str = "https://updates.itxcorp.com/"

    # ========================================================================
    # File Integrity (Optional - for Phase 2)
    # ========================================================================
    file_hashes: Dict[str, str] = field(default_factory=dict)

    # ========================================================================
    # Digital Signature
    # ========================================================================
    signature: str = ""
    signature_algorithm: str = "SHA256withRSA"

    # ========================================================================
    # ⭐ NEW: License Issuance Personnel (ใครสร้าง license)
    # ========================================================================
    issued_by: str = ""                # ชื่อพนักงาน ITX ที่สร้าง license
    issued_by_email: str = ""
    issued_by_employee_id: str = ""
    issued_from_ip: str = ""           # IP address ที่สร้าง license
    issued_from_location: str = ""     # Bangkok Office, Remote, etc.

    # ========================================================================
    # ⭐ NEW: Installation Personnel (ใครติดตั้ง - คำตอบสำหรับคำถามของคุณ!)
    # ========================================================================
    installed_by: str = ""             # ชื่อช่างติดตั้ง ITX
    installed_by_email: str = ""
    installed_by_phone: str = ""
    installation_date: str = ""        # วันที่ติดตั้งจริง
    installation_location: str = ""    # สถานที่ติดตั้ง (ที่ลูกค้า)
    installation_notes: str = ""       # หมายเหตุการติดตั้ง

    # ========================================================================
    # ⭐ NEW: X.509 Certificate Info (ถ้าใช้ cert signing)
    # ========================================================================
    signing_certificate_cn: str = ""   # Common Name จาก cert
    signing_certificate_serial: str = ""
    signing_timestamp: str = ""        # RFC3339 timestamp

    # ========================================================================
    # ⭐ NEW: Sales & Business Information
    # ========================================================================
    sales_info: Optional[Dict] = None  # SalesInfo.to_dict()

    # ========================================================================
    # ⭐ NEW: Deployment Information
    # ========================================================================
    deployment_info: Optional[Dict] = None  # DeploymentInfo.to_dict()

    # ========================================================================
    # ⭐ NEW: Compliance Information
    # ========================================================================
    compliance_info: Optional[Dict] = None  # ComplianceInfo.to_dict()

    # ========================================================================
    # ⭐ NEW: Usage Statistics
    # ========================================================================
    usage_stats: Optional[Dict] = None  # UsageStats.to_dict()

    # ========================================================================
    # ⭐ NEW: Technical Limits
    # ========================================================================
    technical_limits: Optional[Dict] = None  # TechnicalLimits.to_dict()

    # ========================================================================
    # ⭐ NEW: Customization Information
    # ========================================================================
    customization_info: Optional[Dict] = None  # CustomizationInfo.to_dict()

    # ========================================================================
    # ⭐ NEW: Change History & Versioning
    # ========================================================================
    modification_history: List[Dict] = field(default_factory=list)  # List of ChangeHistoryEntry
    last_modified_by: str = ""
    last_modified_date: str = ""
    license_renewal_count: int = 0
    previous_license_id: str = ""

    # ========================================================================
    # ⭐ NEW: Internal Notes (ไม่แสดงให้ลูกค้าเห็น)
    # ========================================================================
    internal_notes: str = ""           # หมายเหตุภายใน ITX
    risk_level: str = "low"            # low, medium, high (ความเสี่ยงของลูกค้า)
    customer_health_score: int = 0     # 0-100 (ประเมินสุขภาพลูกค้า)
    renewal_probability: int = 0       # 0-100 (โอกาสที่จะต่ออายุ)

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return asdict(self)

    def to_json(self):
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict):
        """Create LicenseData from dictionary."""
        # Handle registered_instances
        if 'registered_instances' in data and data['registered_instances']:
            instances = []
            for inst in data['registered_instances']:
                if isinstance(inst, dict):
                    instances.append(inst)
                else:
                    instances.append(inst.to_dict())
            data['registered_instances'] = instances

        # Handle nested objects (keep as dicts for now)
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str):
        """Create LicenseData from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    # ... (keep all existing validation methods)
```

---

## 4. ตัวอย่างการใช้งาน (Usage Example)

### 4.1 สร้าง License แบบเต็ม (Full License with All Fields)

```python
from license_format import (
    LicenseData, PersonnelInfo, SalesInfo, DeploymentInfo,
    ComplianceInfo, UsageStats, TechnicalLimits, CustomizationInfo
)

# Personnel: ใครสร้าง license
issued_by = PersonnelInfo(
    name="Somchai Tanasombat",
    email="somchai@itxcorp.com",
    employee_id="ITX-2024-001",
    phone="+66 81 234 5678",
    department="Technical",
    location="Bangkok Office"
)

# Sales Information
sales = SalesInfo(
    sales_person=PersonnelInfo(
        name="Sutida Wongsawat",
        email="sutida@itxcorp.com",
        employee_id="ITX-SALES-045",
        phone="+66 82 345 6789",
        department="Sales",
        location="Bangkok Office"
    ),
    reseller_name="",  # ไม่มี reseller
    license_price=150000.00,
    currency="THB",
    payment_status="paid",
    payment_date="2025-12-01",
    invoice_number="INV-2025-12-0001",
    sales_team="Bangkok SME Team"
)

# Deployment Information
deployment = DeploymentInfo(
    environment="production",
    location="Thailand",
    region="Asia-Pacific",
    server_hostname="odoo-prod-001.customer.com",
    db_name="customer_production",
    odoo_version="19.0",
    industry="Manufacturing",
    company_size="SME",
    notes="Customer has 3 factories in Thailand"
)

# Compliance
compliance = ComplianceInfo(
    terms_accepted_date="2025-12-01",
    terms_version="v2.0",
    gdpr_compliant=False,
    pdpa_compliant=True,
    data_residency_region="Thailand",
    compliance_notes="PDPA compliance verified"
)

# Technical Limits
tech_limits = TechnicalLimits(
    max_storage_gb=100,
    max_api_calls_per_day=10000,
    max_email_sends_per_day=500,
    max_report_exports_per_month=1000
)

# Customization
customization = CustomizationInfo(
    custom_modules=["itx_customer_barcode_scanner"],
    customization_level="light",
    customization_developer="Dev Team A",
    integrated_systems=["SAP ERP"],
    api_enabled=True
)

# Create full license
license_data = LicenseData(
    # Basic customer info
    customer_name="บริษัท ABC Manufacturing จำกัด",
    po_number="PO-2025-12345",
    contract_number="CNT-2025-001",
    contact_email="admin@abc-manufacturing.com",
    contact_phone="+66 2 123 4567",

    # License rights
    licensed_addons=["itx_helloworld", "itx_inventory", "itx_sales"],
    max_instances=3,
    concurrent_users=50,

    # Dates
    issue_date="2025-12-06",
    expiry_date="2026-12-06",
    grace_period_days=30,
    maintenance_until="2026-12-06",

    # License metadata
    license_type="commercial",
    license_tier="professional",

    # ⭐ NEW: Personnel tracking
    issued_by="Somchai Tanasombat",
    issued_by_email="somchai@itxcorp.com",
    issued_by_employee_id="ITX-2024-001",
    issued_from_ip="203.154.123.45",
    issued_from_location="Bangkok Office",

    installed_by="Apichart Techsupport",
    installed_by_email="apichart@itxcorp.com",
    installed_by_phone="+66 89 456 7890",
    installation_date="2025-12-10",
    installation_location="Customer Factory - Samut Prakan",
    installation_notes="Installed on customer VMware ESXi server. 3 instances setup completed.",

    # ⭐ NEW: X.509 signing info
    signing_certificate_cn="somchai@itx.local",
    signing_certificate_serial="1A2B3C4D5E6F",
    signing_timestamp="2025-12-06T14:30:00+07:00",

    # ⭐ NEW: Nested objects
    sales_info=sales.to_dict(),
    deployment_info=deployment.to_dict(),
    compliance_info=compliance.to_dict(),
    technical_limits=tech_limits.to_dict(),
    customization_info=customization.to_dict(),

    # ⭐ NEW: Internal notes
    internal_notes="Customer is VIP. Provide premium support.",
    risk_level="low",
    customer_health_score=85,
    renewal_probability=90,
)

# Generate license file
from license_crypto import save_license_file_hybrid
save_license_file_hybrid(
    license_data,
    "ABC_Manufacturing_license.lic",
    private_key_path="keys/private_dev.pem"
)

print("✅ License created with full audit trail!")
print(f"   Issued by: {license_data.issued_by}")
print(f"   Installed by: {license_data.installed_by}")
print(f"   Sales: {sales.sales_person.name}")
print(f"   Price: {sales.license_price} {sales.currency}")
```

---

## 5. Benefits Summary (ประโยชน์ที่ได้รับ)

### 5.1 Audit Trail & Security

✅ **รู้ว่าใครทำอะไร เมื่อไหร่**
- สร้าง license: ใคร, เมื่อไหร่, ที่ไหน, IP อะไร
- ติดตั้ง: ใคร, เมื่อไหร่, ที่ไหน
- Signed ด้วย cert อะไร (CN, Serial)

✅ **ตรวจจับการใช้งานที่ผิดปกติ**
- License ถูกสร้างจาก IP แปลก → เตือน
- พนักงาน A สร้าง license แต่ไม่มีสิทธิ์ → block

### 5.2 Customer Support

✅ **ติดต่อคนที่เกี่ยวข้องได้ทันที**
- ลูกค้ามีปัญหา → ติดต่อช่างติดตั้งได้เลย
- ลูกค้าถามเรื่องเงิน → ติดต่อ sales ได้เลย

✅ **ข้อมูลครบสำหรับการแก้ปัญหา**
- Odoo version อะไร
- Deploy ที่ไหน (production, staging)
- มี customization อะไรบ้าง

### 5.3 Business Intelligence

✅ **วิเคราะห์ยอดขาย**
- Sales คนไหนขายได้เยอะสุด
- Tier ไหนขายดีสุด (starter, professional, enterprise)
- ลูกค้าส่วนใหญ่อยู่ industry ไหน

✅ **Customer Health Tracking**
- ลูกค้าไหนมีโอกาสต่ออายุ
- ลูกค้าไหนใช้งานน้อย (risk of churn)
- ลูกค้าไหนเกิน limit (upsell opportunity)

### 5.4 Legal & Compliance

✅ **ป้องกันปัญหากฎหมาย**
- มีหลักฐานว่าลูกค้ายอมรับข้อตกลง
- Comply กับ PDPA (ไทย) และ GDPR (EU)
- Data residency ถูกต้องตามกฎหมาย

### 5.5 Performance & Cost Control

✅ **จำกัดการใช้งานที่ทำให้เกิดค่าใช้จ่าย**
- API calls สูงสุด 10,000 ครั้ง/วัน
- Email ส่งได้สูงสุด 500 ฉบับ/วัน
- Bandwidth สูงสุด 100GB/เดือน

---

## 6. Migration Plan (แผนการย้ายข้อมูล)

### 6.1 เวอร์ชัน 1.0 → 2.0

**ปัญหา:** License เก่าไม่มี field ใหม่

**วิธีแก้:**
```python
def migrate_license_v1_to_v2(old_license: LicenseData) -> LicenseData:
    """Migrate license from v1.0 to v2.0 format"""

    # Copy all existing fields
    new_data = old_license.to_dict()

    # Add new fields with default values
    new_data.update({
        'license_version': '2.0',

        # Personnel (ไม่ทราบ → ใส่ "Unknown")
        'issued_by': 'Unknown (migrated from v1.0)',
        'issued_by_email': '',
        'issued_by_employee_id': '',
        'issued_from_ip': '',
        'issued_from_location': '',

        'installed_by': 'Unknown (migrated from v1.0)',
        'installed_by_email': '',
        'installed_by_phone': '',
        'installation_date': old_data.get('issue_date', ''),
        'installation_location': '',
        'installation_notes': 'Migrated from license v1.0',

        # X.509
        'signing_certificate_cn': '',
        'signing_certificate_serial': '',
        'signing_timestamp': '',

        # Nested objects (empty)
        'sales_info': None,
        'deployment_info': None,
        'compliance_info': None,
        'usage_stats': None,
        'technical_limits': None,
        'customization_info': None,

        # Change history
        'modification_history': [{
            'modified_date': datetime.now().isoformat(),
            'modified_by': 'System Migration',
            'changes': 'Migrated from v1.0 to v2.0',
            'reason': 'License format upgrade',
            'approved_by': 'System'
        }],
        'last_modified_by': 'System Migration',
        'last_modified_date': datetime.now().isoformat(),
        'license_renewal_count': 0,
        'previous_license_id': '',

        # Internal
        'internal_notes': 'Migrated from v1.0. Personnel info not available.',
        'risk_level': 'low',
        'customer_health_score': 0,
        'renewal_probability': 0,
    })

    return LicenseData.from_dict(new_data)
```

### 6.2 Backward Compatibility

License format v2.0 ยังคงอ่าน field เดิมได้ (backward compatible)

ถ้า field ใหม่ไม่มี → ใช้ค่า default

---

## 7. Recommendations (คำแนะนำ)

### 7.1 Priority Implementation

**Phase 1: Critical (ทำก่อน - 1 สัปดาห์)**
1. ✅ เพิ่ม `issued_by`, `issued_by_email`, `issued_by_employee_id`
2. ✅ เพิ่ม `installed_by`, `installed_by_email`, `installation_date`, `installation_notes`
3. ✅ เพิ่ม X.509 cert info: `signing_certificate_cn`, `signing_timestamp`
4. ✅ อัพเดต License Generator UI ให้กรอกข้อมูลเหล่านี้

**Phase 2: Important (ทำต่อ - 2 สัปดาห์)**
5. ✅ เพิ่ม `SalesInfo` (sales person, price, payment)
6. ✅ เพิ่ม `DeploymentInfo` (environment, location, Odoo version)
7. ✅ เพิ่ม `TechnicalLimits` (API calls, email sends, storage)
8. ✅ อัพเดต License Viewer ให้แสดงข้อมูลเหล่านี้

**Phase 3: Nice to Have (ทำเมื่อมีเวลา - 1 เดือน)**
9. ✅ เพิ่ม `ComplianceInfo` (PDPA, GDPR)
10. ✅ เพิ่ม `UsageStats` (activation history, usage tracking)
11. ✅ เพิ่ม `CustomizationInfo` (custom modules, integrations)
12. ✅ เพิ่ม `modification_history` (change tracking)

### 7.2 UI Changes Required

**License Generator Wizard:**
```xml
<!-- Add new fields to license generator form -->
<group string="⭐ License Issuance Personnel">
    <field name="issued_by" required="1"/>
    <field name="issued_by_email"/>
    <field name="issued_by_employee_id"/>
</group>

<group string="⭐ Installation Personnel">
    <field name="installed_by"/>
    <field name="installed_by_email"/>
    <field name="installation_date"/>
    <field name="installation_notes"/>
</group>

<group string="⭐ Sales Information">
    <field name="sales_person"/>
    <field name="sales_email"/>
    <field name="license_price"/>
    <field name="currency"/>
    <field name="payment_status"/>
</group>
```

### 7.3 Database Changes

**Add to `itxss.license.generator` model:**
```python
# In license_generator.py, add new fields:
issued_by = fields.Char(string='Issued By', required=True)
issued_by_email = fields.Char(string='Issued By Email')
issued_by_employee_id = fields.Char(string='Employee ID')

installed_by = fields.Char(string='Installed By')
installed_by_email = fields.Char(string='Installer Email')
installation_notes = fields.Text(string='Installation Notes')

sales_person = fields.Char(string='Sales Person')
sales_email = fields.Char(string='Sales Email')
license_price = fields.Float(string='License Price')
```

---

## 8. Conclusion

### คำตอบสำหรับคำถาม: "ใครของ ITX คือคน install addon ให้ลูกค้า"

✅ **เพิ่ม field เหล่านี้:**
- `installed_by` - ชื่อช่างติดตั้ง
- `installed_by_email` - อีเมล์ช่างติดตั้ง
- `installed_by_phone` - เบอร์โทรช่างติดตั้ง
- `installation_date` - วันที่ติดตั้งจริง
- `installation_location` - สถานที่ติดตั้ง
- `installation_notes` - หมายเหตุการติดตั้ง

### ข้อมูลอื่นๆ ที่ควรเพิ่ม:

✅ **License Issuance:** ใครสร้าง license (audit trail)
✅ **Sales Info:** ใครขาย, ราคาเท่าไหร่, จ่ายเงินแล้วหรือยัง
✅ **Deployment:** ติดตั้งที่ไหน, Odoo version อะไร, industry อะไร
✅ **Compliance:** PDPA, GDPR compliance
✅ **Technical Limits:** จำกัดการใช้งาน (API calls, email, storage)
✅ **Usage Tracking:** activation history, usage statistics
✅ **Customization:** มี custom module อะไรบ้าง
✅ **Change History:** ประวัติการแก้ไข license

### Benefits:

- 🔍 **Audit Trail:** รู้ว่าใครทำอะไร เมื่อไหร่
- 📞 **Better Support:** ติดต่อคนที่เกี่ยวข้องได้ทันที
- 📊 **Business Intelligence:** วิเคราะห์ยอดขาย, ลูกค้า
- ⚖️ **Legal Protection:** ป้องกันปัญหาทางกฎหมาย
- 💰 **Cost Control:** จำกัดการใช้งานที่ทำให้เกิดค่าใช้จ่าย

---

## 9. 💡 Future Feature: Customer Self-Service License Activation

### Idea: ให้ลูกค้า Install และ Request License เอง (เหมือน Odoo Enterprise)

**ปัญหาปัจจุบัน:**
- ต้องมีช่าง ITX ไปติดตั้งที่ลูกค้า (เสียเวลา + ค่าใช้จ่าย)
- ลูกค้ารอนาน (ต้องนัดหมาย, เดินทาง)
- Scale ไม่ได้ (ช่าง ITX จำกัด)

**วิสัยทัศน์:**
ลูกค้าติดตั้งเองได้ภายใน 5 นาที โดยใช้ **License Code** สั้นๆ (เหมือน Odoo Enterprise Subscription Code)

### 9.1 Customer Self-Service Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Customer Purchase License                             │
│  - ลูกค้าซื้อ license ผ่าน ITX Sales                           │
│  - จ่ายเงิน → รับ License Code ทาง email                        │
│                                                                 │
│  Example Code: "ITX-2025-ABCD-1234-XYZ5"                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Customer Install Addon                                │
│  - ลูกค้า download addon จาก ITX portal/GitHub                 │
│  - ติดตั้งเข้า Odoo (ไม่ต้องรอช่าง ITX)                        │
│  - Restart Odoo server                                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Addon Activation Wizard (ตอนเข้า Odoo ครั้งแรก)       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │  🔐 ITX Security Shield Activation                  │       │
│  │                                                     │       │
│  │  Enter your license code:                          │       │
│  │  ┌───────────────────────────────────────────┐     │       │
│  │  │ ITX-2025-ABCD-1234-XYZ5                   │     │       │
│  │  └───────────────────────────────────────────┘     │       │
│  │                                                     │       │
│  │  [x] Accept Terms & Conditions                     │       │
│  │                                                     │       │
│  │         [ Activate License ]                       │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Auto-Registration (Background)                        │
│  - Addon ส่ง API request ไป ITX License Server                 │
│  - ส่ง: License Code + Hardware Fingerprint                    │
│  - Server ตรวจสอบ: Code ถูกต้อง? ยังไม่เกิน max_instances?     │
│  - Server ส่ง: production.lic กลับมา                           │
│  - Addon บันทึก production.lic อัตโนมัติ                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Activated! ✅                                          │
│  - ลูกค้าใช้งานได้ทันที                                        │
│  - ไม่ต้องรอช่าง ITX                                            │
│  - เวลารวม: 5-10 นาที (จากที่เคยต้อง 1-3 วัน!)                │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 License Code System

**License Code Format:**
```
ITX-[YEAR]-[PRODUCT]-[SERIAL]-[CHECK]

Example: ITX-2025-ABCD-1234-XYZ5

Components:
- ITX: Prefix (fixed)
- 2025: Year issued
- ABCD: Product code (4 chars)
  - HWLD = Hello World
  - INVT = Inventory
  - SALE = Sales
  - ENTR = Enterprise (all modules)
- 1234: Serial number (unique)
- XYZ5: Checksum (verification)
```

**License Code Database:**
```python
@dataclass
class LicenseCode:
    """License activation code."""
    code: str                          # ITX-2025-ABCD-1234-XYZ5
    customer_name: str
    customer_email: str
    po_number: str
    licensed_addons: List[str]
    max_instances: int
    expiry_date: str

    # Status
    status: str                        # unused, active, revoked, expired
    activation_count: int              # จำนวนครั้งที่ activate

    # Timestamps
    created_date: str
    first_activated_date: str = ""
    last_activated_date: str = ""

    # Registered instances
    registered_fingerprints: List[str] = []
```

### 9.3 API Endpoints (ITX License Server)

**API #1: Validate License Code**
```http
POST https://license.itxcorp.com/api/v1/validate_code
Content-Type: application/json

{
  "code": "ITX-2025-ABCD-1234-XYZ5",
  "hardware_fingerprint": "a1b2c3d4e5f6...",
  "machine_id": "12345678-1234-1234-1234-123456789012",
  "hostname": "customer-odoo-prod",
  "odoo_version": "19.0",
  "customer_email": "admin@customer.com"  // for verification
}

Response (Success):
{
  "status": "success",
  "license_file": "base64-encoded-production.lic",
  "customer_name": "บริษัท ABC จำกัด",
  "licensed_addons": ["itx_helloworld"],
  "expiry_date": "2026-12-31",
  "message": "License activated successfully!"
}

Response (Error - Already Used):
{
  "status": "error",
  "error_code": "MAX_INSTANCES_REACHED",
  "message": "This license code has already been activated on 3 machines (max: 3)",
  "registered_instances": [
    {"hostname": "prod-01", "activated": "2025-12-01"},
    {"hostname": "prod-02", "activated": "2025-12-05"},
    {"hostname": "prod-03", "activated": "2025-12-10"}
  ],
  "support_email": "license@itxcorp.com",
  "support_phone": "+66 2 123 4567"
}

Response (Error - Invalid Code):
{
  "status": "error",
  "error_code": "INVALID_CODE",
  "message": "License code not found or invalid"
}

Response (Error - Expired):
{
  "status": "error",
  "error_code": "LICENSE_EXPIRED",
  "message": "License expired on 2025-11-30",
  "renewal_url": "https://license.itxcorp.com/renew/ITX-2025-ABCD-1234-XYZ5"
}
```

**API #2: Deactivate Instance (ถ้าลูกค้าย้ายเครื่อง)**
```http
POST https://license.itxcorp.com/api/v1/deactivate_instance
Content-Type: application/json

{
  "code": "ITX-2025-ABCD-1234-XYZ5",
  "hardware_fingerprint": "a1b2c3d4e5f6...",
  "reason": "migrating_to_new_server"
}

Response:
{
  "status": "success",
  "message": "Instance deactivated. You can now activate on a new machine.",
  "remaining_activations": 3
}
```

### 9.4 Client-Side Implementation (Addon)

**Activation Wizard (Odoo Transient Model):**

```python
# models/license_activation_wizard.py

from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import base64
import os

class LicenseActivationWizard(models.TransientModel):
    _name = 'itxss.license.activation.wizard'
    _description = 'License Activation Wizard'

    license_code = fields.Char(
        string='License Code',
        required=True,
        help='Enter license code (e.g., ITX-2025-ABCD-1234-XYZ5)'
    )
    customer_email = fields.Char(
        string='Email',
        required=True,
        help='Email for verification'
    )
    terms_accepted = fields.Boolean(
        string='I accept the Terms & Conditions',
        required=True
    )

    activation_status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error')
    ], default='pending', readonly=True)

    activation_message = fields.Text(readonly=True)

    def action_activate(self):
        """Activate license using license code."""
        self.ensure_one()

        if not self.terms_accepted:
            raise UserError('You must accept Terms & Conditions')

        # Validate code format
        if not self._validate_code_format(self.license_code):
            raise UserError('Invalid license code format')

        try:
            # Get hardware info
            from odoo.addons.itx_security_shield.lib.verifier import get_hardware_info
            hw_info = get_hardware_info()

            # Call ITX License Server API
            response = requests.post(
                'https://license.itxcorp.com/api/v1/validate_code',
                json={
                    'code': self.license_code,
                    'hardware_fingerprint': hw_info.get('fingerprint'),
                    'machine_id': hw_info.get('machine_id'),
                    'hostname': os.uname().nodename,
                    'odoo_version': '19.0',
                    'customer_email': self.customer_email,
                },
                timeout=30,
                verify=True  # Verify SSL
            )

            data = response.json()

            if data.get('status') == 'success':
                # Save license file
                license_data = base64.b64decode(data['license_file'])
                addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                license_path = os.path.join(addon_path, 'production.lic')

                with open(license_path, 'wb') as f:
                    f.write(license_data)

                self.write({
                    'activation_status': 'success',
                    'activation_message': (
                        f"✅ License activated successfully!\n\n"
                        f"Customer: {data['customer_name']}\n"
                        f"Licensed Addons: {', '.join(data['licensed_addons'])}\n"
                        f"Expiry Date: {data['expiry_date']}\n\n"
                        f"Please restart Odoo server to complete activation."
                    )
                })

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success!',
                        'message': 'License activated. Please restart Odoo server.',
                        'type': 'success',
                        'sticky': True,
                    }
                }
            else:
                # Error handling
                error_code = data.get('error_code')
                error_msg = data.get('message')

                if error_code == 'MAX_INSTANCES_REACHED':
                    instances = data.get('registered_instances', [])
                    msg = f"❌ {error_msg}\n\nRegistered instances:\n"
                    for inst in instances:
                        msg += f"- {inst['hostname']} (activated: {inst['activated']})\n"
                    msg += f"\nContact support: {data['support_email']}"

                elif error_code == 'LICENSE_EXPIRED':
                    msg = f"❌ {error_msg}\n\nRenew at: {data.get('renewal_url')}"

                else:
                    msg = f"❌ {error_msg}"

                self.write({
                    'activation_status': 'error',
                    'activation_message': msg
                })

                raise UserError(msg)

        except requests.exceptions.RequestException as e:
            raise UserError(
                f"Cannot connect to ITX License Server.\n\n"
                f"Error: {str(e)}\n\n"
                f"Please check your internet connection or contact support."
            )

    def _validate_code_format(self, code):
        """Validate license code format."""
        import re
        pattern = r'^ITX-\d{4}-[A-Z]{4}-\d{4}-[A-Z0-9]{4}$'
        return re.match(pattern, code) is not None
```

**Auto-Show Activation Wizard (on first run):**

```python
# models/ir_module_module.py

from odoo import models, api

class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _check_license_on_startup(self):
        """Check if license exists, show activation wizard if not."""
        import os
        addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        license_path = os.path.join(addon_path, 'production.lic')

        if not os.path.exists(license_path):
            # No license found - show activation wizard
            return {
                'type': 'ir.actions.act_window',
                'name': 'Activate ITX Security Shield',
                'res_model': 'itxss.license.activation.wizard',
                'view_mode': 'form',
                'target': 'new',
            }
```

### 9.5 License Code Generator (ITX Admin)

**Admin Portal for Generating Codes:**

```python
# ITX Internal System - License Code Generator

import random
import string
import hashlib
from datetime import datetime, timedelta

class LicenseCodeGenerator:
    """Generate license activation codes."""

    PRODUCT_CODES = {
        'itx_helloworld': 'HWLD',
        'itx_inventory': 'INVT',
        'itx_sales': 'SALE',
        'itx_accounting': 'ACCT',
        'itx_enterprise': 'ENTR',  # All modules
    }

    @staticmethod
    def generate_code(product: str, serial_number: int) -> str:
        """
        Generate license code.

        Format: ITX-[YEAR]-[PRODUCT]-[SERIAL]-[CHECK]
        Example: ITX-2025-HWLD-0001-AB3X
        """
        year = datetime.now().year
        product_code = LicenseCodeGenerator.PRODUCT_CODES.get(product, 'UNKN')
        serial = f"{serial_number:04d}"

        # Generate checksum
        data = f"{year}{product_code}{serial}"
        checksum = hashlib.sha256(data.encode()).hexdigest()[:4].upper()

        code = f"ITX-{year}-{product_code}-{serial}-{checksum}"
        return code

    @staticmethod
    def validate_checksum(code: str) -> bool:
        """Validate license code checksum."""
        parts = code.split('-')
        if len(parts) != 5:
            return False

        year, product, serial, checksum = parts[1], parts[2], parts[3], parts[4]
        data = f"{year}{product}{serial}"
        expected_checksum = hashlib.sha256(data.encode()).hexdigest()[:4].upper()

        return checksum == expected_checksum

# Usage:
# code = LicenseCodeGenerator.generate_code('itx_helloworld', 1234)
# print(code)  # ITX-2025-HWLD-1234-A3B5
```

### 9.6 Benefits of Self-Service Activation

| Metric | Current (Manual Install) | Future (Self-Service) |
|--------|--------------------------|----------------------|
| **Activation Time** | 1-3 days | 5-10 minutes |
| **ITX Personnel Required** | 1 technician | 0 (automated) |
| **Cost per Activation** | 5,000-10,000 THB | ~0 THB |
| **Customer Satisfaction** | 6/10 (slow) | 9/10 (instant) |
| **Scalability** | Limited (10-20 customers/month) | Unlimited (1000s/month) |
| **Geographic Coverage** | Thailand only | Worldwide |
| **24/7 Availability** | No (business hours only) | Yes |

### 9.7 Additional Fields Needed for Self-Service

```python
# เพิ่มใน LicenseData

# ⭐ Self-Service Activation
activation_method: str = ""           # manual, self_service, api
license_code: str = ""                # ITX-2025-ABCD-1234-XYZ5
activation_ip: str = ""               # IP ที่ activate
activation_country: str = ""          # ประเทศที่ activate (from GeoIP)
activation_user_agent: str = ""       # Odoo version, OS, etc.

# Customer who activated (not ITX personnel)
activated_by_customer_name: str = ""  # ชื่อคนที่ activate (ลูกค้า)
activated_by_customer_email: str = "" # อีเมล์คนที่ activate
terms_accepted_version: str = ""      # เวอร์ชันข้อตกลงที่ยอมรับ
terms_accepted_ip: str = ""           # IP ที่ยอมรับข้อตกลง
```

### 9.8 Implementation Roadmap

**Phase 1: License Code System (2 สัปดาห์)**
- [ ] สร้าง License Code Generator
- [ ] Database สำหรับ License Codes
- [ ] API endpoint: `/api/v1/validate_code`
- [ ] Admin portal สำหรับ generate codes

**Phase 2: Client-Side Activation (2 สัปดาห์)**
- [ ] Activation Wizard UI
- [ ] API client code
- [ ] Auto-show wizard on first run
- [ ] Error handling + user feedback

**Phase 3: Testing & Security (1 สัปดาห์)**
- [ ] Rate limiting (prevent brute-force)
- [ ] Code expiry (unused codes expire after 30 days)
- [ ] Fraud detection (same code used on 100 machines)
- [ ] Geo-blocking (if needed)

**Phase 4: Customer Portal (3 สัปดาห์)**
- [ ] Customer login portal
- [ ] View license status
- [ ] Manage instances (deactivate old machines)
- [ ] Download invoices
- [ ] Request renewals

**Total Time:** 8 สัปดาห์ (2 เดือน)

### 9.9 Security Considerations

**Prevent Abuse:**

1. **Rate Limiting:**
   - จำกัด 5 activation attempts ต่อ IP ต่อชั่วโมง
   - Code ที่ fail 10 ครั้ง → auto-lock (ต้องติดต่อ support)

2. **Code Expiry:**
   - License code ที่ไม่ได้ activate ภายใน 30 วัน → expire
   - Customer ต้อง request code ใหม่

3. **Geo-Blocking:**
   - ถ้าซื้อ license สำหรับ Thailand only
   - Block activation จาก IP ต่างประเทศ (optional)

4. **Fraud Detection:**
   - Code เดียวกันถูก activate จาก 100 IPs ใน 1 วัน → suspicious
   - Alert admin + auto-revoke

5. **HTTPS Only:**
   - API ต้องเป็น HTTPS เท่านั้น
   - Certificate pinning (optional)

### 9.10 Customer Experience (UX)

**Email ที่ลูกค้าได้รับ:**

```
Subject: Your ITX Security Shield License Code

Dear คุณสมชาย,

Thank you for purchasing ITX Security Shield!

Your license details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
License Code: ITX-2025-HWLD-1234-AB3X
Product: ITX Hello World
Max Instances: 3
Expiry Date: 2026-12-31
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Installation Instructions:
1. Install addon: Upload zip file to Odoo
2. Restart Odoo server
3. Go to: Settings > ITX Security Shield > Activate License
4. Enter license code: ITX-2025-HWLD-1234-AB3X
5. Click "Activate"

Done! ✅

Need help? Contact us:
- Email: support@itxcorp.com
- Phone: +66 2 123 4567
- Portal: https://support.itxcorp.com

Best regards,
ITX Corporation
```

### 9.11 Comparison: Odoo Enterprise vs ITX Self-Service

| Feature | Odoo Enterprise | ITX Self-Service |
|---------|-----------------|------------------|
| **Activation Method** | Subscription code | License code |
| **Code Format** | `ABC123DEF456` (12 chars) | `ITX-2025-HWLD-1234-AB3X` (25 chars) |
| **Hardware Binding** | Yes (fingerprint) | Yes (fingerprint) |
| **Multi-Instance** | Yes (per subscription tier) | Yes (configurable) |
| **Online Required** | Yes (initial activation) | Yes (initial activation) |
| **Offline Mode** | Yes (after activation) | Yes (after activation) |
| **Deactivation** | Self-service portal | Self-service portal |
| **Auto-Renewal** | Yes | Future feature |
| **Trial Period** | 30 days | Configurable |

---

## 10. Summary & Next Steps

### คำตอบสำหรับคำถาม:

1. ✅ **"ใครของ ITX คือคน install addon ให้ลูกค้า"**
   - เพิ่ม `installed_by`, `installation_date`, `installation_notes`

2. ✅ **Future: Customer Self-Service**
   - License Code System (เหมือน Odoo Enterprise)
   - ลูกค้า install + activate เองได้ใน 5 นาที
   - ไม่ต้องรอช่าง ITX

### Priority Actions:

**Short-term (Phase 1 - 1 สัปดาห์):**
- เพิ่ม audit trail fields (`issued_by`, `installed_by`)
- อัพเดต License Generator UI

**Mid-term (Phase 2-3 - 1 เดือน):**
- เพิ่ม Sales/Deployment/Technical info
- Migration script v1.0 → v2.0

**Long-term (Phase 4+ - 2-3 เดือน):**
- Self-Service License Activation
- Customer Portal
- Analytics Dashboard

---

**Next Step:** พี่คลอดจะเริ่มเพิ่ม field เหล่านี้ใน code หรือไม่ครับ? หรือต้องการให้วิเคราะห์เพิ่มเติมอะไรอีกมั๊ยครับ?
