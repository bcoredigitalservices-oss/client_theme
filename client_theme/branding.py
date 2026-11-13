"""One place for B-One's brand values. Runs on install and after every migrate (idempotent)."""

import frappe

BRAND = "B-One"
MARK = "/assets/client_theme/images/logo-mark-clean.svg"

# (module / Sidebar name, title, icon, roles). Seeded once into B-One Settings; after that the
# table in the Desk is the source of truth and is never overwritten.
DEFAULT_TILES = [
	("Accounts", "Finance", "finance", ""),
	("Selling", "Sales", "sales", ""),
	("CRM", "CRM", "crm", ""),
	("Buying", "Procurement", "procurement", ""),
	("Stock", "Inventory", "inventory", ""),
	("Manufacturing", "Manufacturing", "manufacturing", ""),
	("Projects", "Projects", "projects", ""),
	("Assets", "Assets", "assets", ""),
	("Quality", "Quality", "quality", ""),
	("Support", "Support", "support", ""),
	("Setup", "Settings", "settings", "System Manager"),
]


def _core_settings():
	frappe.db.set_single_value("Navbar Settings", "app_logo", MARK)
	for field, value in {
		"app_name": BRAND,
		"favicon": MARK,
		"splash_image": MARK,
		"app_logo": MARK,
		"footer_powered": " ",
	}.items():
		frappe.db.set_single_value("Website Settings", field, value)
	frappe.db.set_single_value("System Settings", "app_name", BRAND)

	# The onboarding panel shows the ERPNext logo and a Frappe video; turn it off.
	if frappe.get_meta("System Settings").has_field("enable_onboarding"):
		frappe.db.set_single_value("System Settings", "enable_onboarding", 0)

	# Restrict error tracebacks from exposing internal app code paths
	if frappe.get_meta("System Settings").has_field("allow_error_traceback"):
		frappe.db.set_single_value("System Settings", "allow_error_traceback", 0)

	# Suppress system update popups linking to GitHub releases
	if frappe.get_meta("System Settings").has_field("disable_system_update_notification"):
		frappe.db.set_single_value("System Settings", "disable_system_update_notification", 1)


def _step(fn):
	"""Run one branding step. A failure is logged and printed, and the remaining steps still run."""
	try:
		fn()
	except Exception:
		frappe.log_error(title=f"B-One branding: {fn.__name__} failed")
		print(f"B-One branding: {fn.__name__} failed (see Error Log)")


def apply_branding():
	for fn in (
		_core_settings,
		_email_footer,
		_property_setters,
		rebrand_onboarding_steps,
		seed_tiles,
		rebrand_labels,
		rebrand_settings_and_links,
	):
		_step(fn)
	frappe.clear_cache()


def seed_tiles():
	if not frappe.db.exists("DocType", "B-One Settings"):
		return
	settings = frappe.get_doc("B-One Settings")
	if settings.tiles:
		return
	for module, title, icon, roles in DEFAULT_TILES:
		settings.append("tiles", {"enabled": 1, "module": module, "title": title, "icon": icon, "roles": roles})
	settings.flags.ignore_permissions = True
	settings.save()


# Visible labels on standard records that still say "ERPNext". Re-applied after every migrate because
# standard records are re-synced from the app JSON. Only these label fields are touched, and only when
# they contain the word. Record names (and so URL slugs) are left alone on purpose.
LABEL_FIELDS = {
	"Workspace": ("label", "title"),
	"Workspace Sidebar": ("title",),
	"Desktop Icon": ("label",),
	"Module Onboarding": ("title",),
}


def rebrand_labels():
	for doctype, fields in LABEL_FIELDS.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		meta = frappe.get_meta(doctype)
		for field in fields:
			if not meta.has_field(field):
				continue
			rows = frappe.db.sql(
				f"select name, `{field}` from `tab{doctype}` where `{field}` like %s", ("%ERPNext%",)
			)
			for name, value in rows:
				frappe.db.set_value(
					doctype, name, field, (value or "").replace("ERPNext", BRAND), update_modified=False
				)

	# R5-Item-6: The workspace whose record name is "ERPNext Settings" (URL slug stays
	# /desk/setup/erpnext-settings) now carries label/title "B-One Settings" from the loop
	# above. But that title clashes with the "B-One Settings" doctype. Rename it to
	# "Business Setup" as a special case — label and title only, never the record name.
	if frappe.db.exists("DocType", "Workspace") and frappe.db.exists("Workspace", "ERPNext Settings"):
		frappe.db.set_value(
			"Workspace", "ERPNext Settings",
			{"label": "Business Setup", "title": "Business Setup"},
			update_modified=False,
		)


