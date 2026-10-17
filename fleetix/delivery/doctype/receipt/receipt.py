# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class Receipt(Document):
	def validate(self):
		if not self.permit:
			self.permit = frappe.db.get_value("Permit", {"handover": self.handover, "docstatus": 1})

	def before_submit(self):
		self.status = "Damaged" if self.damaged else "Received"

	def on_submit(self):
		if self.permit:
			permit = frappe.get_doc("Permit", self.permit)
			permit.update({"to_date": getdate(self.receipt_date), "status": "Cancelled"})
			permit.save()
		handover = frappe.get_doc("Handover", self.handover)
		handover.status = "Returned"
		handover.save()
		car = frappe.get_doc("Car", self.car)
		car.update({"status": "Available", "deal": None, "staff": None})
		car.save()
