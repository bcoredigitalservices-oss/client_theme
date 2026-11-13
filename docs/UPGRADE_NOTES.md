# B-One Upgrade Notes — Forked Core Template Reference

> When updating Frappe or ERPNext, compare each forked template against upstream core using the exact `diff` commands below.
> Ensure that only white-label branding modifications are maintained.

---

## 1. Upstream Base Details

| Repository | Base Commit | Branch / Tag |
|---|---|---|
| **Frappe Framework** (`apps/frappe`) | `16a9c0fac88226c67de9873a9f4a3435172283c3` | `v17.0.0-dev` |
| **ERPNext** (`apps/erpnext`) | `69609bf05386d0d4f404cffb6918b5c764427301` | `v17.0.0-dev` |

---

## 2. Forked Templates

### A. Base Web Template (`base.html`)
* **Forked File**: `apps/client_theme/client_theme/templates/base.html`
* **Core File**: `apps/frappe/frappe/templates/base.html`
* **Purpose**: Removes the HTML source comment `<!-- Built on Frappe. https://frappeframework.com/ -->` and `<meta name="generator" content="frappe">`, and sets the default favicon fallback to the B-One mark.
* **Diff Command**:
  ```bash
  diff -u apps/frappe/frappe/templates/base.html apps/client_theme/client_theme/templates/base.html
  ```
* **Expected Diff**:
  ```diff
  --- apps/frappe/frappe/templates/base.html
  +++ apps/client_theme/client_theme/templates/base.html
  @@ -2 +1,0 @@
  -<!-- Built on Frappe. https://frappeframework.com/ -->
  @@ -7 +5,0 @@
  -	<meta name="generator" content="frappe">
  @@ -18 +16 @@
  -		href="{{ (favicon or "/assets/frappe/images/frappe-favicon.svg") | abs_url }}"
  +		href="{{ (favicon or "/assets/client_theme/images/logo-mark-clean.svg") | abs_url }}"
  ```

---

### B. Authentication / System Email Template (`auth_email.html`)
* **Forked File**: `apps/client_theme/client_theme/templates/emails/auth_email.html`
* **Core File**: `apps/frappe/frappe/templates/emails/auth_email.html`
* **Purpose**: Replaces the default `https://frappe.io` fallback link with `/` and replaces `Frappe` / `frappe-wordmark.png` fallbacks with `B-One`.
* **Diff Command**:
  ```bash
  diff -u apps/frappe/frappe/templates/emails/auth_email.html apps/client_theme/client_theme/templates/emails/auth_email.html
  ```
* **Expected Diff**:
  ```diff
  --- apps/frappe/frappe/templates/emails/auth_email.html
  +++ apps/client_theme/client_theme/templates/emails/auth_email.html
  @@ -24 +24 @@
  -						<a href="{{ site_url or 'https://frappe.io' }}">
  +						<a href="{{ site_url or '/' }}">
  @@ -26 +26 @@
  -							<img class="email-brand-logo" src="{{ brand_logo }}" alt="{{ brand_name or 'Frappe' }}" />
  +							<img class="email-brand-logo" src="{{ brand_logo }}" alt="{{ brand_name or 'B-One' }}" />
  @@ -28 +28 @@
  -							{% elif brand_name and brand_name != "Frappe" %}
  +							{% elif brand_name %}
  @@ -31 +31 @@
  -							<img class="email-brand-logo" src="/assets/frappe/images/frappe-wordmark.png" alt="Frappe" />
  +							<span class="email-brand-name">B-One</span>
  ```

---

### C. Standard Email Layout Template (`standard.html`)
* **Forked File**: `apps/client_theme/client_theme/templates/emails/standard.html`
* **Core File**: `apps/frappe/frappe/templates/emails/standard.html`
* **Purpose**: Replaces the masthead fallback link `https://frappeframework.com` with `/` and prevents rendering of `frappe-framework-logo.svg`.
* **Diff Command**:
  ```bash
  diff -u apps/frappe/frappe/templates/emails/standard.html apps/client_theme/client_theme/templates/emails/standard.html
  ```
* **Expected Diff**:
  ```diff
  --- apps/frappe/frappe/templates/emails/standard.html
  +++ apps/client_theme/client_theme/templates/emails/standard.html
  @@ -19 +19 @@
  -							<a href="{{ site_url or 'https://frappeframework.com' }}">
  +							<a href="{{ site_url or '/' }}">
  @@ -22 +22 @@
  -									src="{{ brand_logo or '/assets/frappe/images/frappe-framework-logo.svg' }}"
  +									src="{{ brand_logo }}"
  ```

