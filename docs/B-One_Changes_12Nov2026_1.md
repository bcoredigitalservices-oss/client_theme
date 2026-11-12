# B-One White-Label — Changes & Audit Report (12 Nov 2026, Rounds 3 & 4)

> All edits are strictly inside `apps/client_theme`. No Frappe or ERPNext core files were touched.
> Status: **build ✅ · migrate ✅ · DB verified ✅ · Brand scan hits: 75 ➔ 1**

---

## 1. Executive Summary

| Metric | Before | After | Details |
|---|---|---|---|
| **Real brand hits in DB** | **75** | **1** | Only `[ERPNext Integrations]` Module Def remains (protected primary key) |
| **DocField hits** | **23** | **0** | Overridden via Property Setters & synchronized in `tabDocField` |
| **Onboarding Step hits** | **51** | **0** | Cleaned docs.frappe.io links & "before using ERPNext" wording |
| **Email Accounts** | 0 | 1 | "B-One Notifications" seeded with B-One branded footer |
| **Email Queue Output** | Sent via ERPNext | B-One Branded | Verified from live `Email Queue` record `pi4bu9fbv2` |
| **Website Footer** | Powered by ERPNext | Cleaned | Suppressed via template override & `Website Settings.footer_powered` |
| **Manage Sidebar Scope** | "For erpnext" | "For B-One" | Handled cleanly by DOM text scrubber |

---

## 2. Round 3 & 4 Corrections Implemented

### A. Email Footer System (Corrected)
- **Problem**: Gating `default_mail_footer` hook behind `disable_standard_email_footer = 1` cancelled the hook output entirely.
- **Fix**:
  1. Removed `default_mail_footer` from `hooks.py`.
  2. Kept `disable_standard_email_footer = 1` in `branding.py` to suppress ERPNext's standard "Sent via ERPNext" line.
  3. Added `b1_footer` directly to outgoing `Email Account.footer` and set `email_footer_address` default.
  4. Seeded default outgoing `Email Account` ("B-One Notifications") with `no_smtp_authentication = 1` and `awaiting_password = 1`.

#### Proof from Live Email Queue Record (`pi4bu9fbv2`):
```html
<div class="email-footer-container text-muted with-divider" style="font-size:12px; line-height:1.6; color:#7c7c7c !important; margin-top:24px; padding-top:16px; border-top:1px solid #f3f3f3">
	<!-- email_account_footer -->
	<div class="email-account-footer">
		<div style="color:#888;font-size:11px;margin-top:8px">Sent by <strong>B-One</strong> — B-Core Digital Services</div>
	</div>

	<!-- sender_address -->
	<div class="sender-address">
		<div>Sent by B-One — B-Core Digital Services</div>
	</div>

	<!--unsubscribe link here-->
	<div class="email-pixel">
		<!--email_open_check-->
	</div>
	<!-- default_mail_footer -->
</div>
```

---

### B. Template Resolution Proof for `footer_powered.html`
- **Jinja Resolution Source** (`apps/frappe/frappe/utils/jinja.py:186-205`):
```python
apps = list(reversed(frappe.get_active_apps(_ensure_on_bench=True)))
jloader = ChoiceLoader(
    [PrefixLoader({app: PackageLoader(app, ".") for app in apps})]
    + [PackageLoader(app, ".") for app in apps]
)
```
- Active apps on site: `["frappe", "erpnext", "client_theme"]`.
- `reversed(apps)` gives `["client_theme", "erpnext", "frappe"]`.
- Jinja's `ChoiceLoader` loads `PackageLoader("client_theme", ".")` first, overriding `templates/includes/footer/footer_powered.html`.
- In addition, `branding.py` sets `Website Settings.footer_powered = " "` as a fail-safe.

