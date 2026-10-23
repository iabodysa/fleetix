# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from fleetix.fleetix.doctype.vehicle_assignment.vehicle_assignment import customer_at


class VehicleRequest(Document):
	def validate(self):
		if not self.customer:
			self.customer = customer_at(self.required_date, driver=self.driver)