DOC_URL_PATTERNS = ("%docs.frappe.io%", "%docs.erpnext.com%", "%frappe.io%", "%erpnext.com%", "%frappeframework.com%")


def rebrand_settings_and_links():
	"""Fixes for what the database scan found. Idempotent; re-applied after every migrate."""
	# The name an authenticator app shows for two-factor codes.
	if frappe.get_meta("System Settings").has_field("otp_issuer_name"):
		frappe.db.set_single_value("System Settings", "otp_issuer_name", BRAND)

	# Help-menu item that pointed at frappe.io/support: now an in-app action opening B-One's Support dialog.
	if frappe.db.exists("DocType", "Navbar Item"):
		meta = frappe.get_meta("Navbar Item")
		rows = frappe.db.sql("select name from `tabNavbar Item` where item_label like %s", ("%Frappe Support%",))
		for (name,) in rows:
			values = {"item_label": "Support"}
			if meta.has_field("item_type"):
				values["item_type"] = "Action"
			if meta.has_field("action"):
				values["action"] = "frappe.ui.toolbar.b1_support()"
			if meta.has_field("route"):
				values["route"] = ""
			frappe.db.set_value("Navbar Item", name, values, update_modified=False)

	# 'Documentation' links on reports and doctypes that open docs.frappe.io / docs.erpnext.com.
	for doctype, field in (("Report", "documentation_url"), ("DocType", "documentation")):
		if not frappe.db.exists("DocType", doctype) or not frappe.get_meta(doctype).has_field(field):
			continue
		condition = " or ".join([f"`{field}` like %s"] * len(DOC_URL_PATTERNS))
		frappe.db.sql(f"update `tab{doctype}` set `{field}` = '' where {condition}", DOC_URL_PATTERNS)



def _email_footer():
	"""Disable ERPNext's standard footer line; set the global email_footer_address default.

	Rule (Round 5): branding.py must NEVER create Email Accounts.
	Rule: for existing accounts, only clear a footer that mentions ERPNext or Frappe — do not
	      write the B-One text into accounts.  The global default (email_footer_address) renders
	      even with no Email Account, so the B-One line appears exactly once from sender_address.
	"""
	frappe.db.set_default("disable_standard_email_footer", "1")
	# The global default renders in the sender_address block of every outgoing message.
	# We deliberately do NOT write this into Email Account.footer to avoid the footer appearing
	# twice (email_account_footer block + sender_address block).
	frappe.db.set_default("email_footer_address", "Sent by B-One — B-Core Digital Services")
	# Keep default_mail_footer empty so the third block is also empty.
	frappe.db.set_default("default_mail_footer", "")

	if frappe.db.exists("DocType", "Email Account"):
		accounts = frappe.get_all("Email Account", fields=["name", "footer", "default_outgoing"])
		for acc in accounts:
			updates = {}
			# Only clear footers that mention ERPNext or Frappe — never write B-One text in.
			if acc.footer and ("ERPNext" in acc.footer or "Frappe" in acc.footer):
				updates["footer"] = ""
			if frappe.get_meta("Email Account").has_field("frappe_mail_site"):
				updates["frappe_mail_site"] = ""
			if updates:
				frappe.db.set_value("Email Account", acc.name, updates, update_modified=False)


# ---------------------------------------------------------------------------
# Property Setters — override field labels and descriptions from ERPNext/Frappe
# DocFields without editing core JSON. Idempotent: re-applied after every migrate.
# ---------------------------------------------------------------------------