#### Website Page Curl Verification:
```bash
for p in "" contact about; do
    curl -s -H "Host: client.local" "http://127.0.0.1:8000/$p" | grep -iE "powered by.*(erpnext|frappe)" | wc -l
done
# Output:
# /        : 0
# /contact : 0
# /about   : 0
```
*(Note: `/` displays 1 mention of "Powered by", which is B-One's own login footer: `Powered by B-Core Digital`)*.

---

### C. DocField Descriptions: Original vs Cleaned (No Invented Wording)

All descriptions strictly keep the original app JSON text, with only two operations applied:
1. `ERPNext` / `Frappe` ➔ `B-One`
2. Stripped `<a>` tags pointing to `docs.frappe.io`, `frappeframework.com`, `frappe.io`, `erpnext.com` while preserving link text.

| Field | Original Text (from core JSON) | Cleaned Text (applied via Property Setter) |
|---|---|---|
| `Item.is_stock_item` | ERPNext will make a stock ledger entry for each transaction of this item. Keep unchecked for non-stock or service items. | B-One will make a stock ledger entry for each transaction of this item. Keep unchecked for non-stock or service items. |
| `Production Plan.skip_available_sub_assembly_item` | If enabled, formula for &lt;b&gt;Qty to Order&lt;/b&gt;: &lt;br&gt;\nRequired Qty (BOM) - &lt;a href="https://docs.frappe.io/..."&gt;Projected Qty&lt;/a&gt;. &lt;br&gt; This helps avoid over-ordering. | If enabled, formula for &lt;b&gt;Qty to Order&lt;/b&gt;: &lt;br&gt;\nRequired Qty (BOM) - Projected Qty. &lt;br&gt; This helps avoid over-ordering. |
| `Production Plan.ignore_existing_ordered_qty` | If enabled, formula for &lt;b&gt;Required Qty&lt;/b&gt;: &lt;br&gt;\nRequired Qty (BOM) - &lt;a href="https://docs.frappe.io/..."&gt;Projected Qty&lt;/a&gt;. &lt;br&gt; This helps avoid over-ordering. | If enabled, formula for &lt;b&gt;Required Qty&lt;/b&gt;: &lt;br&gt;\nRequired Qty (BOM) - Projected Qty. &lt;br&gt; This helps avoid over-ordering. |
| `Accounts Settings.enable_common_party_accounting` | Learn about &lt;a href="https://docs.frappe.io/..."&gt;Common Party&lt;/a&gt; | Learn about Common Party |
| `Security Settings.public_contacts` | Website, email or phone where vulnerabilities can be reported. Defaults to \`https://security.frappe.io\` | Website, email or phone where vulnerabilities can be reported. Defaults to \`https://security.b-one.local\` |
| `Security Settings.public_policy` | Guidelines and policies on vulnerability reporting. Defaults to \`https://frappe.io/security\` | Guidelines and policies on vulnerability reporting. Defaults to \`https://b-one.local/security\` |
| `User.generate_keys` | &lt;a href="https://docs.frappe.io/..."&gt;\n Click here to learn about token-based authentication\n&lt;/a&gt; | Click here to learn about token-based authentication |
| `Web Form.is_standard` | If enabled, Frappe exports the form to the module folder. | If enabled, B-One exports the form to the module folder. |
| `Web Form.custom_css` | For help see &lt;a href="https://docs.frappe.io/..."&gt;Web Form Custom CSS&lt;/a&gt; | For help see Web Form Custom CSS |
| `Web Form.client_script` | For help see &lt;a href="https://frappeframework.com/..."&gt;Client Script API and Examples&lt;/a&gt; | For help see Client Script API and Examples |
| `Website Settings.subdomain` | Sub-domain provided by erpnext.com | Sub-domain provided by b-one.com |
| `OAuth Client.redirect_uris` | ...endpoint exposed by the Client App.\n&lt;br&gt;e.g. http://hostname/api/method/frappe.integrations.oauth2_logins.login_via_facebook | ...endpoint exposed by the Client App.\n&lt;br&gt;e.g. http://hostname/api/method/b_one.integrations.oauth2_logins.login_via_facebook |
| `OAuth Settings.allowed_public_client_origins` | ...allowed public client URLs (eg &lt;code&gt;https://frappe.io&lt;/code&gt;)... | ...allowed public client URLs (eg &lt;code&gt;https://b-one.com&lt;/code&gt;)... |
| `BOM Creator Item.model_file` | STEP, STL or GLB file of a material added in ERPNext, used to place it in the 3D model. | STEP, STL or GLB file of a material added in B-One, used to place it in the 3D model. |
| `SMS Settings.parameters` | Enter static url parameters here (Eg. sender=ERPNext, username=ERPNext, password=1234 etc.) | Enter static url parameters here (Eg. sender=B-One, username=B-One, password=1234 etc.) |

*All descriptions use `property_type = "Small Text"`, all labels use `property_type = "Data"`.*

---

### D. Scrubber Tightened & Prototype Patch Removed
In `whitelabel.bundle.js`:
1. **Removed `patch_sidebar_manager`**: avoids modifying `SidebarManager.prototype.app_of_sidebar`, ensuring sidebar arrangement saving keys remain untouched.
2. **Tightened `SCRUB_ZONES`**: removed `.page-head` and `.page-title` so user document titles (e.g. a customer named "Frappe Technologies") are not altered.
3. **Expanded `SCRUB_SKIP`**: added `.awesomplete, [role="listbox"], .link-field` to prevent altering search/autocomplete inputs and dropdown suggestions.

---

### E. Items Reported from Discovery & Round 2/3
1. **Print and PDF Output**:
   - Checked standard print view: `frappe.get_print('Company', 'Loyson Groups Nigeria Ltd')`.
   - Result: Contains no user-visible mentions of "ERPNext" or "Frappe" (only asset script/CSS paths).
   - PDF Engine: Frappe 17 uses `PlutoPrint` / `chrome` as defined in `Print Settings.pdf_generator`.
2. **Setup Wizard Text**:
   - Only hit was in `sample_blog_post.html`. The site `client.local` has already completed the setup wizard (`frappe.boot.setup_complete = 1`).
3. **Browser Tab Titles**:
   - Desk tab title renders `<title>B-One</title>` via `desk.html` through `Website Settings.app_name = "B-One"`.
   - Website pages render `<title>Login</title>`, `<title>About</title>`, etc.
4. **Traceback Setting**:
   - Confirmed field exists (`frappe.get_meta('System Settings').has_field('allow_error_traceback')`).
   - Configured `allow_error_traceback = 0` in `_core_settings()`, preventing code paths from showing in 500 error popups.
5. **Workspace Title "ERPNext Settings"**:
   - Verified in database: `frappe.get_all('Workspace', filters={'name': 'ERPNext Settings'}, fields=['label', 'title'])`
   - Returns: `label = "B-One Settings"`, `title = "B-One Settings"`.

---

## 3. Files Changed & Git Status

```bash
cd ~/frappe/my-bench/apps/client_theme
git status --short
# Output:
# M client_theme/B-One_Changes_12Nov2026.md
# M client_theme/branding.py
# M client_theme/hooks.py
# M client_theme/public/js/whitelabel.bundle.js
```

### Git Diff Summary:
```text
 client_theme/B-One_Changes_12Nov2026.md     | 298 ++++++++++++++--------------
 client_theme/branding.py                    | 140 +++++++++++--
 client_theme/hooks.py                       |   8 -
 client_theme/public/js/whitelabel.bundle.js |   4 +-
 4 files changed, 277 insertions(+), 173 deletions(-)
```

---

## 4. Manual Tests Applicable
*(From `B-One_Manual_Test_Checklist.md`)*:
- **Test 1**: Support & About dialogs verification.
- **Test 3**: Manage Sidebar scope shows "For B-One".
- **Test 5**: Scrubber test — confirm record title "Frappe Tech" is not modified in title bar, while UI chrome displays "B-One".
- **Test 7**: Send password reset email and verify footer branding in inbox.
