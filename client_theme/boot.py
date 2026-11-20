import frappe

# Brand facts shown in the About and Support dialogs. Override per site without code changes:
#   bench --site <site> set-config b1_support_email "support@bcore.digital"
#   bench --site <site> set-config b1_support_url "https://bcore.digital/support"
# Support mailbox confirmed and final.
VENDOR = "B-Core Digital"
WEBSITE = "https://bcore.digital"
SUPPORT_EMAIL = "support@bcore.digital"
SUPPORT_URL = "https://bcore.digital/support"
CLIENT = "I2 Techno Solutions"


def _parse_roles(value):
	"""Roles are typed one per line (commas also accepted)."""
	return [r.strip() for r in (value or "").replace(",", "\n").splitlines() if r.strip()]


def _brand():
	try:
		from client_theme import __version__ as version
	except Exception:
		version = ""
	return {
		"name": "B-One",
		"vendor": VENDOR,
		"website": WEBSITE,
		"client": frappe.conf.get("b1_client_name") or CLIENT,
		"version": version,
		"support_email": frappe.conf.get("b1_support_email") or SUPPORT_EMAIL,
		"support_url": frappe.conf.get("b1_support_url") or SUPPORT_URL,
	}


def extend_bootinfo(bootinfo):
	"""Send brand info and this user's apps-screen tiles to the desk.

	Must never raise: an error here would block every login, so on any problem we log it
	and let the desk fall back to its built-in defaults.
	"""
	try:
		bootinfo.b1_brand = _brand()
		bootinfo.show_new_navigation_prompt = False
	except Exception:
		frappe.log_error(title="B-One: brand boot info failed")

	try:
		if frappe.session.user == "Guest" or not frappe.db.exists("DocType", "B-One Settings"):
			return
		rows = frappe.get_cached_doc("B-One Settings").get("tiles") or []
		if not rows:
			return  # not configured yet: the desk falls back to built-in defaults

		user_roles = set(frappe.get_roles())
		tiles = []
		for row in rows:
			if not row.enabled:
				continue
			allowed = _parse_roles(row.roles)
			if allowed and not user_roles.intersection(allowed):
				continue
			tiles.append(
				{
					"title": row.title,
					"module": row.module,
					"route": row.route,
					"icon": row.icon,
					"custom_icon": row.custom_icon,
				}
			)
		bootinfo.b1_tiles = tiles
	except Exception:
		frappe.log_error(title="B-One: extend_bootinfo failed")