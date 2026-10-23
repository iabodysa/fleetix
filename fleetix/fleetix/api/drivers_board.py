# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_datetime, now_datetime, today

from fleetix.fleetix.doctype.vehicle_assignment.vehicle_assignment import LIVE
from fleetix.fleetix.fleet_state import BOARD_ROLES, STATES, count
from fleetix.fleetix.report.drivers_with_multiple_vehicles.drivers_with_multiple_vehicles import (
	multi_vehicle_drivers,
)

TRAINED = "Trained"


@frappe.whitelist()
def get_drivers(project=None, city=None):
	frappe.only_for(BOARD_ROLES)
	frappe.has_permission("Vehicle", "read", throw=True)
	frappe.has_permission("Driver", "read", throw=True)
	drivers = frappe.get_list(
		"Driver",
		filters={"status": "Active", "active": 1},
		fields=["name", "full_name", "cell_number", "training_status", "project"],
		limit_page_length=0,
	)
	if not drivers:
		return {"rows": [], "counts": dict.fromkeys(STATES, 0), "projects": [], "cities": []}
	now = now_datetime()
	day_end = get_datetime(f"{today()} 23:59:59")
	live = {}
	for row in frappe.get_list(
		"Vehicle Assignment",
		filters={"docstatus": 1, "status": ("in", LIVE), "driver": ("in", [d.name for d in drivers])},
		fields=["name", "driver", "vehicle", "project", "assignment_type", "to_datetime"],
		order_by="from_datetime asc",
	):
		live[row.driver] = row
	plates = dict(
		frappe.get_list(
			"Vehicle",
			filters={"name": ("in", [a.vehicle for a in live.values()])},
			fields=["name", "license_plate"],
			as_list=True,
		)
	)
	project_rows = frappe.get_list("Project", fields=["name", "project_name", "city"])
	project_city = {p.name: p.city for p in project_rows}
	project_label = {p.name: p.project_name for p in project_rows}

	rows = []
	for driver in drivers:
		assignment = live.get(driver.name)
		row = frappe._dict(
			driver=driver.name,
			name=driver.full_name or driver.name,
			phone=driver.cell_number,
			training=driver.training_status,
			project=assignment.project if assignment else driver.project,
			vehicle=assignment.vehicle if assignment else None,
			plate=plates.get(assignment.vehicle) if assignment else None,
			assignment=assignment.name if assignment else None,
		)
		row.city = project_city.get(row.project)
		row.project_name = project_label.get(row.project)
		if assignment and assignment.to_datetime and get_datetime(assignment.to_datetime) <= day_end:
			late = (now - get_datetime(assignment.to_datetime)).total_seconds() / 3600
			row.update(
				state="red", reason="return_due", due=assignment.to_datetime, late_hours=round(late, 1)
			)
		elif driver.training_status != TRAINED:
			row.update(state="gray", reason=driver.training_status or "Not Trained")
		elif not assignment:
			row.update(state="black", reason="trained_no_vehicle")
		else:
			row.update(state="green", reason="")
		rows.append(row)

	projects = sorted({(r.project, r.project_name or r.project) for r in rows if r.project})
	if project:
		rows = [r for r in rows if r.project == project]
	if city:
		rows = [r for r in rows if r.city == city]
	rows.sort(key=lambda r: (STATES.index(r.state), -(r.get("late_hours") or 0), r.name))
	return {
		"rows": rows,
		"counts": count(rows),
		"projects": [{"value": name, "label": label} for name, label in projects],
		"cities": frappe.get_list("City", pluck="name", order_by="name"),
	}


@frappe.whitelist()
def count_multi_vehicle_drivers(filters=None):
	frappe.only_for(BOARD_ROLES)
	frappe.has_permission("Vehicle Assignment", "read", throw=True)
	return {
		"value": len(multi_vehicle_drivers()),
		"fieldtype": "Int",
		"route": ["query-report", "Drivers With Multiple Vehicles"],
	}
