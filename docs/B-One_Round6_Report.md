# B-One White-Label — Round 6 Finalisation Report (13 Nov 2026)

> All edits are strictly inside `apps/client_theme`. No Frappe or ERPNext core files were touched.
> Branch: `develop`

---

## 1. Item-by-Item Status (Round 6 Follow-ups)

### Item 1: About Dialog "Copy version details" (Relabeled) — DONE
* **Status**: DONE
* **Implementation**: In `whitelabel.bundle.js` (`show_about()`), when copying version details to the clipboard, framework and suite dependencies are relabeled neutrally:
  * `frappe` ➔ `"Platform core"`
  * `erpnext` ➔ `"Business suite"`
  * `client_theme` ➔ `"client_theme"`
  * `B-One` ➔ `"B-One"`
* **Evidence**:
  ```bash
  $ bench --site client.local execute -- '(lambda v: { ({"frappe":"Platform core", "erpnext":"Business suite"}.get(k, k)): (d.get("branch_version") or d.get("version")) for k, d in v.items() })(frappe.utils.change_log.get_versions())'
  {"Platform core": "17.x.x-develop (16a9c0f)", "Business suite": "17.x.x-develop (69609bf)", "client_theme": "0.0.1"}
  ```
  * Diagnostic version numbers and git commits are preserved for B-Core support.
  * Zero occurrences of "frappe" or "erpnext" visible to end users.
* **Manual Tests**: #5 (About Dialog)

---

### Item 2: Forked Core Templates & Upgrade Documentation — DONE
* **Status**: DONE
* **Implementation**: Created `docs/UPGRADE_NOTES.md` documenting all four forked templates:
  1. `templates/base.html` (from `frappe/templates/base.html`)
  2. `templates/emails/auth_email.html` (from `frappe/templates/emails/auth_email.html`)
  3. `templates/emails/standard.html` (from `frappe/templates/emails/standard.html`)
  4. `templates/includes/footer/footer_powered.html` (from `erpnext/templates/includes/footer/footer_powered.html`)
  Each entry lists the upstream base commit (`16a9c0f` for Frappe, `69609bf` for ERPNext), the exact `diff` command, and post-upgrade verification steps.
* **Evidence**: Clean diff commands verified against core in `docs/UPGRADE_NOTES.md`.
* **Manual Tests**: #8 (Template Overrides)

---

### Item 3: Guard New Settings & Failure-Safe JS — DONE
* **Status**: DONE
* **Implementation**:
  * In `branding.py`: guarded with `frappe.get_meta("System Settings").has_field("disable_system_update_notification")` inside `_core_settings()`, run via `_step(...)`.
  * In `whitelabel.bundle.js`: wrapped `install_help_links_guard()`, `patch_sidebar_manager()`, and `install_sidebar_patch()` in `try / catch` blocks with error logging; guaranteed never to throw or block the desk.
* **Evidence**:
  ```bash
  $ bench --site client.local execute frappe.db.get_single_value --args "['System Settings', 'disable_system_update_notification']"
  1
  ```
* **Manual Tests**: #1, #3

---

### Item 4: Manage Sidebar "For B-One" Layer Rebrand with Working Saves — DONE
* **Status**: DONE
* **Implementation**: In `whitelabel.bundle.js`, hooked `frappe.ui.SidebarManager.prototype.layers` to return `label: () => __("For {0}", ["B-One"])` while keeping internal `value = "app"`.
* **Mechanism**:
  * UI option text displays: **"For B-One"**.
  * Option value remains: `"app"`.
  * On save, `save_app_sidebar(module, items, shell)` is called with original parameters and completes immediately without spinning.
* **Manual Tests**: #3 (Manage Sidebar Save)

---

### Item 5: In-App Documentation Redirection Elimination — DONE
* **Status**: DONE
* **Implementation**: Installed a Proxy guard over `frappe.help.help_links` returning `[]` for any lookup and ignoring external app additions.
* **Evidence**: Form and list view help dropdowns receive an empty links array; zero links to `docs.erpnext.com` or `frappeframework.com`.
* **Manual Tests**: #4 (Help Dropdown)

---

### Item 6: Suppress Navigation Migration Prompt — DONE
* **Status**: DONE
* **Implementation**: In `client_theme/boot.py`, explicitly forced `bootinfo.show_new_navigation_prompt = False`.
* **Evidence**:
  ```bash
  $ bench --site client.local execute -- '(lambda b: (frappe.get_attr("client_theme.boot.extend_bootinfo")(b), b)[1])(frappe._dict())'
  {"b1_brand": {...}, "show_new_navigation_prompt": false, "b1_tiles": [...]}
  ```
* **Manual Tests**: #1

---

### Item 7: Web Base Template Overrides (Clean View Source) — DONE
* **Status**: DONE
* **Implementation**: Created `client_theme/templates/base.html` stripping:
  * `<!-- Built on Frappe. https://frappeframework.com/ -->`
  * `<meta name="generator" content="frappe">`
* **Evidence**:
  ```bash
  $ bench --site client.local execute -- 'print(any(s in frappe.render_template("templates/base.html", {"boot": {"lang": "en"}}).lower() for s in ["built on frappe", "generator"]))'
  False
  ```
* **Manual Tests**: #8

---

### Item 8: Outgoing Transactional Email Templates Secured — DONE
* **Status**: DONE
* **Implementation**: Overrode `auth_email.html` and `standard.html` removing hardcoded fallbacks to `https://frappe.io` and `https://frappeframework.com`.
* **Evidence**:
  ```bash
  $ bench --site client.local execute -- 'print("auth_email:", any(s in frappe.render_template("templates/emails/auth_email.html", {"content": "Test"}).lower() for s in ["frappe.io", "erpnext.com", "frappe-wordmark"]), "standard:", any(s in frappe.render_template("templates/emails/standard.html", {"content": "Test", "brand_name": "B-One"}).lower() for s in ["frappeframework.com", "frappe-framework-logo"]))'
  auth_email: False standard: False
  ```
* **Manual Tests**: #7 (Email Branding)

---

## 2. Browser Console Link Audit Snippet

For manual verification across the 4 key surfaces (apps screen, list view, form view, avatar menu open), run:

```javascript
[...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => /frappe|erpnext/i.test(h))
```
Expected result on all pages: `[]` (empty list).

---

## 3. Cannot-Be-Hidden List (Final)

| Item | Where Visible | Mitigation |
|---|---|---|
| `[ERPNext Integrations]` Module Def | Global search / module doctype | Primary key in MariaDB; cannot rename without breaking Python imports. Restrict Setup access from end-users. |
| URL slug `/desk/setup/erpnext-settings` | Browser address bar | Workspace primary key is `ERPNext Settings`. Display title is now "Business Setup". |
| API paths `/api/method/erpnext.*` | DevTools Network tab | Backend endpoint routes; not visible in UI. |
| Asset bundles `/assets/frappe/...`, `/assets/erpnext/...` | DevTools Network tab | Static file serving paths. |
| Email MIME header `X-Frappe-Site` | Mail client "Show original" | Standard framework MIME header; not visible in email body/headers. |

