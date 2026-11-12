from frappe.www.login import get_context as _core_get_context
from frappe.www.login import no_cache  # noqa: F401  (Frappe reads this module attribute)


def get_context(context):
	# Core handles auth context, redirects for logged-in users, social/LDAP/signup flags
	context = _core_get_context(context)
	context.full_width = True
	context.no_breadcrumbs = True
	return context
