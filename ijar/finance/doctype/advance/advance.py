# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Advance(Document):
	def validate(self):
		self.set_balance()

	def before_update_after_submit(self):
		self.set_balance()

	def set_balance(self):
		deducted = 0 if self.is_new() else sum(
			frappe.get_all("Deduction", filters={"advance": self.name, "docstatus": 1}, pluck="amount")
		)
		self.balance = flt(self.amount) - flt(deducted)
		if self.docstatus == 1:
			self.status = "Recovered" if self.balance <= 0 else "Open"
