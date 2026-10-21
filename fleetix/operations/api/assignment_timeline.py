# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, cint, getdate, today

from fleetix.operations.fleet_state import BOARD_ROLES, classify

DEFAULT_DAYS = 14
MAX_DAYS = 31
BACK_DAYS = 3


@frappe.whitelist()
def get_timeline(start=None, days=DEFAULT_DAYS, project=None, city=None):
	frappe.only_for(BOARD_ROLES)
	frappe.has_permission("Vehicle", "read", throw=True)
	frappe.has_permission("Driver", "read", throw=True)
	days = min(max(cint(days), 1), MAX_DAYS)
	start = getdate(start or add_days(today(), -BACK_DAYS))
	end = add_days(start, days)
	rows = classify(project=project, city=city)
	names = [r.vehicle for r in rows]
	spans = {name: [] for name in names}
	if names:
		for a in frappe.get_list(
			"Vehicle Assignment",
			filters={"docstatus": 1, "vehicle": ("in", names), "from_datetime": ("<", end)},
			or_filters={
				"to_datetime": (">=", start),
				"status": ("in", ("Active", "Expiring", "Converted to Permanent")),
			},
			fields=[
				"name",
				"vehicle",
				"driver",
				"project",
				"assignment_type",
				"from_datetime",
				"to_datetime",
				"status",
			],
		):
			spans[a.vehicle].append(
				{
					"kind": "train" if a.assignment_type == "Temporary (Training)" else "on",
					"start": a.from_datetime,
					"end": a.to_datetime,
					"doctype": "Vehicle Assignment",
					"name": a.name,
					"label": a.project or a.driver,
				}
			)
		for r in frappe.get_list(
			"Vehicle Request",
			filters={
				"selected_vehicle": ("in", names),
				"workflow_state": ("not in", ("Assigned", "Rejected", "Cancelled")),
				"required_date": ("<", end),
			},
			fields=["name", "selected_vehicle", "project", "required_date"],
		):
			spans[r.selected_vehicle].append(
				{
					"kind": "plan",
					"start": r.required_date,
					"end": None,
					"doctype": "Vehicle Request",
					"name": r.name,
					"label": r.project,
				}
			)
		for m in frappe.get_list(
			"Maintenance",
			filters={
				"vehicle": ("in", names),
				"docstatus": ("!=", 2),
				"visit_datetime": ("between", (start, end)),
			},
			fields=["name", "vehicle", "visit_datetime"],
		):
			spans[m.vehicle].append(
				{"kind": "maintenance", "start": m.visit_datetime, "doctype": "Maintenance", "name": m.name}
			)
		for h in frappe.get_list(
			"Vehicle Handover",
			filters={
				"vehicle": ("in", names),
				"docstatus": ("!=", 2),
				"handover_datetime": ("between", (start, end)),
			},
			fields=["name", "vehicle", "handover_datetime", "handover_type"],
		):
			spans[h.vehicle].append(
				{
					"kind": "handover",
					"start": h.handover_datetime,
					"doctype": "Vehicle Handover",
					"name": h.name,
					"label": h.handover_type,
				}
			)
	return {
		"start": start,
		"days": days,
		"today": today(),
		"rows": [{**r, "spans": spans.get(r.vehicle, [])} for r in rows],
	}
