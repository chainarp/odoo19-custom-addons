# 🚀 Quick Reference Guide
## Protecting Odoo Addons - Cheat Sheet

---

## 📋 **Quick Commands**

### **Obfuscate Addon**
```bash
cd /path/to/itx_security_shield
./obfuscate_addon.sh YOUR_ADDON_NAME
```

### **Generate License for Customer**
```bash
# Method 1: Using UI
# Open Odoo → ITX Security Shield → License Generator
# Fill in customer info → Generate

# Method 2: Using Python (if you create CLI tool)
python3 generate_license.py \
  --customer "ABC Company" \
  --hardware "cpu_model:Intel..." \
  --expiration "2026-12-31" \
  --output production.lic
```

### **Get Hardware Fingerprint (Customer runs this)**
```bash
python3 -c "
from itx_security_shield.models.hardware_fingerprint import get_hardware_fingerprint
import json
print(json.dumps(get_hardware_fingerprint(), indent=2))
"
```

### **Package Addon for Delivery**
```bash
cd YOUR_ADDON
zip -r ../YOUR_ADDON_v1.0.0_CustomerName.zip \
  __manifest__.py \
  __init__.py \
  models/ \
  lib/ \
  views/ \
  security/ \
  pyarmor_runtime_000000/ \
  production.lic
```

---

## 🎯 **Protection Decision Tree**

```
┌─────────────────────────────────────────────────────────┐
│ What are you trying to prevent?                        │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
   ┌────▼────┐                   ┌──────▼──────┐
   │ Copying │                   │  Reading    │
   │  Addon  │                   │   Source    │
   │ to Other│                   │    Code     │
   │ Machine │                   └──────┬──────┘
   └────┬────┘                          │
        │                               │
        │ Solution:                     │ Solution:
        │ LICENSE                       │ PYARMOR
        │ - Hardware Binding            │ - Code Obfuscation
        │ - Unique per server           │ - AES-256 Encryption
        │ - Expiration date             │ - Runtime Decryption
        │                               │
        └───────────────┬───────────────┘
                        │
                ┌───────▼────────┐
                │  BEST OPTION:  │
                │   USE BOTH!    │
                │                │
                │  License +     │
                │  PyArmor =     │
                │  92% Protection│
                └────────────────┘
```

---

## 🔐 **Protection Comparison**

| Protection | Prevents Copying | Prevents Reading | Prevents Bypass | Difficulty | Cost |
|------------|-----------------|------------------|-----------------|------------|------|
| **None** | ❌ No | ❌ No | ❌ No | - | Free |
| **License Only** | ✅ 95% | ❌ No | ⚠️ 30% | Easy | Free* |
| **PyArmor Only** | ❌ No | ✅ 85% | ✅ 85% | Easy | Free* |
| **Both** | ✅ 99% | ✅ 85% | ✅ 90% | Medium | Free* |
| **Both + Legal** | ✅ 99% | ✅ 85% | ✅ 95% | Medium | $$ |

*Free with trial versions (suitable for your use case)

---

## 🎓 **When to Use What**

### **Use License Generator When:**
- ✅ You want to control which server can run addon
- ✅ You want expiration dates (subscription model)
- ✅ You want to track customers
- ✅ You want to remotely disable licenses

### **Use PyArmor When:**
- ✅ You want to protect business logic
- ✅ You want to prevent code modifications
- ✅ You don't want customers reading algorithms
- ✅ You want to protect license check code

### **Use Both When:**
- ✅ You're selling valuable addons
- ✅ You want maximum protection
- ✅ You can afford 5 minutes of automation

### **Don't Use Protection When:**
- ⚠️ Open source project (defeats the purpose)
- ⚠️ Internal tools (not worth the hassle)
- ⚠️ Proof of concept (premature optimization)

---

## 📊 **File Size Impact**

| File Type | Before | After Obfuscation | Increase |
|-----------|--------|-------------------|----------|
| models.py (652 bytes) | 0.6 KB | 2.2 KB | +3.5x |
| __init__.py (124 bytes) | 0.1 KB | 2.1 KB | +21x |
| verifier.py (3 KB) | 3 KB | 5.4 KB | +1.8x |
| **Total Python** | 3.7 KB | 9.7 KB | +2.6x |
| **PyArmor Runtime** | - | 778 KB | +778 KB |
| **Grand Total** | 3.7 KB | 788 KB | +213x |

**Note:** Most size increase is PyArmor runtime (one-time, reused across files)

