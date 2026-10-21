# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint

from fleetix.transaction.doctype.vehicle_assignment.vehicle_assignment import LIVE


class VehicleHandover(Document):
	def on_submit(self):
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		if cint(self.odometer) > cint(vehicle.last_odometer):
			vehicle.last_odometer = self.odometer
			vehicle.save()
		if self.handover_type != "Return":
			return
		for name in frappe.get_all(
			"Vehicle Assignment",
			filters={"vehicle": self.vehicle, "docstatus": 1, "status": ("in", LIVE)},
			pluck="name",
		):
			frappe.get_doc("Vehicle Assignment", name).end()
