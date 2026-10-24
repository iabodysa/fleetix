# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow
from frappe.utils import get_datetime, getdate, now_datetime, today

from fleetix.fleetix.vehicle import policy_intervals

PERMANENT = "Permanent"
INTERVAL_FIELDS = (
	"oil_interval_summer_km",
	"oil_interval_winter_km",
	"tire_interval_km",
	"battery_interval_months",
)
SUBMIT_FIELDS = ("usage_type", "from_datetime")
CONVERTIBLE = ("Active", "Expiring")
LIVE = ("Active", "Expiring", "Converted to Permanent")


class VehicleAssignment(Document):
	def validate(self):
		self.set_default_intervals()

	def before_update_after_submit(self):
		self.validate_driver_trained()

	@frappe.whitelist()
	def set_default_intervals(self):
		city = frappe.db.get_value("Project", self.project, "city") if self.project else None
		region, tire_interval = frappe.db.get_value("City", city, ["region", "default_tire_interval_km"]) or (
			None,
			None,
		)
		defaults = {**policy_intervals(region), "tire_interval_km": tire_interval}
		for fieldname in INTERVAL_FIELDS:
			if not self.get(fieldname) and defaults.get(fieldname):
				self.set(fieldname, defaults[fieldname])

	def validate_driver_trained(self):
		if self.assignment_type != PERMANENT:
			return
		if frappe.db.get_value("Driver", self.driver, "training_status") != "Trained":
			frappe.throw(
				_("Driver {0} is not trained and can only receive a temporary training assignment").format(
					self.driver
				)
			)

	def validate_submit_fields(self):
		for fieldname in SUBMIT_FIELDS:
			if not self.get(fieldname):
				frappe.throw(_("{0} is required to submit").format(_(self.meta.get_label(fieldname))))

	def validate_driver_licence(self):
		licence, expiry = frappe.db.get_value("Driver", self.driver, ["license_number", "expiry_date"])
		driver_meta = frappe.get_meta("Driver")
		for fieldname, value in (("license_number", licence), ("expiry_date", expiry)):
			if not value:
				frappe.throw(
					_("{0} is missing on Driver {1}").format(_(driver_meta.get_label(fieldname)), self.driver)
				)
		if getdate(expiry) < getdate(today()):
			frappe.throw(
				_("{0} on Driver {1} has passed").format(_(driver_meta.get_label("expiry_date")), self.driver)
			)

	def validate_active(self):
		for doctype, name in (("Driver", self.driver), ("Vehicle", self.vehicle)):
			if not frappe.db.get_value(doctype, name, "active"):
				frappe.throw(_("{0} {1} is inactive").format(_(doctype), name))

	def warn_other_vehicles(self):
		others = frappe.get_all(
			"Vehicle Assignment",
			filters={
				"docstatus": 1,
				"status": ("in", LIVE),
				"driver": self.driver,
				"name": ("!=", self.name),
			},
			pluck="vehicle",
		)
		if others:
			frappe.msgprint(
				_("Driver {0} already holds vehicle {1}").format(self.driver, ", ".join(others)),
				indicator="orange",
			)

	def validate_vehicle_free(self):
		holder = frappe.db.get_value(
			"Vehicle Assignment",
			{"vehicle": self.vehicle, "docstatus": 1, "status": ("in", LIVE), "name": ("!=", self.name)},
			["name", "driver"],
			as_dict=True,
		)
		if holder:
			frappe.throw(
				_("Vehicle {0} is already assigned to driver {1} in {2}").format(
					self.vehicle, holder.driver, holder.name
				)
			)

	def before_submit(self):
		self.validate_active()
		self.validate_vehicle_free()
		self.validate_submit_fields()
		self.validate_driver_licence()
		self.validate_driver_trained()
		self.handover_date = delivered_at(self.vehicle, self.driver, self.from_datetime)
		self.status = "Active"

	def on_submit(self):
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		vehicle.update({field: self.get(field) for field in INTERVAL_FIELDS})
		vehicle.update({"current_driver": self.driver, "current_project": self.project, "status": "Assigned"})
		vehicle.save()
		if self.vehicle_request:
			apply_workflow(frappe.get_doc("Vehicle Request", self.vehicle_request), "Assign")
		self.warn_other_vehicles()

	def before_cancel(self):
		if self.handover_date:
			frappe.throw(
				_(
					"Vehicle {0} was handed to the driver on {1}; record its return with a Vehicle Handover of type Return"
				).format(self.vehicle, frappe.format_value(self.handover_date, {"fieldtype": "Datetime"}))
			)
		self.status = "Cancelled"

	def on_cancel(self):
		self.release_vehicle()

	def convert_to_permanent(self):
		if self.docstatus != 1 or self.status not in CONVERTIBLE:
			return
		self.update(
			{
				"assignment_type": PERMANENT,
				"status": "Converted to Permanent",
				"handover_date": now_datetime(),
				"to_datetime": None,
			}
		)
		self.flags.ignore_permissions = True
		self.save()

	def record_handover(self, at):
		self.handover_date = at
		self.flags.ignore_permissions = True
		self.save()

	def end(self, at):
		self.status = "Ended"
		self.return_datetime = at
		self.flags.ignore_permissions = True
		self.save()
		self.release_vehicle()

	def release_vehicle(self):
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		if vehicle.current_driver != self.driver:
			return
		vehicle.update({"current_driver": None, "current_project": None, "status": "Available"})
		vehicle.save()


def delivered_at(vehicle, driver, since):
	return frappe.db.get_value(
		"Vehicle Handover",
		{
			"vehicle": vehicle,
			"to_driver": driver,
			"handover_type": "Handover",
			"docstatus": 1,
			"handover_datetime": (">=", since),
		},
		"handover_datetime",
		order_by="handover_datetime desc",
	)


def held_until(vehicle, driver, since):
	return frappe.db.get_value(
		"Vehicle Handover",
		{"vehicle": vehicle, "from_driver": driver, "docstatus": 1, "handover_datetime": (">", since)},
		"handover_datetime",
		order_by="handover_datetime asc",
	)


def holder_at(vehicle, at, driver=None):
	if not ((vehicle or driver) and at):
		return None
	for holder in frappe.get_all(
		"Vehicle Assignment",
		filters={
			"docstatus": 1,
			"handover_date": ("<=", at),
			**({"vehicle": vehicle} if vehicle else {"driver": driver}),
		},
		fields=["vehicle", "driver", "project", "customer", "handover_date"],
		order_by="handover_date desc",
		limit=1,
	):
		until = held_until(holder.vehicle, holder.driver, holder.handover_date)
		if not until or get_datetime(until) > get_datetime(at):
			return holder
	return None


def customer_at(at, vehicle=None, driver=None):
	holder = holder_at(vehicle, at, driver=driver)
	return (holder and holder.customer) or (driver and frappe.db.get_value("Driver", driver, "customer"))
