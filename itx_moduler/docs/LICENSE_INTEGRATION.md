# ITX Moduler + ITX Security Shield Integration

## 🎯 Vision: Licensed AI-Powered Module Creator

**ITX Moduler** (AI module creator) + **ITX Security Shield** (licensing system) = **Commercial SaaS Product**

---

## 💰 Business Model

### Pricing Tiers

#### 1. **Free Tier** (Community Edition)
```
Price: $0
Features:
- Import existing modules
- Basic editing (models, fields)
- Generate code (max 3 models per module)
- No AI assistance
- Watermark in generated code
```

#### 2. **Professional** ($99/month or $990/year)
```
Features:
- Unlimited modules
- Unlimited models/fields
- Basic AI assistance (10 requests/day)
- No watermark
- Priority support
```

#### 3. **Enterprise** ($299/month or $2,990/year)
```
Features:
- Everything in Professional
- Unlimited AI assistance
- Claude Opus 4.5 (most capable)
- Multi-user support
- Custom training
- Dedicated support
```

#### 4. **Lifetime License** ($4,999 one-time)
```
Features:
- Everything in Enterprise
- Forever license
- All future updates
- On-premise installation
```

---

## 🏗️ Integration Architecture

### Component Interaction

```
┌─────────────────────────────────────────────────────┐
│            ITX Moduler (Main App)                    │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  User Interface                                 │ │
│  │  - Wizard: Create/Edit modules                  │ │
│  │  - AI Chat: Ask Claude for help                 │ │
│  └────────────────┬───────────────────────────────┘ │
│                   │                                  │
│  ┌────────────────▼───────────────────────────────┐ │
│  │  License Validation Layer                       │ │
│  │  - Check feature access                         │ │
│  │  - Track AI usage quota                         │ │
│  │  - Enforce limits                               │ │
│  └────────────────┬───────────────────────────────┘ │
│                   │                                  │
└───────────────────┼──────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────┐
│        ITX Security Shield (License System)          │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │  License Check                                  │ │
│  │  - Validate license file                        │ │
│  │  - Check hardware binding                       │ │
│  │  - Verify expiry date                           │ │
│  └────────────────┬───────────────────────────────┘ │
│                   │                                  │
│  ┌────────────────▼───────────────────────────────┐ │
│  │  License Data                                   │ │
│  │  - Customer info                                │ │
│  │  - Tier level (Free/Pro/Enterprise)             │ │
│  │  - Feature flags                                │ │
│  │  - AI quota (requests per day)                  │ │
│  └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation

### 1. License Data Structure

Extend ITX Security Shield license format to include ITX Moduler-specific data:

```json
{
  "customer_name": "ABC Company Ltd.",
  "customer_po": "PO-2025-001",
  "expiry_date": "2025-12-31",
  "max_instances": 1,
  "licensed_addons": ["itx_moduler"],

  "itx_moduler": {
    "tier": "enterprise",
    "features": {
      "max_models_per_module": -1,
      "ai_enabled": true,
      "ai_quota_daily": -1,
      "ai_model": "claude-opus-4-5-20251101",
      "watermark": false,
      "multi_user": true
    }
  },

  "hardware_fingerprint": "abc123...",
  "signature": "RSA signature..."
}
```

### 2. License Validation in ITX Moduler

```python
# models/itx_moduler_license.py
from odoo import models, fields, api
from odoo.exceptions import UserError

