# B-One White-Label — Changes Made (12 Nov 2026)

> All edits are inside `apps/client_theme`. No Frappe or ERPNext core files were touched.
> Status: **build ✅ · migrate ✅ · DB verified ✅** · screen check still pending.

---

## Files Changed

| # | File | Type | What changed |
|---|------|------|-------------|
| 1 | `client_theme/hooks.py` | Modified | Added `default_mail_footer` hook |
| 2 | `client_theme/branding.py` | Modified | Added `_email_footer()`, `_property_setters()`, updated `apply_branding()` |
| 3 | `client_theme/templates/includes/footer/footer_powered.html` | **New file** | Blank override suppresses "Powered by ERPNext" |

---

## 1. `client_theme/hooks.py`

**What:** Added the `default_mail_footer` hook so every outgoing system email ends with a B-One branded footer instead of the default "Sent by Frappe Framework" line. The standard footer is disabled in `branding.py`.

**Where:** Appended after `website_context`, before `after_install`.

```python
# Email footer appended to every outgoing system email.
# The standard Frappe footer ("Sent by Frappe Framework") is disabled in branding.py.
default_mail_footer = [
    "<div style='color:#888;font-size:11px;margin-top:8px;'>"
    "Sent by <strong>B-One</strong> &mdash; B-Core Digital Services"
    "</div>"
]
```

**Full bottom section of `hooks.py` after the change:**

```python
# Custom Theme Assets
app_include_css = ["whitelabel.bundle.css", "b_one_desk.bundle.css", "/assets/client_theme/css/b_one_fonts.css"]
web_include_css = "whitelabel.bundle.css"
app_include_js = "whitelabel.bundle.js"
extend_bootinfo = ["client_theme.boot.extend_bootinfo"]

website_context = {
    "favicon": "/assets/client_theme/images/logo-mark-clean.svg",
    "splash_image": "/assets/client_theme/images/logo-mark-clean.svg",
}

# Email footer appended to every outgoing system email.
# The standard Frappe footer ("Sent by Frappe Framework") is disabled in branding.py.
default_mail_footer = [
    "<div style='color:#888;font-size:11px;margin-top:8px;'>"
    "Sent by <strong>B-One</strong> &mdash; B-Core Digital Services"
    "</div>"
]

after_install = "client_theme.branding.apply_branding"
after_migrate = ["client_theme.branding.apply_branding"]
```

---

## 2. `client_theme/branding.py`

### 2a. `apply_branding()` — updated to include two new steps

**Before:**
```python
def apply_branding():
    for fn in (_core_settings, seed_tiles, rebrand_labels, rebrand_settings_and_links):
        _step(fn)
    frappe.clear_cache()
```

**After:**
```python
def apply_branding():
    for fn in (
        _core_settings,
        _email_footer,        # NEW — disables standard Frappe email footer
        _property_setters,    # NEW — creates Property Setters for field labels/descriptions
        seed_tiles,
        rebrand_labels,
        rebrand_settings_and_links,
    ):
        _step(fn)
    frappe.clear_cache()
```

---

### 2b. `_email_footer()` — new function

**What:** Sets the `disable_standard_email_footer` site default to `1` so Frappe stops appending its own footer to outgoing emails. Our `default_mail_footer` hook (in `hooks.py`) then becomes the only footer.

```python
def _email_footer():
    """Disable the standard Frappe email footer so our hook-supplied B-One footer is the only one."""
    frappe.db.set_default("disable_standard_email_footer", "1")
```

**Verified:** `bench --site client.local execute "frappe.db.get_default" --args '["disable_standard_email_footer"]'` → `1` ✅

---

### 2c. `_property_setters()` — new function + data table

**What:** Creates idempotent `Property Setter` records that override field labels and descriptions in ERPNext/Frappe DocTypes — without editing any core JSON. Re-applied after every `migrate` so it survives app updates.

**10 Property Setters created:**

| DocType | Field | Property | Old value | New value |
|---------|-------|----------|-----------|-----------|
| Employee Group Table | `erpnext_user_id` | label | ERPNext User ID | B-One User ID |
| CRM Settings | `frappe_crm` | label | Frappe CRM | B-One CRM |
| CRM Settings | `enable_frappe_crm_data_sync` | label | Enable Frappe CRM Data Synchronization | Enable B-One CRM Data Synchronization |
| Email Account | `frappe_mail_site` | label | Frappe Mail Site | Mail Site |
| Email Account | `validate_frappe_mail_settings` | label | Validate Frappe Mail Settings | Validate Mail Settings |
| Studio App | `frappe_app` | label | Frappe App (for export) | App (for export) |
| Studio Page | `frappe_app` | label | Frappe App (for export) | App (for export) |
| Item | `is_stock_item` | description | ERPNext will make a stock ledger entry… | B-One will make a stock ledger entry… |
| BOM Creator Item | `file` | description | …material added in ERPNext… | …material added in B-One… |
| SMS Settings | `sms_parameters` | description | Eg. sender=ERPNext… | Eg. sender=B-One… |

**Code added to `branding.py`:**

