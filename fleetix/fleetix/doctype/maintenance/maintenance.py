# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, getdate, now_datetime, today

from fleetix.fleetix.vehicle import due_odometer, set_next_due

COMPONENT_FIELDS = {
	"Oil": ("last_oil_change_date", "last_oil_change_odometer"),
	"Oil Filter": ("last_filter_change_date", "last_filter_change_odometer"),
	"Front Tires": ("last_front_tires_date", "last_front_tires_odometer"),
	"Rear Tires": ("last_rear_tires_date", "last_rear_tires_odometer"),
	"Battery": ("battery_install_date", None),
}
NEXT_DUE_FIELDS = {
	"Oil": "next_oil_due_odometer",
	"Front Tires": "next_front_tires_due_odometer",
	"Rear Tires": "next_rear_tires_due_odometer",
}
ISSUE_STATES = ("Service", "Final Check")


class Maintenance(Document):
	def validate(self):
		if self.status == "Driver Arrived" and not self.visit_datetime:
			self.visit_datetime = now_datetime()
		if self.status == "Approved" and not self.approved_by:
			self.approved_by = frappe.session.user
		if self.status in ISSUE_STATES and not self.items_issued:
			self.items_issued = issue_items(self)
		if cint(self.odometer) > cint(frappe.db.get_value("Vehicle", self.vehicle, "last_odometer")):
			frappe.db.set_value(
				"Vehicle", self.vehicle, "last_odometer", cint(self.odometer), update_modified=False
			)

	def on_submit(self):
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		replaced_on = getdate(self.visit_datetime)
		vehicle.last_odometer = max(cint(vehicle.last_odometer), cint(self.odometer))
		for row in self.components_replaced:
			date_field, odometer_field = COMPONENT_FIELDS[row.component]
			vehicle.set(date_field, replaced_on)
			if odometer_field:
				vehicle.set(odometer_field, self.odometer)
		set_next_due(vehicle)
		vehicle.save()
		for row in self.components_replaced:
			next_due_odometer, next_due_date = next_due(vehicle, row.component)
			frappe.get_doc(
				{
					"doctype": "Component Replacement Log",
					"component": row.component,
					"replacement_date": replaced_on,
					"odometer_at_replacement": self.odometer,
					"item": row.item,
					"maintenance": self.name,
					"next_due_odometer": next_due_odometer,
					"next_due_date": next_due_date,
				}
			).insert(ignore_permissions=True)


def issue_items(maintenance):
	rows = [row for row in maintenance.components_replaced if row.item]
	if not rows:
		return None
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	entry = frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Issue",
			"company": maintenance.company,
			"maintenance": maintenance.name,
			"from_warehouse": warehouse,
			"items": [{"item_code": row.item, "qty": row.qty, "s_warehouse": warehouse} for row in rows],
		}
	).insert()
	return entry.name


def next_due(vehicle, component):
	if component == "Battery":
		return None, vehicle.next_battery_due_date
	if component == "Oil Filter":
		return due_odometer(vehicle.last_filter_change_odometer, vehicle.filter_interval_km), None
	return vehicle.get(NEXT_DUE_FIELDS[component]), None


def due_components(vehicle):
	due = []
	for component in COMPONENT_FIELDS:
		due_km, due_date = next_due(vehicle, component)
		if cint(due_km) and cint(vehicle.last_odometer) >= cint(due_km):
			due.append(component)
		elif due_date and getdate(due_date) <= getdate(today()):
			due.append(component)
	return due


def create_due_alerts():
	open_vehicles = set(frappe.get_all("Maintenance", filters={"docstatus": 0}, pluck="vehicle"))
	assigned = frappe.get_all(
		"Vehicle",
		filters={"active": 1, "current_driver": ("is", "set"), "current_project": ("is", "set")},
		pluck="name",
	)
	for name in assigned:
		vehicle = frappe.get_doc("Vehicle", name)
		stored_oil_due = vehicle.next_oil_due_odometer
		set_next_due(vehicle)
		if vehicle.next_oil_due_odometer != stored_oil_due:
			vehicle.save()
		due = due_components(vehicle)
		if name in open_vehicles or not due:
			continue
		frappe.get_doc(
			{
				"doctype": "Maintenance",
				"maintenance_type": "Periodic",
				"vehicle": name,
				"description": ", ".join(due),
			}
		).insert()