---

### D. Website Powered-by Footer (`footer_powered.html`)
* **Forked File**: `apps/client_theme/client_theme/templates/includes/footer/footer_powered.html`
* **Core File**: `apps/erpnext/erpnext/templates/includes/footer/footer_powered.html`
* **Purpose**: Replaces the ERPNext website footer line with an empty template to suppress `Powered by ERPNext`.
* **Diff Command**:
  ```bash
  diff -u apps/erpnext/erpnext/templates/includes/footer/footer_powered.html apps/client_theme/client_theme/templates/includes/footer/footer_powered.html
  ```

---

## 3. JavaScript Monkey-Patches & Frappe Internals

The following table lists every client-side monkey-patch in `client_theme/public/js/whitelabel.bundle.js`, the core Frappe internal it depends upon, and what must be retested following an upstream version upgrade.

| Patch Name | Core File & Target | Core Mechanism | B-One Modification | What to Retest After Upgrade |
|---|---|---|---|---|
| **Manage Sidebar Layers Hook** | `frappe/public/js/frappe/views/sidebar/arrangement_editor.js`<br>`frappe.ui.SidebarManager.prototype.layers` | Getter returning layer definitions (`user`, `desk`, `app`) | Overrides `layers.app.label` to return `__("For {0}", ["B-One"])`. Retains `value = "app"`. | Open *Manage Sidebar* on any workspace. Verify the dropdown displays **"For B-One"** and saving the arrangement persists without error. |
| **Help Links Proxy Guard** | `frappe/public/js/frappe/utils/help_links.js`<br>`frappe/public/js/frappe/utils/utils.js`<br>`frappe.help.help_links` | Object holding documentation link arrays per DocType/view | Replaced by a comprehensive `Proxy` with traps for `get`, `set`, `has`, `ownKeys`, `getOwnPropertyDescriptor`, `deleteProperty`. | In Form and List views, open the Help dropdown in the top bar. Ensure no external Frappe/ERPNext doc links appear and no console errors occur. |
| **User Menu Options** | `frappe/public/js/frappe/ui/sidebar/sidebar.js`<br>`frappe.ui.Sidebar.prototype.user_menu_options` | Returns array of action groups for dock & sidebar avatar menus | Spliced custom items **Support** (calls `frappe.ui.toolbar.b1_support()`) and **About** (calls `frappe.ui.toolbar.show_about()`) after the "Reload" entry. | Click the user avatar in the dock and sidebar. Confirm "Support" and "About" options render and open custom B-One dialogs. |
| **Dropdown Subclass** | `frappe/public/js/frappe/ui/dropdown.js`<br>`frappe.ui.Dropdown` | Base class for rendering desk dropdowns | Subclassed into `B1Dropdown` to intercept option lists and rewrite any entry with label `/frappe\s+support/i` to "Support". | Inspect all standard dropdowns that previously showed "Frappe Support" (e.g. toolbar menus); verify they open B-One support. |
| **Sidebar Banners Suppression** | `frappe/public/js/frappe/ui/sidebar/sidebar.js`<br>`frappe.ui.sidebar_banners` | Global array of promo banner descriptors appended by ERPNext | Empties the array (`length = 0`) and replaces `.push` with a no-op function. | Inspect the bottom of the left sidebar on all workspaces; confirm no "Switch to Frappe CRM" or "Switch to Helpdesk" ads appear. |
| **Apps Screen Tiles** | `frappe/public/js/frappe/utils/utils.js`<br>`frappe.utils.get_apps_screen_apps` | Function returning app cards displayed on `/app` desktop | Overridden to return B-One configured tiles from `frappe.boot.b1_tiles` (or default B-One tiles). | Navigate to `/app` (Desktop). Verify tiles match configured modules with custom icons and routes. |
| **App Logo Overrides** | `frappe/public/js/frappe/utils/utils.js`<br>`frappe.utils.app_logo` | Returns navbar/sidebar brand mark HTML | Overridden to return clean B-One SVG marks (`logo-mark-clean.svg` and `logo-mark-clean-light.svg`). | Check desk header and collapsed sidebar to confirm the B-One brand logo renders cleanly in both light and dark mode. |

---

## 4. Property Setter Field Names & Boot Keys

