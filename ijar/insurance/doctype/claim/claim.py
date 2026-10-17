# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Claim(Document):
	def before_submit(self):
		if self.status == "Draft":
			self.status = "Filed"

	def on_submit(self):
		accident = frappe.get_doc("Accident", self.accident)
		accident.status = "Claimed"
		accident.save()
