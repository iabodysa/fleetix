# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime

SAMPLE_NAME = "SAMPLE"
SAMPLE_ODOMETER = 48210
DAMAGE_BODIES = ("Car", "SUV", "Bus", "Pickup Truck")
HANDOVER_TYPES = ("Handover", "Return")


def body_vehicle(body):
	types = frappe.get_all("Vehicle Type", filters={"body_type": body}, pluck="name")
	return frappe.db.get_value("Vehicle", {"vehicle_type": ("in", types)}, "name") if types else None


def sample(label, doctype, print_format, values):
	return {
		"label": label,
		"format": print_format,
		"doc": dict(values, doctype=doctype, name=SAMPLE_NAME, docstatus=0),
	}


def print_samples():
	vehicle_name = frappe.db.get_value("Vehicle", {}, "name", order_by="modified desc")
	if not vehicle_name:
		return []
	vehicle = frappe.get_doc("Vehicle", vehicle_name)
	now = now_datetime()
	samples = []
	for body in DAMAGE_BODIES:
		name = body_vehicle(body)
		if name:
			samples.append(
				sample(
					_("Damage sheet") + " · " + _(body),
					"Vehicle Inspection",
					"Thermal Damage Sheet",
					{
						"vehicle": name,
						"odometer": SAMPLE_ODOMETER,
						"fuel_level": "1/2",
						"inspection_datetime": now,
					},
				)
			)
	item = frappe.db.get_value("Item", {"is_stock_item": 1, "disabled": 0}, "name")
	visit = {
		"vehicle": vehicle.name,
		"driver": vehicle.current_driver,
		"project": vehicle.current_project,
		"company": vehicle.company,
		"odometer": SAMPLE_ODOMETER,
		"visit_datetime": now,
		"maintenance_type": "Periodic",
		"status": "Final Check",
		"components_replaced": [{"component": "Oil Filter", "item": item, "qty": 1}] if item else [],
	}
	samples += [
		sample(_("Maintenance Invoice"), "Maintenance", "Thermal Maintenance Invoice", visit),
		sample(_("Gate Entry Pass"), "Maintenance", "Thermal Gate Entry Pass", visit),
		sample(_("Gate Exit Pass"), "Maintenance", "Thermal Gate Exit Pass", visit),
		sample(_("Vehicle Card"), "Vehicle", "Thermal Vehicle Card", vehicle.as_dict(no_default_fields=True)),
	]
	for handover_type in HANDOVER_TYPES:
		samples.append(
			sample(
				_("Handover Pass") + " · " + _(handover_type),
				"Vehicle Handover",
				"Thermal Handover Pass",
				{
					"handover_type": handover_type,
					"vehicle": vehicle.name,
					"handover_datetime": now,
					"odometer": SAMPLE_ODOMETER,
					"fuel_level": "1/2",
					"to_driver": vehicle.current_driver,
					"to_project": vehicle.current_project,
					"status": "Completed",
				},
			)
		)
	return samples
