# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Repair(Document):
	def on_update(self):
		if self.status == "In Workshop" and frappe.db.get_value("Car", self.car, "status") != "Repair":
			car = frappe.get_doc("Car", self.car)
			car.status = "Repair"
			car.save()