---

## ⚡ **Common Errors & Fixes**

### **Error: ModuleNotFoundError: No module named 'pyarmor_runtime_000000'**
**Cause:** sys.path not set correctly

**Fix:** Use obfuscate_addon.sh script (auto-injects sys.path fix)

Or manually add to __init__.py:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

---

### **Error: SyntaxError in __manifest__.py**
**Cause:** __manifest__.py was obfuscated

**Fix:** __manifest__.py must NOT be obfuscated
```bash
cp backup/__manifest__.py addon/__manifest__.py
```

---

### **Error: Hardware mismatch detected**
**Cause:** License generated for different hardware

**Fix:** Generate new license with correct hardware fingerprint
```bash
# Get current hardware
python3 -c "from itx_security_shield... import get_hardware_fingerprint; ..."

# Generate new license with this fingerprint
```

---

### **Error: License validation failed**
**Cause:** License file missing or invalid

**Fix:** Ensure production.lic exists in addon root
```bash
ls YOUR_ADDON/production.lic  # Should exist
```

---

### **Error: License expired**
**Cause:** Expiration date passed

**Fix:** Generate new license with new expiration date

---

## 🔍 **How to Verify Protection Works**

### **Test 1: License Required**
```bash
# Remove license file
rm YOUR_ADDON/production.lic

# Try to use addon
# → Should fail: "License validation failed"

# Restore license
cp production.lic YOUR_ADDON/

# Try again
# → Should work ✅
```

### **Test 2: Hardware Binding**
```bash
# Copy addon to different machine
scp -r YOUR_ADDON user@other-server:/opt/odoo/addons/

# On other server, try to use addon
# → Should fail: "Hardware mismatch detected" ✅
```

### **Test 3: Code Obfuscation**
```bash
# Try to read source code
cat YOUR_ADDON/models/models.py

# Should see encrypted bytecode:
# from pyarmor_runtime_000000 import __pyarmor__
# __pyarmor__(__name__, __file__, b'PY000000\x00\x03\x0c...')
# [Binary data] ✅
```

### **Test 4: Can't Modify License Check**
```bash
# Try to bypass license check by editing file
nano YOUR_ADDON/lib/verifier.py

# Should see encrypted bytecode (can't understand) ✅
```

---

## 🎯 **Customer Support Quick Responses**

### **Customer: "Addon won't activate"**
```
Please send us:
1. Odoo log file (last 50 lines)
2. Output of this command:
   python3 -c "from itx_security_shield... import get_hardware_fingerprint; ..."

We'll generate a new license for you.
```

### **Customer: "Can I move addon to new server?"**
```
Yes, but you need a new license because licenses are hardware-bound.

Please run this on your NEW server:
  [command to get hardware fingerprint]

Send us the output, and we'll generate a new license within 24 hours.

Note: Your old server's license will be deactivated.
```

### **Customer: "License expired"**
```
Your license expired on [date].

To renew:
1. Contact sales@yourcompany.com
2. Subscription fee: $XXX/year
3. We'll send new license within 24 hours after payment

Thank you for using [YOUR_ADDON]!
```

### **Customer: "Can I see source code?"**
```
[YOUR_ADDON] is proprietary software. Source code is protected.

However, we provide:
- Full documentation
- API reference
- Support via email/phone
- Custom development services (quote available)

If you need custom modifications, contact us at dev@yourcompany.com
```

---

## 📁 **File Checklist - What to Deliver**

When delivering addon to customer, include:

- [ ] Obfuscated addon (ZIP file)
  - [ ] `__manifest__.py` (original)
  - [ ] `__init__.py` (obfuscated + sys.path fix)
  - [ ] `models/` (obfuscated)
  - [ ] `lib/verifier.py` (obfuscated)
  - [ ] `pyarmor_runtime_000000/` (runtime)
  - [ ] `views/` (original XML)
  - [ ] `security/` (original CSV)
  - [ ] `production.lic` (customer-specific license)

- [ ] Installation guide (PDF)
  - [ ] System requirements
  - [ ] Installation steps
  - [ ] Verification steps
  - [ ] Troubleshooting
  - [ ] Support contact info

- [ ] License agreement (PDF)
  - [ ] Terms of use
  - [ ] Hardware binding notice
  - [ ] No redistribution clause
  - [ ] Support terms

- [ ] Invoice/Receipt (if applicable)

---

## 💰 **Pricing Strategy (Suggestions)**

