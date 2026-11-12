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
	for field, value in {"app_name": BRAND, "favicon": MARK, "splash_image": MARK, "app_logo": MARK}.items():
		frappe.db.set_single_value("Website Settings", field, value)
	frappe.db.set_single_value("System Settings", "app_name", BRAND)

	# The onboarding panel shows the ERPNext logo and a Frappe video; turn it off.
	if frappe.get_meta("System Settings").has_field("enable_onboarding"):
		frappe.db.set_single_value("System Settings", "enable_onboarding", 0)


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
	"""Disable the standard Frappe email footer so our hook-supplied B-One footer is the only one."""
	frappe.db.set_default("disable_standard_email_footer", "1")


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
	("Item",           "is_stock_item",   "description",
	 "B-One will make a stock ledger entry for each transaction of this item."
	 " Keep unchecked for non-stock or service items."),
	("BOM Creator Item", "file",          "description",
	 "STEP, STL or GLB file of a material added in B-One, used to place it in the 3D model."),
	("SMS Settings",   "sms_parameters",  "description",
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