### A. Boot Keys (`bootinfo`)
Defined in `client_theme/boot.py` via `extend_bootinfo(bootinfo)`:
* `bootinfo.b1_brand`: Dictionary containing brand facts (`name`, `vendor`, `website`, `client`, `version`, `support_email`, `support_url`).
* `bootinfo.b1_tiles`: Role-filtered list of application tiles for the desktop `/app` screen.
* `bootinfo.show_new_navigation_prompt`: Hardcoded to `False` to suppress Frappe's new navigation prompt dialog.

### B. Property Setter Fields Maintained in `branding.py`
The following DocField properties are managed idempotently during `bench migrate`:

| DocType | Field Name | Property | Value / Purpose |
|---|---|---|---|
| `Employee Group Table` | `user_id` | label | `B-One User ID` |
| `CRM Settings` | `frappe_crm_section` | label | `B-One CRM` |
| `CRM Settings` | `enable_frappe_crm_data_synchronization` | label | `Enable B-One CRM Data Synchronization` |
| `Email Account` | `frappe_mail_site` | label | `Mail Site` |
| `Email Account` | `validate_frappe_mail_settings` | label | `Validate Mail Settings` |
| `Studio App` | `frappe_app` | label | `App (for export)` |
| `Studio Page` | `frappe_app` | label | `App (for export)` |
| `System Settings` | `frappectl_section` | label | `CLI Settings` |
| `Item` | `is_stock_item` | description | `B-One will make a stock ledger entry for each transaction...` |
| `Production Plan` | `skip_available_sub_assembly_item` | description | Formula explanation without ERPNext references |
| `Production Plan` | `ignore_existing_ordered_qty` | description | Formula explanation without ERPNext references |
| `Accounts Settings` | `enable_common_party_accounting` | description | `""` (cleared dangling pointer) |
| `Security Settings` | `public_contacts` | description | `Website, email or phone where vulnerabilities can be reported.` |
| `Security Settings` | `public_policy` | description | `Guidelines and policies on vulnerability reporting.` |
| `User` | `generate_keys` | description | `""` (cleared dangling pointer) |
| `Web Form` | `is_standard` | description | `If enabled, B-One exports the form to the module folder.` |
| `Web Form` | `custom_css` | description | `""` (cleared dangling pointer) |
| `Web Form` | `client_script` | description | `""` (cleared dangling pointer) |
| `Website Settings` | `subdomain` | description | `""` (cleared dangling pointer) |
| `OAuth Client` | `redirect_uris` | description | URIs description using real `<app>` path example |
| `OAuth Settings` | `allowed_public_client_origins` | description | Examples using `https://example.com` |
| `BOM Creator Item` | `model_file` | description | Model file description referring to B-One |
| `SMS Settings` | `parameters` | description | SMS parameters description using B-One sender |

---

## 5. Post-Upgrade Verification & Smoke Test
After pulling updates to Frappe or ERPNext, execute this smoke test procedure:

1. **Template Diff Check**:
   Run each `diff` command from Section 2. If upstream modified markup outside branding lines, re-apply upstream structural updates while keeping the branding overrides.

2. **Rebuild & Migrate**:
   ```bash
   export PATH=$PATH:$HOME/.nvm/versions/node/$(ls $HOME/.nvm/versions/node 2>/dev/null | tail -n 1)/bin
   bench build --app client_theme
   bench --site client.local migrate
   bench --site client.local execute client_theme.scan_brand.run
   ```

3. **Checklist Smoke Test Verification**:
   * **Section 3 (Navigation & Manage Sidebar)**:
     * Open any workspace, click *Edit Sidebar* / *Manage Sidebar*.
     * Verify layer option reads **"For B-One"** (not "For erpnext").
     * Reorder an item, save, and confirm save completes instantly without hanging.
     * Verify sidebar bottom has no promo banners.
   * **Section 8 (Brand Dialogs & Menus)**:
     * Click user avatar in dock/sidebar ➔ open **About**. Confirm version and copy action displays "Platform core" and "Business suite".
     * Click user avatar ➔ open **Support**. Confirm support email (`bcoredigitalservices@gmail.com`) and portal link render.
   * **Section 14 (Help Links & External Documentation)**:
     * Open form view and list view help menus. Verify zero outbound links to `docs.erpnext.com` or `frappeframework.com`.
     * Run browser console check:
       ```javascript
       [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => /frappe|erpnext/i.test(h))
       ```
       Confirm returns `[]`.
   * **Section 16 (Outgoing Emails & Notifications)**:
     * Trigger a password reset email or test notification.
     * Verify masthead image URL is non-empty and absolute.
     * Verify email footer contains exactly one line: `Sent by B-One — B-Core Digital Services`.