class ItxCreatorLicense(models.AbstractModel):
    _name = 'itx.moduler.license'
    _description = 'ITX Moduler License Manager'

    @api.model
    def check_license(self):
        """Check if ITX Moduler is licensed"""
        LicenseCheck = self.env['license.check']

        # Validate license through ITX Security Shield
        result = LicenseCheck.validate_license()

        if not result['valid']:
            raise UserError(
                'ITX Moduler is not licensed.\n\n'
                'Please contact sales@itexpert.co.th to purchase a license.'
            )

        # Check if itx_moduler is in licensed addons
        license_data = result['license_data']
        if 'itx_moduler' not in license_data.get('licensed_addons', []):
            raise UserError(
                'ITX Moduler is not included in your license.\n\n'
                'Please upgrade your license to include ITX Moduler.'
            )

        return license_data.get('itx_moduler', {})

    @api.model
    def get_tier(self):
        """Get current license tier"""
        try:
            creator_license = self.check_license()
            return creator_license.get('tier', 'free')
        except UserError:
            return 'free'

    @api.model
    def check_feature(self, feature_name):
        """Check if a feature is enabled in current tier"""
        tier = self.get_tier()
        creator_license = self.check_license()

        features = creator_license.get('features', {})

        # Feature matrix
        FEATURES = {
            'free': {
                'max_models_per_module': 3,
                'ai_enabled': False,
                'ai_quota_daily': 0,
                'watermark': True,
                'multi_user': False,
            },
            'professional': {
                'max_models_per_module': -1,
                'ai_enabled': True,
                'ai_quota_daily': 10,
                'ai_model': 'claude-sonnet-4-5-20250929',
                'watermark': False,
                'multi_user': False,
            },
            'enterprise': {
                'max_models_per_module': -1,
                'ai_enabled': True,
                'ai_quota_daily': -1,
                'ai_model': 'claude-opus-4-5-20251101',
                'watermark': False,
                'multi_user': True,
            },
        }

        tier_features = FEATURES.get(tier, FEATURES['free'])
        return features.get(feature_name, tier_features.get(feature_name))

    @api.model
    def get_ai_quota_remaining(self):
        """Get remaining AI requests for today"""
        quota_daily = self.check_feature('ai_quota_daily')

        if quota_daily == -1:  # Unlimited
            return -1

        # Count today's usage
        today = fields.Date.today()
        usage_count = self.env['itx.moduler.ai.usage'].search_count([
            ('user_id', '=', self.env.user.id),
            ('date', '=', today),
        ])

        return max(0, quota_daily - usage_count)
```

### 3. Feature Gates

```python
# models/itx_moduler_module.py
class ItxCreatorModule(models.Model):
    _name = 'itx.moduler.module'

    @api.constrains('model_ids')
    def _check_model_limit(self):
        """Enforce model limit based on license tier"""
        license = self.env['itx.moduler.license']
        max_models = license.check_feature('max_models_per_module')

        for module in self:
            if max_models != -1 and len(module.model_ids) > max_models:
                raise ValidationError(
                    f'Your license tier allows maximum {max_models} models per module.\n\n'
                    f'Current: {len(module.model_ids)} models\n\n'
                    f'Please upgrade to Professional or Enterprise tier.'
                )

    def action_generate_code(self):
        """Generate code with watermark if free tier"""
        license = self.env['itx.moduler.license']
        watermark = license.check_feature('watermark')

        # Generate code
        code = self._generate_module_code()

        if watermark:
            code = self._add_watermark(code)

        return code

    def _add_watermark(self, code):
        """Add watermark to generated code"""
        watermark_text = """
# =========================================================================
# Generated with ITX Moduler - Free Edition
#
# This code was generated using the free tier of ITX Moduler.
#
# To remove this watermark and unlock premium features:
# - Unlimited models per module
# - AI-assisted development with Claude
# - Priority support
#
# Visit: https://www.itexpert.co.th/itx-creator
# Email: sales@itexpert.co.th
# =========================================================================
"""
        return watermark_text + code
```

### 4. AI Usage Tracking

```python
# models/itx_moduler_ai_usage.py
class ItxCreatorAIUsage(models.Model):
    _name = 'itx.moduler.ai.usage'
    _description = 'AI Usage Tracking'

    user_id = fields.Many2one('res.users', required=True)
    date = fields.Date(required=True, default=fields.Date.today)
    prompt_tokens = fields.Integer()
    completion_tokens = fields.Integer()
    cost = fields.Float(compute='_compute_cost')
    request_type = fields.Selection([
        ('model_creation', 'Model Creation'),
        ('field_generation', 'Field Generation'),
        ('view_generation', 'View Generation'),
        ('code_review', 'Code Review'),
    ])

    @api.depends('prompt_tokens', 'completion_tokens')
    def _compute_cost(self):
        INPUT_COST = 3.00 / 1_000_000
        OUTPUT_COST = 15.00 / 1_000_000

        for record in self:
            record.cost = (
                record.prompt_tokens * INPUT_COST +
                record.completion_tokens * OUTPUT_COST
            )


