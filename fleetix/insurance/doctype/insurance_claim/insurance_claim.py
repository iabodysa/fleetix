# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InsuranceClaim(Document):
	def after_insert(self):
		frappe.db.set_value("Accident", self.accident, "insurance_claim", self.name, update_modified=False)
