# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from fleetix.fleetix.vehicle import parse_fieldnames


class FleetixSettings(Document):
	def validate(self):
		meta = frappe.get_meta("Vehicle")
		unknown = [f for f in parse_fieldnames(self.vehicle_required_fields) if not meta.has_field(f)]
		if unknown:
			frappe.throw(_("These are not Vehicle fields: {0}").format(", ".join(unknown)))