# wizards/itx_moduler_ai_wizard.py
class ItxCreatorAIWizard(models.TransientModel):
    _name = 'itx.moduler.ai.wizard'

    def action_generate_with_ai(self):
        """Generate with AI - check quota first"""
        license = self.env['itx.moduler.license']

        # Check if AI is enabled
        if not license.check_feature('ai_enabled'):
            raise UserError(
                'AI features are not available in your license tier.\n\n'
                'Upgrade to Professional ($99/month) or Enterprise ($299/month)\n'
                'to unlock AI-assisted development.'
            )

        # Check quota
        remaining = license.get_ai_quota_remaining()
        if remaining == 0:
            raise UserError(
                'Daily AI quota exceeded.\n\n'
                'You have used all your AI requests for today.\n'
                'Quota resets at midnight.\n\n'
                'Upgrade to Enterprise for unlimited AI requests.'
            )

        # Proceed with AI generation
        response = self._call_claude_api()

        # Track usage
        self.env['itx.moduler.ai.usage'].create({
            'user_id': self.env.user.id,
            'prompt_tokens': response.usage.input_tokens,
            'completion_tokens': response.usage.output_tokens,
            'request_type': 'model_creation',
        })

        return response
```

### 5. License Info Display

```xml
<!-- views/itx_moduler.xml -->

<!-- Show license info in main menu -->
<template id="license_info_banner" name="License Info Banner">
    <div class="alert alert-info" role="alert">
        <strong>License:</strong>
        <t t-if="tier == 'free'">
            Free Edition (Limited Features)
            <a href="/web#action=upgrade_license" class="btn btn-sm btn-primary">
                Upgrade Now
            </a>
        </t>
        <t t-elif="tier == 'professional'">
            Professional Edition
            <span class="badge bg-success">Active</span>
        </t>
        <t t-elif="tier == 'enterprise'">
            Enterprise Edition
            <span class="badge bg-primary">Premium</span>
        </t>

        <t t-if="ai_enabled and ai_quota != -1">
            <br/>
            <small>AI Requests Today: <t t-esc="ai_quota_used"/> / <t t-esc="ai_quota_daily"/></small>
        </t>
    </div>
</template>

<!-- License upgrade wizard -->
<record id="upgrade_license_wizard" model="ir.ui.view">
    <field name="name">Upgrade License</field>
    <field name="model">itx.moduler.upgrade.wizard</field>
    <field name="arch" type="xml">
        <form>
            <h2>Upgrade ITX Moduler</h2>

            <group>
                <field name="current_tier" readonly="1"/>
                <field name="target_tier" widget="radio"/>
            </group>

            <group string="Pricing">
                <div class="row">
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5>Professional</h5>
                                <h3>$99/month</h3>
                                <ul>
                                    <li>Unlimited modules</li>
                                    <li>10 AI requests/day</li>
                                    <li>No watermark</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card border-primary">
                            <div class="card-body">
                                <h5>Enterprise</h5>
                                <h3>$299/month</h3>
                                <span class="badge bg-primary">Popular</span>
                                <ul>
                                    <li>Everything in Pro</li>
                                    <li>Unlimited AI requests</li>
                                    <li>Claude Opus 4.5</li>
                                    <li>Multi-user</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5>Lifetime</h5>
                                <h3>$4,999</h3>
                                <span class="badge bg-success">Best Value</span>
                                <ul>
                                    <li>Everything in Enterprise</li>
                                    <li>Forever license</li>
                                    <li>All updates included</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </group>

            <footer>
                <button name="action_contact_sales" string="Contact Sales" type="object" class="btn-primary"/>
                <button string="Cancel" class="btn-secondary" special="cancel"/>
            </footer>
        </form>
    </field>
