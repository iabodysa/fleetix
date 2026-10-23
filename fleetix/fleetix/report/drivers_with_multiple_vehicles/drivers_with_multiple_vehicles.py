# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from fleetix.fleetix.doctype.vehicle_assignment.vehicle_assignment import LIVE
from fleetix.fleetix.titles import titles


def execute(filters=None):
	return get_columns(), multi_vehicle_drivers()


def multi_vehicle_drivers():
	held = {}
	for row in frappe.get_list(
		"Vehicle Assignment",
		filters={"docstatus": 1, "status": ("in", LIVE)},
		fields=["driver", "vehicle", "project"],
		order_by="driver asc, from_datetime asc",
		limit_page_length=0,
	):
		held.setdefault(row.driver, []).append(row)
	held = {driver: rows for driver, rows in held.items() if len({row.vehicle for row in rows}) > 1}
	if not held:
		return []
	assignments = [row for rows in held.values() for row in rows]
	vehicles = {
		vehicle.name: vehicle
		for vehicle in frappe.get_list(
			"Vehicle",
			filters={"name": ("in", list({row.vehicle for row in assignments}))},
			fields=["name", "license_plate", "vehicle_type"],
			limit_page_length=0,
		)
	}
	driver_names = titles("Driver", list(held), "full_name")
	project_names = titles("Project", [row.project for row in assignments], "project_name")
	data = []
	for driver, rows in held.items():
		names = list(dict.fromkeys(row.vehicle for row in rows))
		projects = list(dict.fromkeys(row.project for row in rows if row.project))
		data.append(
			{
				"driver": driver,
				"driver_name": driver_names.get(driver),
				"vehicle_count": len(names),
				"vehicles": ", ".join(vehicle_label(vehicles.get(name), name) for name in names),
				"projects": ", ".join(project_names.get(project) or project for project in projects),
			}
		)
	return data


def vehicle_label(vehicle, name):
	if not vehicle:
		return name
	plate = vehicle.license_plate or name
	return f"{plate} ({vehicle.vehicle_type})" if vehicle.vehicle_type else plate


def get_columns():
	return [
		{"fieldname": "driver", "label": _("Driver"), "fieldtype": "Link", "options": "Driver", "width": 130},
		{"fieldname": "driver_name", "label": _("Driver Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "vehicle_count", "label": _("Vehicles Held"), "fieldtype": "Int", "width": 110},
		{"fieldname": "vehicles", "label": _("Vehicles"), "fieldtype": "Data", "width": 320},
		{"fieldname": "projects", "label": _("Projects"), "fieldtype": "Data", "width": 240},
	]