```python
# ---------------------------------------------------------------------------
# Property Setters — override field labels and descriptions from ERPNext/Frappe
# DocFields without editing core JSON. Idempotent: re-applied after every migrate.
# ---------------------------------------------------------------------------

# (doctype, fieldname, property, new_value)
_PROPERTY_SETTERS = [
    # Field labels visible to end-users
    ("Employee Group Table",     "erpnext_user_id",               "label",       "B-One User ID"),
    ("CRM Settings",             "frappe_crm",                    "label",       "B-One CRM"),
    ("CRM Settings",             "enable_frappe_crm_data_sync",   "label",       "Enable B-One CRM Data Synchronization"),
    ("Email Account",            "frappe_mail_site",              "label",       "Mail Site"),
    ("Email Account",            "validate_frappe_mail_settings", "label",       "Validate Mail Settings"),
    ("Studio App",               "frappe_app",                    "label",       "App (for export)"),
    ("Studio Page",              "frappe_app",                    "label",       "App (for export)"),
    # Descriptions visible to users / admins
    ("Item",            "is_stock_item",  "description",
     "B-One will make a stock ledger entry for each transaction of this item."
     " Keep unchecked for non-stock or service items."),
    ("BOM Creator Item", "file",          "description",
     "STEP, STL or GLB file of a material added in B-One, used to place it in the 3D model."),
    ("SMS Settings",    "sms_parameters", "description",
     "Enter static url parameters here (Eg. sender=B-One, username=B-One, password=1234 etc.)"),
]


def _property_setters():
    """Create or update Property Setter records to override ERPNext/Frappe field metadata."""
    if not frappe.db.exists("DocType", "Property Setter"):
        return

    for doctype, fieldname, prop, value in _PROPERTY_SETTERS:
        # Skip if the doctype itself is not installed on this site
        if not frappe.db.exists("DocType", doctype):
            continue

        ps_name = f"{doctype}-{fieldname}-{prop}"
        if frappe.db.exists("Property Setter", ps_name):
            frappe.db.set_value("Property Setter", ps_name, "value", value, update_modified=False)
        else:
            frappe.get_doc({
                "doctype":          "Property Setter",
                "name":             ps_name,
                "doctype_or_field": "DocField",
                "doc_type":         doctype,
                "field_name":       fieldname,
                "property":         prop,
                "property_type":    "Data",
                "value":            value,
            }).insert(ignore_permissions=True, ignore_if_duplicate=True)
```

**Verified:** `bench --site client.local execute "frappe.db.count" --args '["Property Setter"]' --kwargs '{...}'` → `10` ✅

---

## 3. `client_theme/templates/includes/footer/footer_powered.html` *(new file)*

**What:** A blank Jinja template that overrides ERPNext's `footer_powered.html` which outputs `Powered by ERPNext`. Frappe's template resolution picks up `client_theme`'s copy first, so the "Powered by" line simply disappears from all website pages.

**Path:** `apps/client_theme/client_theme/templates/includes/footer/footer_powered.html`

```jinja
{#- B-One override: suppress the "Powered by ERPNext" line in website footers. -#}
```

**Original file it replaces (in ERPNext core — not edited):**
```jinja
{{ _("Powered by {0}").format('<a href="https://frappe.io/erpnext?source=website_footer" target="_blank" class="text-muted">ERPNext</a>') }}
```

---

## Build & Migrate Commands Used

```bash
export PATH="/home/palankarta/.nvm/versions/node/v24.22.2/bin:$PATH"
cd ~/frappe/my-bench

bench build --app client_theme
bench --site client.local migrate
```

> **Note:** Node.js is managed by `nvm`. The PATH must include the nvm node bin dir or
> `bench build` will fail with `node: not found`. Add the export to your shell profile
> or `.env` to avoid doing it manually each session.

---

## Verification Commands

```bash
# 1. Check standard email footer is disabled
bench --site client.local execute "frappe.db.get_default" \
  --args '["disable_standard_email_footer"]'
# Expected output: 1

# 2. Check Website Settings app_name
bench --site client.local execute "frappe.db.get_single_value" \
  --args '["Website Settings", "app_name"]'
# Expected output: B-One

# 3. Count Property Setters created
bench --site client.local execute "frappe.db.count" \
  --args '["Property Setter"]' \
  --kwargs '{"filters": {"doc_type": ["in", ["CRM Settings", "Email Account",
    "Employee Group Table", "Item", "BOM Creator Item",
    "SMS Settings", "Studio App", "Studio Page"]]}}'
# Expected output: 10
```

---

## Still Pending (screen check required)

| Item | What to look for |
|------|-----------------|
| Avatar menu | "Support" and "About B-One" rows appear after "Reload" in the dock avatar menu |
| Manage Dock/Sidebar scope | Dropdown reads "For B-One" (not "For erpnext") |
| Dark-mode dock/title bar | No 8px alignment gap between title bar and dock |
| White content block | Workspace pages (Accounting, Support) — proposed CSS fix not yet applied |
| Outgoing email | Send a password reset; check footer reads "Sent by B-One — B-Core Digital Services" with no Frappe footer |

