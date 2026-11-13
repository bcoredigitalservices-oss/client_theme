# B-One White-Label — Round 5 Report (12 Nov 2026)

> All edits are strictly inside `apps/client_theme`. No Frappe or ERPNext core files were touched.
> Commit: `56ebbb2`  Branch: `develop`

---

## Git Diff Summary

```
 client_theme/branding.py                    | 144 ++++++++++++++--
 client_theme/public/js/whitelabel.bundle.js |   4 +-
 client_theme/B-One_Changes_12Nov2026.md     | deleted (moved to docs/)
 docs/B-One_Changes_12Nov2026.md             | 166 +++++++++++++++++++ (new location)
 docs/B-One_Changes_12Nov2026_1.md           | 166 +++++++++++++++++++ (new location)
 6 files changed, 460 insertions(+), 277 deletions(-)
```

---

## Item-by-Item Status

### Items 1 & 2 — Email Account seeding removed; footer appears exactly once  DONE

Root cause: `_email_footer()` seeded "B-One Notifications" (vendor Gmail, no SMTP)
and also set `Email Account.footer` = B-One HTML. The result was `email_account_footer` block AND
`sender_address` block both carrying the B-One line — the footer appeared TWICE. The queue records
`q8the17lr6`, `pi4bu9fbv2`, `sbjej9fitr` all errored because `get_smtp_server()` rejected the
account (no SMTP config).

Fix (`branding.py` -> `_email_footer()`):

| Before | After |
|---|---|
| Seeds "B-One Notifications" Email Account | Never creates any Email Account |
| Sets `Email Account.footer` = B-One HTML on every account | Clears footer only when it still mentions ERPNext or Frappe (never writes B-One text into accounts) |
| Sets `email_footer_address` default | Kept — renders once from `sender_address` block |
| `default_mail_footer` not explicitly cleared | Now explicitly set to `""` |

DB changes (applied now, idempotent on future migrate):
- Deleted Email Queue records: `q8the17lr6`, `pi4bu9fbv2`, `sbjej9fitr` → count now 0
- Deleted Email Account "B-One Notifications" → no Email Accounts remain
- `email_footer_address` = "Sent by B-One — B-Core Digital Services"
- `default_mail_footer` = ""
- `disable_standard_email_footer` = "1"

Footer result — `get_footer(email_account=None)`:
```
email_account_footer block: (empty — no account)
sender_address block:        "Sent by B-One — B-Core Digital Services"
default_mail_footer block:   (empty)
```
B-One line appears exactly once.

Manual tests: #7 (password-reset email branding)

---

### Item 3 — Manage Sidebar "For B-One" saves forever — fixed  DONE

Root cause confirmed by reading `sidebar_manager.js`:
- The `app` layer's label is `__("For {0}", [this.app_of_sidebar()])` where `app_of_sidebar()`
  returns the Frappe app name (e.g. `"erpnext"`).
- The DOM scrubber rewrote the rendered `<option>` text `"For erpnext"` to `"For B-One"`.
- When the user chose "For B-One" and hit Save, the layer switch read the scrubbed text "B-One"
  not the original key `"erpnext"`. The API call `save_app_sidebar` received the wrong app name
  and timed out / spun forever.

Note: `SIDEBAR_LAYERS.app` already has `condition: () => !!frappe.boot.developer_mode`, so this
option is hidden in production. The scrubber was rewriting it unnecessarily.

Fix (`whitelabel.bundle.js`): added `select, option` to `SCRUB_SKIP`.

```js
// Before
const SCRUB_SKIP = "input, textarea, pre, code, ...";
// After
const SCRUB_SKIP = "input, textarea, select, option, pre, code, ...";
```

`<select>` and `<option>` elements carry machine-readable values and option keys — scrubbing them
breaks lookup logic. "Just for me" and "For everyone" are plain text siblings unaffected by this.

Manual tests: #3 (Manage Sidebar — all three scopes work)

---

### Item 4 — False text in descriptions  DONE

| Field | Old (wrong) | New (correct) |
|---|---|---|
| `Security Settings.public_contacts` | "… Defaults to `https://security.b-one.local`" | "Website, email or phone where vulnerabilities can be reported." |
| `Security Settings.public_policy` | "… Defaults to `https://b-one.local/security`" | "Guidelines and policies on vulnerability reporting." |
| `Website Settings.subdomain` | "Sub-domain provided by b-one.com" | "" (blank) |
| `OAuth Client.redirect_uris` | `b_one.integrations.oauth2_logins…` | `<app>.integrations.oauth2_logins…` |
| `OAuth Settings.allowed_public_client_origins` | `https://b-one.com` | `https://example.com` |

Rule: Never replace the brand word inside a URL or dotted code path with B-One.

---

### Item 5 — Dead sentences after link strip  DONE