</record>
```

---

## 📦 License Generation Workflow

### For ITX Staff

1. **Customer purchases ITX Moduler license**

2. **Generate license using ITX Security Shield:**
   ```
   ITX Security Shield → Generate License

   Customer: ABC Company
   Licensed Addons: itx_moduler
   Expiry: 2025-12-31

   Custom Data (JSON):
   {
     "itx_moduler": {
       "tier": "enterprise",
       "features": {
         "ai_enabled": true,
         "ai_quota_daily": -1,
         "ai_model": "claude-opus-4-5-20251101"
       }
     }
   }
   ```

3. **Download .lic file**

4. **Send to customer with instructions**

### For Customers

1. **Receive `.lic` file**

2. **Install on server:**
   ```bash
   sudo cp itx_moduler_ABC.lic /etc/odoo/production.lic
   sudo systemctl restart odoo
   ```

3. **Verify in ITX Moduler:**
   - Open ITX Moduler
   - See "Enterprise Edition" badge
   - AI features enabled
   - No watermark

---

## 🔐 Security Considerations

### 1. **License File Protection**
```python
# Prevent license file extraction
if os.path.exists('/etc/odoo/production.lic'):
    os.chmod('/etc/odoo/production.lic', 0o400)  # Read-only owner
```

### 2. **Feature Bypass Prevention**
```python
# Always validate license before critical operations
def action_generate_code(self):
    # ALWAYS check license first
    license = self.env['itx.moduler.license']
    license.check_license()  # Raises exception if invalid

    # Then proceed
    ...
```

### 3. **AI Quota Enforcement**
```python
# Server-side validation (can't be bypassed)
@api.model
def call_claude_api(self, prompt):
    # Check quota on server
    if self.get_ai_quota_remaining() == 0:
        raise UserError('Quota exceeded')

    # Track BEFORE making API call
    # (prevents bypass by interrupting request)
    self.env['itx.moduler.ai.usage'].create({...})

    # Then call API
    ...
```

---

## 💵 Revenue Projections

### Conservative Estimate (Year 1)

| Tier | Price | Customers | MRR | ARR |
|------|-------|-----------|-----|-----|
| Free | $0 | 500 | $0 | $0 |
| Professional | $99 | 20 | $1,980 | $23,760 |
| Enterprise | $299 | 5 | $1,495 | $17,940 |
| Lifetime | $4,999 | 2 | - | $9,998 |
| **Total** | | **527** | **$3,475** | **$51,698** |

### Optimistic Estimate (Year 2)

| Tier | Price | Customers | MRR | ARR |
|------|-------|-----------|-----|-----|
| Free | $0 | 2,000 | $0 | $0 |
| Professional | $99 | 100 | $9,900 | $118,800 |
| Enterprise | $299 | 30 | $8,970 | $107,640 |
| Lifetime | $4,999 | 10 | - | $49,990 |
| **Total** | | **2,140** | **$18,870** | **$276,430** |

---

## 🎯 Go-to-Market Strategy

### Phase 1: Soft Launch (Month 1-2)
- Release Free edition to public
- Beta test with 5-10 early adopters
- Collect feedback
- Refine features

### Phase 2: Marketing (Month 3-4)
- Write blog posts / case studies
- Create video tutorials (Thai + English)
- Present at Odoo community events
- LinkedIn / Facebook ads

### Phase 3: Sales (Month 5+)
- Direct outreach to Odoo partners
- Offer free trials (30 days)
- Referral program (20% commission)
- Annual billing discount (save 2 months)

---

## 🚀 Implementation Timeline

### Week 1-2: License Integration
- [ ] Add `itx.moduler.license` model
- [ ] Implement feature gates
- [ ] Add license info display
- [ ] Test with ITX Security Shield

### Week 3-4: AI Quota System
- [ ] Create usage tracking model
- [ ] Implement quota enforcement
- [ ] Add usage dashboard
- [ ] Test quota limits

### Week 5-6: UI/UX Polish
- [ ] Add upgrade prompts
- [ ] Create pricing page
- [ ] Design upgrade wizard
- [ ] Marketing materials

### Week 7-8: Testing & Launch
- [ ] Beta testing with customers
- [ ] Security audit
- [ ] Documentation
- [ ] Public launch! 🎉

---

## 📞 Sales Contact

**For License Inquiries:**
- Email: sales@itexpert.co.th
- Phone: +66-XXX-XXXX
- Website: https://www.itexpert.co.th/itx-creator

---

**ITX Moduler + ITX Security Shield = Profitable SaaS Business** 💰🚀

*Let's make this happen!*
