# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint

from fleetix.fleetix.doctype.vehicle_assignment.vehicle_assignment import LIVE


class VehicleHandover(Document):
	def on_submit(self):
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		if cint(self.odometer) > cint(vehicle.last_odometer):
			vehicle.last_odometer = self.odometer
			vehicle.flags.ignore_mandatory = True
			vehicle.save()
		if self.handover_type == "Handover":
			self.deliver_assignment()
		elif self.handover_type == "Return":
			for name in frappe.get_all(
				"Vehicle Assignment",
				filters={"vehicle": self.vehicle, "docstatus": 1, "status": ("in", LIVE)},
				pluck="name",
			):
				frappe.get_doc("Vehicle Assignment", name).end(self.handover_datetime)

	def deliver_assignment(self):
		for name in frappe.get_all(
			"Vehicle Assignment",
			filters={
				"vehicle": self.vehicle,
				"docstatus": 1,
				"status": ("in", LIVE),
				"handover_date": ("is", "not set"),
				**({"driver": self.to_driver} if self.to_driver else {}),
			},
			pluck="name",
		):
			frappe.get_doc("Vehicle Assignment", name).record_handover(self.handover_datetime)
