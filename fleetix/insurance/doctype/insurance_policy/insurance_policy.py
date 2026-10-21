# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InsurancePolicy(Document):
	def on_update(self):
		current = None if self.status == "Expired" else self.name
		for row in self.vehicles:
			vehicle = frappe.get_doc("Vehicle", row.vehicle)
			if vehicle.insurance_policy == current or (not current and vehicle.insurance_policy != self.name):
				continue
			vehicle.insurance_policy = current
			vehicle.save()
