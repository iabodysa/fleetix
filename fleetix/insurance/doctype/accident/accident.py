# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Accident(Document):
	def on_submit(self):
		car = frappe.get_doc("Car", self.car)
		car.status = "Accident"
		car.save()
