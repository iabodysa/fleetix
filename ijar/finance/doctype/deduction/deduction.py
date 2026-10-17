# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Deduction(Document):
	def before_submit(self):
		self.status = "Deducted"

	def on_submit(self):
		self.update_advance()

	def on_cancel(self):
		self.update_advance()

	def update_advance(self):
		if self.advance:
			frappe.get_doc("Advance", self.advance).save()
