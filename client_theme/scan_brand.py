"""Read-only audit: finds 'ERPNext' / 'Frappe' in records stored in the site database.

Run:  bench --site client.local execute client_theme.scan_brand.run
More: bench --site client.local execute client_theme.scan_brand.run --kwargs '{"limit": 200}'

Nothing is changed. A hit is "code" when every mention is a code reference such as
frappe.utils.formatdate(...) or an import path like erpnext/templates/...; those are counted but not
listed. Everything else is a "real" hit: visible text, a docs link, or a frappe.io / erpnext.com URL.
"""

import re

import frappe

# Doctypes whose records can show up in the UI. Missing ones are skipped.
TARGETS = [
	"Workspace", "Workspace Sidebar", "Workspace Sidebar Item", "Workspace Shortcut", "Workspace Link",
	"Desktop Icon", "Desktop Layout", "Dock", "Dock Item", "Module Def", "Module Onboarding",
	"Onboarding Step", "Email Template", "Print Format", "Letter Head", "Notification",
	"Number Card", "Dashboard Chart", "Dashboard", "Custom HTML Block", "Web Page", "Web Form",
	"Website Settings", "System Settings", "Navbar Settings", "Navbar Item", "Email Account",
	"Email Domain", "Print Settings", "Portal Settings", "Report",
	"DocField", "Custom Field", "Property Setter", "Help Article", "Translation",
]

# For these, only the listed fields are checked (scanning every text field would be mostly noise).
FIELD_ONLY = {
	"DocField": ("label", "description"),
	"Custom Field": ("label", "description"),
	"Property Setter": ("value",),
	"Help Article": ("title", "content"),
	"Translation": ("translated_text",),
}

# Internal identifiers, never shown to users.
SKIP_FIELDS = {("Module Def", "app_name")}

# Only field types that are stored as a text column. (HTML, Button and Heading fields have no column.)
TEXT_TYPES = {
	"Data", "Small Text", "Text", "Long Text", "Text Editor", "HTML Editor", "Markdown Editor",
	"Code", "Select", "Link",
}
NEEDLES = ("erpnext", "frappe")

# Code references: frappe.utils.x(), erpnext.demo.clear_demo(), and import paths such as
# erpnext/templates/... . Case-sensitive on purpose, so "Frappe CRM" and docs.frappe.io stay real hits.
CODE = re.compile(
	r"""(?<![\w./-])(?:frappe|erpnext)\.(?!(?:io|com|cloud|school)\b)[a-z_]\w*(?:\.[a-z_]\w*)*
	|(?<![\w./:-])(?:erpnext|frappe)/[\w/.\-]+""",
	re.X,
)


def _is_real(text: str) -> bool:
	return any(n in CODE.sub("", text).lower() for n in NEEDLES)


def _snippet(text: str) -> str:
	low = text.lower()
	idx = min((low.find(n) for n in NEEDLES if n in low), default=0)
	return " ".join(text[max(0, idx - 40) : idx + 60].split())


def _fields_for(dt, meta):
	if dt in FIELD_ONLY:
		names = FIELD_ONLY[dt]
	else:
		names = [f.fieldname for f in meta.fields if f.fieldtype in TEXT_TYPES and not f.is_virtual]
	names = [f for f in names if (dt, f) not in SKIP_FIELDS]
	if not meta.issingle:
		columns = set(frappe.db.get_table_columns(dt))
		names = [f for f in names if f in columns]
	return names


def run(limit=40):
	total_real = total_code = 0
	for dt in TARGETS:
		if not frappe.db.exists("DocType", dt):
			continue
		meta = frappe.get_meta(dt)
		fields = _fields_for(dt, meta)
		if not fields:
			continue

		hits = []
		if meta.issingle:
			for field in fields:
				try:
					value = frappe.db.get_single_value(dt, field)
				except Exception:
					continue
				if isinstance(value, str) and any(n in value.lower() for n in NEEDLES):
					hits.append((dt, field, value))
		else:
			for field in fields:
				try:
					rows = frappe.db.sql(
						f"select name, `{field}` from `tab{dt}` where `{field}` like %s or `{field}` like %s",
						("%erpnext%", "%frappe%"),
					)
				except Exception as e:
					print(f"  (skipped {dt}.{field}: {str(e)[:60]})")
					continue
				hits.extend((name, field, value) for name, value in rows if isinstance(value, str))

		real = [h for h in hits if _is_real(h[2])]
		code = len(hits) - len(real)
		total_real += len(real)
		total_code += code
		if not real and not code:
			continue

		print(f"\n== {dt}: {len(real)} real, {code} code (ignored)")
		for name, field, value in real[:limit]:
			print(f"  [{name}] .{field}: ...{_snippet(value)}...")
		if len(real) > limit:
			print(f"  ... {len(real) - limit} more real hits (raise limit to see them)")

	print(f"\nReal hits: {total_real}    Code references ignored: {total_code}")