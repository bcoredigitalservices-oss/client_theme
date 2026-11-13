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

## 3. Post-Upgrade Verification Checklist
After pulling updates to Frappe or ERPNext:
1. Run each `diff` command above to inspect upstream changes.
2. If upstream modified markup outside branding lines, re-apply upstream structural updates while keeping the branding overrides.
3. Re-run:
   ```bash
   bench build --app client_theme
   bench --site client.local migrate
   bench --site client.local execute client_theme.scan_brand.run
   ```
