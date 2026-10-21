# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from fleetix.fleetix.doctype.maintenance.maintenance import COMPONENT_FIELDS, next_due
from fleetix.fleetix.fleet_state import STATES, classify, count

STATE_LABELS = {
	"red": "Due for Handover",
	"black": "Idle Without Assignment",
	"gray": "Periodic Maintenance Missed",
	"green": "All Clear",
}
STATE_COLORS = {"red": "#dc2626", "black": "#141518", "gray": "#8b919b", "green": "#16a34a"}
VEHICLE_FIELDS = [
	"name",
	"vehicle_type",
	"last_odometer",
	"registration_expiry",
	"periodic_inspection_expiry",
	"insurance_policy",
	"next_oil_due_odometer",
	"next_front_tires_due_odometer",
	"next_rear_tires_due_odometer",
	"next_battery_due_date",
	"last_filter_change_odometer",
	"filter_interval_km",
]


def execute(filters=None):
	filters = frappe._dict(filters or {})
	rows = classify(project=filters.project, city=filters.city)
	vehicles = {
		vehicle.name: vehicle
		for vehicle in frappe.get_list(
			"Vehicle",
			filters={"name": ("in", [row.vehicle for row in rows] or [""])},
			fields=VEHICLE_FIELDS,
			limit_page_length=0,
		)
	}
	policies = list({vehicle.insurance_policy for vehicle in vehicles.values() if vehicle.insurance_policy})
	policy_end = (
		dict(
			frappe.get_list(
				"Insurance Policy",
				filters={"name": ("in", policies)},
				fields=["name", "end_date"],
				as_list=True,
			)
		)
		if policies
		else {}
	)

	customers = dict(
		frappe.get_all(
			"Driver",
			filters={"name": ("in", [row.driver for row in rows if row.driver] or [""])},
			fields=["name", "customer"],
			as_list=True,
		)
	)
	kept, data = [], []
	for row in rows:
		vehicle = vehicles.get(row.vehicle)
		if not vehicle:
			continue
		customer = customers.get(row.driver)
		if filters.customer and customer != filters.customer:
			continue
		if filters.vehicle_type and vehicle.vehicle_type != filters.vehicle_type:
			continue
		entry = {
			"vehicle": row.vehicle,
			"vehicle_type": vehicle.vehicle_type,
			"customer": customer,
			"project": row.project,
			"driver": row.driver,
			"driver_name": row.driver_name,
			"state": _(STATE_LABELS[row.state]),
			"state_color": row.state,
			"odometer": vehicle.last_odometer,
			"istimara_expiry": vehicle.registration_expiry,
			"inspection_expiry": vehicle.periodic_inspection_expiry,
			"insurance_expiry": policy_end.get(vehicle.insurance_policy),
		}
		for component in COMPONENT_FIELDS:
			due_km, due_date = next_due(vehicle, component)
			entry[frappe.scrub(component)] = due_date or due_km
		kept.append(row)
		data.append(entry)

	return get_columns(), data, None, get_chart(count(kept))


def get_columns():
	columns = [
		{
			"fieldname": "vehicle",
			"label": _("Vehicle"),
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 120,
		},
		{
			"fieldname": "vehicle_type",
			"label": _("Vehicle Type"),
			"fieldtype": "Link",
			"options": "Vehicle Type",
			"width": 120,
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 140,
		},
		{
			"fieldname": "project",
			"label": _("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 140,
		},
		{"fieldname": "driver", "label": _("Driver"), "fieldtype": "Link", "options": "Driver", "width": 130},
		{"fieldname": "driver_name", "label": _("Driver Name"), "fieldtype": "Data", "width": 160},
		{"fieldname": "state", "label": _("Vehicle State"), "fieldtype": "Data", "width": 200},
		{"fieldname": "odometer", "label": _("Odometer"), "fieldtype": "Int", "width": 100},
	]
	for component, fields in COMPONENT_FIELDS.items():
		columns.append(
			{
				"fieldname": frappe.scrub(component),
				"label": _("{0} Due").format(_(component)),
				"fieldtype": "Int" if fields[1] else "Date",
				"width": 120,
			}
		)
	columns += [
		{"fieldname": "istimara_expiry", "label": _("Istimara Expiry"), "fieldtype": "Date", "width": 120},
		{
			"fieldname": "inspection_expiry",
			"label": _("Inspection Expiry"),
			"fieldtype": "Date",
			"width": 120,
		},
		{"fieldname": "insurance_expiry", "label": _("Insurance Expiry"), "fieldtype": "Date", "width": 120},
	]
	return columns


def get_chart(counts):
	return {
		"data": {
			"labels": [_(STATE_LABELS[state]) for state in STATES],
			"datasets": [{"name": _("Vehicles"), "values": [counts[state] for state in STATES]}],
		},
		"type": "donut",
		"colors": [STATE_COLORS[state] for state in STATES],
	}