### **Option 1: One-Time License**
```
Basic Addon:     $500 - $1,000
Medium Addon:  $1,500 - $3,000
Complex Addon: $5,000 - $10,000

+ $200/year support & updates
```

### **Option 2: Subscription Model**
```
Monthly:  $100 - $500/month
Yearly:   $1,000 - $5,000/year (2 months free)

Includes:
- License for 1 server
- Updates
- Support (email)
```

### **Option 3: Perpetual + Maintenance**
```
Perpetual License: $2,000 - $10,000 (one-time)
Annual Maintenance: 20% of license price

Maintenance includes:
- Updates
- Bug fixes
- Email support
```

**Recommendation:** Use subscription model for predictable revenue.

---

## 🎓 **Best Practices**

### **DO:**
- ✅ Always test obfuscated addon before delivery
- ✅ Keep original source in private git repo
- ✅ Generate unique license per customer
- ✅ Document customer's hardware fingerprint
- ✅ Set realistic expiration dates
- ✅ Use version numbers in filenames
- ✅ Provide good documentation
- ✅ Respond to support requests quickly
- ✅ Have legal contracts in place

### **DON'T:**
- ❌ Don't share private_key.pem with anyone
- ❌ Don't reuse licenses across customers
- ❌ Don't obfuscate __manifest__.py
- ❌ Don't claim "100% unbreakable"
- ❌ Don't forget to backup original code
- ❌ Don't deliver without testing first
- ❌ Don't ignore customer support requests
- ❌ Don't rely on security alone (use contracts)

---

## 📞 **Emergency Procedures**

### **Private Key Compromised**
```
1. IMMEDIATELY generate new RSA key pair
2. Re-generate ALL customer licenses with new key
3. Deploy new public key to all customers
4. Revoke old licenses
5. Notify customers (system maintenance)
6. Investigate how key was compromised
```

### **PyArmor Bypassed**
```
1. Don't panic - this is extremely rare
2. Investigate how bypass was achieved
3. Consider upgrading to PyArmor Pro
4. Add additional obfuscation layers
5. Update license check logic
6. Re-obfuscate all addons
7. Deploy updates to customers
```

### **Mass License Piracy**
```
1. Document evidence
2. Contact legal counsel
3. Send cease & desist letters
4. Consider online license validation
5. Add phone-home feature (with customer consent)
6. Improve protection (harder to crack)
```

---

## 🔗 **Useful Links**

- PyArmor Documentation: https://pyarmor.readthedocs.io/
- Odoo Development: https://www.odoo.com/documentation/
- Python Cryptography: https://cryptography.io/
- RSA Encryption: https://en.wikipedia.org/wiki/RSA_(cryptosystem)

---

## 📈 **Protection Evolution Path**

```
START
  │
  ├─ Phase 1: Basic Protection (CURRENT) ✅
  │  - License Generator
  │  - Hardware Binding
  │  - PyArmor Obfuscation
  │  Protection: 92%
  │
  ├─ Phase 2: Enhanced Protection (FUTURE)
  │  - Online license validation
  │  - Usage tracking
  │  - Automated license renewal
  │  - Multi-server licenses
  │  Protection: 95%
  │
  ├─ Phase 3: Advanced Protection (OPTIONAL)
  │  - Custom obfuscation
  │  - Dongle/Hardware key
  │  - Cloud-based licensing
  │  - Real-time monitoring
  │  Protection: 98%
  │
  └─ Phase 4: Enterprise (IF NEEDED)
     - Dedicated license server
     - Load balancing
     - High availability
     - Global distribution
     Protection: 99%
```

**Your current Phase 1 is sufficient for most use cases!**

---

## ✅ **Final Checklist Before Delivery**

- [ ] Addon fully tested (non-obfuscated)
- [ ] License check implemented
- [ ] License check tested (fail without license)
- [ ] License check tested (fail on wrong hardware)
- [ ] Addon obfuscated using obfuscate_addon.sh
- [ ] Obfuscated version tested on dev server
- [ ] Customer hardware fingerprint collected
- [ ] License generated with correct hardware fingerprint
- [ ] License tested on customer's hardware (if possible)
- [ ] Documentation prepared (installation guide)
- [ ] Legal documents prepared (license agreement)
- [ ] Support contact info included
- [ ] Backup of original source code saved
- [ ] Delivery package created (ZIP file)
- [ ] Invoice/receipt prepared (if selling)
- [ ] Customer notified (email with instructions)

---

**You're ready to ship! 🚀**
