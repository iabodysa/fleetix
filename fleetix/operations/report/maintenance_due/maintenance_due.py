# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, date_diff, today

from fleetix.operations.doctype.maintenance.maintenance import (
	COMPONENT_FIELDS,
	NEXT_DUE_FIELDS,
	due_components,
	next_due,
)

VEHICLE_FIELDS = [
	"name",
	"current_project",
	"last_odometer",
	"next_battery_due_date",
	"filter_interval_km",
	*NEXT_DUE_FIELDS.values(),
	*(field for pair in COMPONENT_FIELDS.values() for field in pair if field),
]


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = {key: filters[key] for key in ("company", "city") if filters.get(key)}
	if filters.project:
		conditions["current_project"] = filters.project
	if filters.vehicle:
		conditions["name"] = filters.vehicle

	data = []
	for vehicle in frappe.get_list(
		"Vehicle", filters=conditions, fields=VEHICLE_FIELDS, order_by="name asc", limit_page_length=0
	):
		due = due_components(vehicle)
		odometer = cint(vehicle.last_odometer)
		for component, fields in COMPONENT_FIELDS.items():
			overdue = component in due
			if filters.overdue_only and not overdue:
				continue
			due_km, due_date = next_due(vehicle, component)
			data.append(
				{
					"vehicle": vehicle.name,
					"project": vehicle.current_project,
					"component": _(component),
					"last_done": vehicle.get(fields[0]),
					"odometer": vehicle.last_odometer,
					"next_due_odometer": due_km,
					"next_due_date": due_date,
					"km_remaining": cint(due_km) - odometer if cint(due_km) and odometer else None,
					"days_remaining": date_diff(due_date, today()) if due_date else None,
					"overdue": 1 if overdue else 0,
				}
			)

	data.sort(key=lambda row: (-row["overdue"], not (row["next_due_odometer"] or row["next_due_date"])))
	return get_columns(), data


def get_columns():
	return [
		{
			"fieldname": "vehicle",
			"label": _("Vehicle"),
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 120,
		},
		{
			"fieldname": "project",
			"label": _("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 140,
		},
		{"fieldname": "component", "label": _("Component"), "fieldtype": "Data", "width": 120},
		{"fieldname": "last_done", "label": _("Last Done"), "fieldtype": "Date", "width": 110},
		{"fieldname": "odometer", "label": _("Odometer"), "fieldtype": "Int", "width": 100},
		{"fieldname": "next_due_odometer", "label": _("Due Odometer"), "fieldtype": "Int", "width": 130},
		{"fieldname": "next_due_date", "label": _("Due Date"), "fieldtype": "Date", "width": 120},
		{"fieldname": "km_remaining", "label": _("Km Remaining"), "fieldtype": "Int", "width": 110},
		{"fieldname": "days_remaining", "label": _("Days Remaining"), "fieldtype": "Int", "width": 110},
		{"fieldname": "overdue", "label": _("Overdue"), "fieldtype": "Check", "width": 90},
	]
