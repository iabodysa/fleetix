# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class Handover(Document):
	def before_submit(self):
		self.status = "Delivered"

	def on_submit(self):
		permit = frappe.get_doc(
			{
				"doctype": "Permit",
				"handover": self.name,
				"car": self.car,
				"staff": self.staff,
				"deal": self.deal,
				"firm": self.firm,
				"from_date": getdate(self.handover_date),
			}
		)
		permit.insert()
		permit.submit()
		car = frappe.get_doc("Car", self.car)
		car.update({"status": "Leased", "deal": self.deal, "staff": self.staff})
		car.save()