| Field | Old (dangling) | New |
|---|---|---|
| `User.generate_keys` | "Click here to learn about token-based authentication" | "" |
| `Web Form.custom_css` | "For help see Web Form Custom CSS" | "" |
| `Web Form.client_script` | "For help see Client Script API and Examples" | "" |
| `Accounts Settings.enable_common_party_accounting` | "Learn about Common Party" | "" |

Rule: If stripping a link leaves a dangling pointer to it, blank the whole description.

---

### Item 6 — Name clash: "B-One Settings" workspace → "Business Setup"  DONE

Fix (`branding.py` -> `rebrand_labels()`): after the generic loop, a special-case block sets
`label = "Business Setup"` and `title = "Business Setup"` on the `"ERPNext Settings"` workspace.
Record name and URL slug stay as `"ERPNext Settings"` / `/desk/setup/erpnext-settings`.

Verified:
```
frappe.db.get_value("Workspace", "ERPNext Settings", ["label", "title"])
# → ["Business Setup", "Business Setup"]
```

---

### Item 7 — Notes moved out of the Python package  DONE

```
client_theme/B-One_Changes_12Nov2026.md   → docs/B-One_Changes_12Nov2026.md
client_theme/B-One_Changes_12Nov2026_1.md → docs/B-One_Changes_12Nov2026_1.md
```

---

### Item 8 — Unreported items  DONE

#### (a) 404, 403 and 500 error pages

- **404**: No user-visible "ERPNext" or "Frappe" text. All hits are HTML comments and asset paths
  (not rendered). PASS.
- **403**: Frappe renders a login redirect for protected pages. NOT POSSIBLE to reach a 403 page
  anonymously. Support team can verify by accessing a restricted document while logged in.
  Frappe's 403 template carries no brand text.
- **500**: Controlled by `allow_error_traceback = 0`. Browser popup shows only the user-friendly
  message. The raw WSGI 500 page has no brand text.

#### (b) Email body brand scan

Three Email Queue records scanned. Only "Frappe" hits: `X-Frappe-Site: http://client.local:8000`
in the raw MIME header — visible only via "Show original" in a mail client, not in the message body.
No ERPNext or Frappe text in subject, body, or any user-visible part.

> Cannot be hidden: `X-Frappe-Site` raw email header. Visible only in "Show original".

#### (c) PDF output

Confirmed from Round 3–4 report:
- PDF engine: PlutoPrint / Chrome (from `Print Settings.pdf_generator`).
- `get_print('Company', 'Loyson Groups Nigeria Ltd')` — no user-visible ERPNext/Frappe text.
- Sales Invoice and Purchase Order print previews are clean (same template as PDF).

#### (d) Cannot-be-hidden list

| Item | Where visible | Mitigation |
|---|---|---|
| Module record name `[ERPNext Integrations]` | Ctrl+K / module search | Primary key — cannot rename. Restrict Setup access for client. |
| API paths `/api/method/erpnext.*` | Browser DevTools Network tab | Server-side endpoints — not user-facing. |
| Workspace record name `ERPNext Settings` | Ctrl+K results, search history | Display is now "Business Setup". Restrict Setup access. |
| URL slug `/desk/setup/erpnext-settings` | Browser address bar | Record name cannot change without breaking navigation. Restrict access. |
| Raw email header `X-Frappe-Site` | "Show original" in mail client only | Frappe core header; not visible in normal mail reading. |
| HTML comment `<!-- Built on Frappe. -->` | Browser "View source" on website pages | Hidden comment; not rendered. |
| Asset paths `/assets/frappe/…`, `/assets/erpnext/…` | Browser DevTools / View source | Server paths; not shown to end users. |

---

### Item 9 — `allow_error_traceback = 0`  DONE

Applied by `_core_settings()` in `branding.py` on every migrate.

Where the support team reads tracebacks: `Desk → Logs → Error Log` (`/app/error-log`).
Full tracebacks are always written to the Error Log regardless of this setting — only the in-browser
display is suppressed.

---

## Manual Tests Applicable

| Test | Item | Expected |
|---|---|---|
| #3 | Sidebar "For B-One" spin | "Just for me" and "For everyone" save without spin; "For [app]" absent in non-dev mode |
| #7 | Password-reset email footer | B-One line appears exactly once; no SMTP error |
| #4 | Field descriptions | `generate_keys`, `custom_css`, `client_script`, `enable_common_party_accounting` blank; `redirect_uris` shows `<app>.integrations…`; `allowed_public_client_origins` shows `https://example.com` |
| #6 | Workspace label | Sidebar and Ctrl+K show "Business Setup", not "B-One Settings" |
| #8 | PDF download | No ERPNext/Frappe in visible PDF content |
| #9 | Error Log | Tracebacks in Error Log; not shown in browser popup |

