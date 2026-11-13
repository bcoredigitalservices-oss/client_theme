# B-One Deployment & Handover Guide

## 1. Deploying to a New Server

Follow these steps to deploy B-One white-label on a production server:

1. **Install Application**:
   ```bash
   cd ~/frappe/my-bench
   bench get-app https://github.com/<org>/client_theme.git
   bench --site <site_name> install-app client_theme
   ```

2. **Build Client Bundles**:
   Ensure Node is on `PATH`:
   ```bash
   export PATH=$PATH:$HOME/.nvm/versions/node/$(ls $HOME/.nvm/versions/node 2>/dev/null | tail -n 1)/bin
   bench build --app client_theme
   ```

3. **Migrate Site & Apply Database Branding**:
   ```bash
   bench --site <site_name> migrate
   ```

4. **Restart Bench Services**:
   ```bash
   bench restart
   ```

5. **Optional Site Config Keys**:
   The support portal and email defaults are baked directly into code (`client_theme/boot.py`), so no `site_config.json` keys are required. However, you can optionally override them per site:
   * `b1_support_email`: Custom support mailbox (defaults to `bcoredigitalservices@gmail.com`; currently set to `bcoredigitalservices@gmail.com` in `site_config.json`)
   * `b1_support_url`: Custom support portal URL (defaults to `https://bcore.digital/support`; currently set to `https://bcore.digital/support` in `site_config.json`)
   * `b1_client_name`: Client name shown in About/Support headers (defaults to `Loyson Groups`)

---

## 2. Branding Code Executed on Every Migrate

The application hooks `after_migrate` in `client_theme/hooks.py` to run `client_theme.branding.apply_branding()`. Every step is wrapped in `_step(...)` ensuring idempotency:

1. `_core_settings`: Sets system brand name to "B-One", hides copyright, sets default mail footer address, disables standard email footers, suppresses update notifications, and sets `allow_error_traceback = 0`.
2. `_email_footer`: Sets clean sender address footer ("Sent by B-One — B-Core Digital Services") on outgoing email accounts without creating or overwriting existing accounts.
3. `_property_setters`: Idempotently applies 23 custom `Property Setter` records overriding DocField labels and descriptions to eliminate ERPNext/Frappe references and clean up dangling documentation links.
4. `rebrand_onboarding_steps`: Replaces any remaining brand text in onboarding step definitions.
5. `seed_tiles`: Populates default B-One apps-screen navigation tiles in `B-One Settings` if empty.
6. `rebrand_labels`: Rebrands workspace titles (e.g., renames "ERPNext Settings" display title to "Business Setup") and standard doctype labels.
7. `rebrand_settings_and_links`: Cleans descriptions, portal settings, and navigation links.

---

## 3. Local-Only Database Records (Audit from Development Bench)

Most of the 144 Property Setters and 12 Custom Fields in the development bench database (`client.local`) are standard records created automatically by Frappe and ERPNext when installed, so a clean new server gets them automatically upon app installation.

Only **4 custom records** in the local database are truly custom local creations:

| Record Type | Record Name | DocType / Purpose | Deployment Status |
|---|---|---|---|
| **Letter Head** | `Company Letterhead Report` | Letter Head | Not shipped; recreate manually if the client needs them. |
| **Letter Head** | `Company Letterhead` | Letter Head | Not shipped; recreate manually if the client needs them. |
| **Print Format** | `IRS 1099 Form` | Custom Print Format for `Supplier` (`standard = 'No'`) | Not shipped; recreate manually if the client needs them. |
| **Email Template** | `Dispatch Notification` | Email Template | Not shipped; recreate manually if the client needs them. |

*Note: Server Scripts, Client Scripts, Custom HTML Blocks, Web Pages, Dashboard Charts, Number Cards, and Custom Roles have zero custom local records.*

---

## 4. Go-Live Gate (Checklist Section 15 Summary)

Before opening the site to client users, execute and verify every step of the Section 15 Go-Live Gate:

- [ ] **Developer Mode OFF**: Disable developer mode on the production site so internal development tools and the "For app" layer scope option in Manage Sidebar/Dock do not appear to end users:
  ```bash
  bench --site <site_name> set-config developer_mode 0
  ```
- [ ] **Outgoing Email Account Configured**: Configure and enable the client's own outgoing `Email Account` with live SMTP host, port, credentials, and SSL/TLS. (Without an active SMTP account, no outgoing emails or password resets will send).
- [ ] **Credential & Secret Rotation**: Rotate sensitive secrets from development printouts:
  * Update MariaDB user password (`db_password`) in `site_config.json` and in MariaDB.
  * Rotate `flow_server_secret` and any temporary API/encryption secrets in `site_config.json`.
- [ ] **Clean Test Data & Production Admin**:
  * Purge test transactions, mock customers, and demo vouchers created during testing.
  * Update `Administrator` user profile with the client's real production contact email.
- [ ] **Brand Scanner**: Verify database cleanliness:
  ```bash
  bench --site <site_name> execute client_theme.scan_brand.run
  ```
  Reports only 1 known permitted record (`[ERPNext Integrations]`).
- [ ] **Console Link Audit**: In browser DevTools console on `/desk`, a list view, a form view, and with user avatar menu open, run:
  ```javascript
  [...document.querySelectorAll('a[href]')].map(a => a.href).filter(h => /frappe|erpnext/i.test(h))
  ```
  Returns `[]` (empty array).
- [ ] **Manage Sidebar Save**: Open *Edit Sidebar* / *Manage Sidebar*. The layer dropdown shows **"For B-One"**. Reordering items and clicking *Save* completes without errors or hanging.
- [ ] **Email Masthead & Footer**: Outgoing test email displays an absolute logo URL in the masthead and exactly one line in footer: `Sent by B-One — B-Core Digital Services`.
- [ ] **Tracebacks Suppressed**: `allow_error_traceback = 0` is active. Staff diagnose errors via the `Error Log` doctype (`/desk/error-log`).
- [ ] **Role Permissions Restricted**: Restrict client user roles from accessing the "Business Setup" (ERPNext Settings) workspace and developer tools.
- [ ] **Backup, Production Build & Restart**:
  ```bash
  bench --site <site_name> backup --with-files
  bench build --app client_theme --production
  bench restart
  ```
- [ ] **Git Commit & Tag**: Ensure repository working directory is clean, changes committed, and tagged (e.g. `b-one-whitelabel-v1`).

---

## 5. Cannot-Be-Hidden List (Final)

| Surface | Exact Leak | Reason & Mitigation |
|---|---|---|
| **Global Search / Module List** | `[ERPNext Integrations]` Module Def | Primary key in MariaDB table `tabModule Def`. Cannot rename without breaking standard Python module imports. Restrict Setup access from end-user roles. |
| **Awesome Bar / Search History** | Workspace record name `ERPNext Settings` | The primary key remains `ERPNext Settings` (display title is "Business Setup"). Appears in Ctrl+K search if user has Setup permissions. Mitigate by restricting Setup workspace access for client roles. |
| **Browser Address Bar** | URL slug `/desk/setup/erpnext-settings` | Route derived from primary key. Display title in desk is "Business Setup". |
| **DevTools Network Tab** | API endpoints `/api/method/erpnext.*` | Underlying Python RPC routes. Invisible in normal user browsing. |
| **DevTools Network Tab** | Static assets `/assets/frappe/...`, `/assets/erpnext/...` | Web server static bundle directory paths. Invisible in normal UI. |
| **Mail Client "Show Original"** | Email header `X-Frappe-Site: client.local` | Standard framework MIME header visible only in raw source headers. Never visible in email body or client header view. |