# (doctype, fieldname, property, property_type, new_value)
_PROPERTY_SETTERS = [
	# Field labels visible to end-users
	("Employee Group Table",     "user_id",                               "label",       "Data",       "B-One User ID"),
	("CRM Settings",             "frappe_crm_section",                    "label",       "Data",       "B-One CRM"),
	("CRM Settings",             "enable_frappe_crm_data_synchronization", "label",      "Data",       "Enable B-One CRM Data Synchronization"),
	("Email Account",            "frappe_mail_site",                      "label",       "Data",       "Mail Site"),
	("Email Account",            "validate_frappe_mail_settings",         "label",       "Data",       "Validate Mail Settings"),
	("Studio App",               "frappe_app",                            "label",       "Data",       "App (for export)"),
	("Studio Page",              "frappe_app",                            "label",       "Data",       "App (for export)"),
	("System Settings",          "frappectl_section",                     "label",       "Data",       "CLI Settings"),

	# Descriptions visible to users / admins (R5: corrected; rule = never invent URLs or dotted paths)
	("Item",                     "is_stock_item",                         "description", "Small Text",
	 "B-One will make a stock ledger entry for each transaction of this item. Keep unchecked for non-stock or service items."),
	("Production Plan",          "skip_available_sub_assembly_item",       "description", "Small Text",
	 "If enabled, formula for <b>Qty to Order</b>: <br>\nRequired Qty (BOM) - Projected Qty. <br> This helps avoid over-ordering."),
	("Production Plan",          "ignore_existing_ordered_qty",           "description", "Small Text",
	 "If enabled, formula for <b>Required Qty</b>: <br>\nRequired Qty (BOM) - Projected Qty. <br> This helps avoid over-ordering."),
	# R5-Item-5: stripping the link leaves a dangling pointer — blank the whole description.
	("Accounts Settings",        "enable_common_party_accounting",        "description", "Small Text", ""),
	# R5-Item-4: drop the invented "Defaults to ..." sentence; keep only the factual opening.
	("Security Settings",        "public_contacts",                       "description", "Small Text",
	 "Website, email or phone where vulnerabilities can be reported."),
	("Security Settings",        "public_policy",                         "description", "Small Text",
	 "Guidelines and policies on vulnerability reporting."),
	# R5-Item-5: dangling pointer after link strip — blank.
	("User",                     "generate_keys",                         "description", "Small Text", ""),
	("Web Form",                 "is_standard",                           "description", "Small Text",
	 "If enabled, B-One exports the form to the module folder."),
	# R5-Item-5: dangling pointers — blank.
	("Web Form",                 "custom_css",                            "description", "Small Text", ""),
	("Web Form",                 "client_script",                         "description", "Small Text", ""),
	# R5-Item-4: subdomain description invents b-one.com — blank it.
	("Website Settings",         "subdomain",                             "description", "Small Text", ""),
	# R5-Item-4: use the real Frappe module path in the example; never invent a b_one. module.
	("OAuth Client",             "redirect_uris",                         "description", "Small Text",
	 "URIs for receiving authorization code once the user allows access, as well as failure responses. Typically a REST endpoint exposed by the Client App.\n<br>e.g. http://hostname/api/method/<app>.integrations.oauth2_logins.login_via_facebook"),
	# R5-Item-4: use a neutral example URL.
	("OAuth Settings",           "allowed_public_client_origins",         "description", "Small Text",
	 "New line separated list of allowed public client URLs (eg <code>https://example.com</code>), or <code>*</code> to accept all.\n<br>\nPublic clients are restricted by default."),
	("BOM Creator Item",         "model_file",                            "description", "Small Text",
	 "STEP, STL or GLB file of a material added in B-One, used to place it in the 3D model."),
	("SMS Settings",             "parameters",                            "description", "Small Text",
	 "Enter static url parameters here (Eg. sender=B-One, username=B-One, password=1234 etc.)"),
]


def _property_setters():
	"""Create or update Property Setter records to override ERPNext/Frappe field metadata."""
	if not frappe.db.exists("DocType", "Property Setter"):
		return

	for doctype, fieldname, prop, prop_type, value in _PROPERTY_SETTERS:
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
				"property_type":    prop_type,
				"value":            value,
			}).insert(ignore_permissions=True, ignore_if_duplicate=True)

		# Also sync tabDocField directly so database scans reflect the change
		frappe.db.sql(
			f"update `tabDocField` set `{prop}` = %s where parent = %s and fieldname = %s",
			(value, doctype, fieldname),
		)


def rebrand_onboarding_steps():
	"""Strip frappe/erpnext doc links and replace ERPNext references in Onboarding Steps."""
	if not frappe.db.exists("DocType", "Onboarding Step"):
		return

	# Fix "before using ERPNext" -> "before using B-One"
	frappe.db.sql(
		"update `tabOnboarding Step` set description = replace(description, 'ERPNext', %s) "
		"where description like %s",
		(BRAND, "%ERPNext%"),
	)

	# Strip "See [Topic](https://docs.frappe.io/...)" markdown links from descriptions
	import re
	link_re = re.compile(
		r"\s*See\s+\[[^\]]+\]\(https?://(?:docs\.frappe\.io|frappe\.io|erpnext\.com)[^\)]*\)\.?",
		re.IGNORECASE,
	)
	rows = frappe.db.sql(
		"select name, description from `tabOnboarding Step` where description like %s or description like %s",
		("%docs.frappe.io%", "%frappe.io%"),
		as_dict=True,
	)
	for r in rows:
		clean = link_re.sub("", r.description or "").strip()
		if clean != r.description:
			frappe.db.set_value("Onboarding Step", r.name, "description", clean, update_modified=False)
