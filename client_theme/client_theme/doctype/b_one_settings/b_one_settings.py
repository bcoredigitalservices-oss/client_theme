import frappe
from frappe import _
from frappe.model.document import Document


def parse_roles(value: str | None) -> list[str]:
	"""Roles are typed one per line (commas also accepted)."""
	return [r.strip() for r in (value or "").replace(",", "\n").splitlines() if r.strip()]


class BOneSettings(Document):
	def validate(self):
		for row in self.tiles or []:
			if not (row.module or row.route):
				frappe.throw(_("Row {0}: set a Module or a Custom Route.").format(row.idx))
			for role in parse_roles(row.roles):
				if not frappe.db.exists("Role", role):
					frappe.throw(_("Row {0}: Role {1} does not exist.").format(row.idx, frappe.bold(role)))

	def on_update(self):
		# Boot info is cached per user; clear so the new tile list is served on next reload.
		frappe.clear_cache()