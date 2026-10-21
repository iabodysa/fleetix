# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_datetime, now_datetime, time_diff_in_hours

from fleetix.fleetix.titles import titles

BAR_COLOR = "#2a78d6"


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = {"docstatus": ("<", 2)}
	conditions.update(
		{key: filters[key] for key in ("company", "project", "vehicle", "driver") if filters.get(key)}
	)
	rows = frappe.get_list(
		"Vehicle Assignment",
		filters=conditions,
		fields=["name", "project", "vehicle", "driver", "from_datetime", "to_datetime", "status"],
		order_by="project asc, from_datetime desc",
		limit_page_length=0,
	)
	project_names = titles("Project", [row.project for row in rows], "project_name")
	driver_names = titles("Driver", [row.driver for row in rows], "full_name")
	now = now_datetime()
	data = [
		{
			"assignment": row.name,
			"project": row.project,
			"project_name": project_names.get(row.project),
			"vehicle": row.vehicle,
			"driver": row.driver,
			"driver_name": driver_names.get(row.driver),
			"from_datetime": row.from_datetime,
			"to_datetime": row.to_datetime,
			"status": _(row.status),
			"hours": hours(row, now),
		}
		for row in rows
	]
	return get_columns(), data, None, get_chart(data)


def hours(row, now):
	if not row.from_datetime:
		return None
	end = min(get_datetime(row.to_datetime), now) if row.to_datetime else now
	return max(flt(time_diff_in_hours(end, row.from_datetime), 1), 0)


def get_columns():
	return [
		{
			"fieldname": "assignment",
			"label": _("Vehicle Assignment"),
			"fieldtype": "Link",
			"options": "Vehicle Assignment",
			"width": 140,
		},
		{
			"fieldname": "project",
			"label": _("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 120,
		},
		{"fieldname": "project_name", "label": _("Project Name"), "fieldtype": "Data", "width": 180},
		{
			"fieldname": "vehicle",
			"label": _("Vehicle"),
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 120,
		},
		{"fieldname": "driver", "label": _("Driver"), "fieldtype": "Link", "options": "Driver", "width": 130},
		{"fieldname": "driver_name", "label": _("Driver Name"), "fieldtype": "Data", "width": 160},
		{"fieldname": "from_datetime", "label": _("From"), "fieldtype": "Datetime", "width": 150},
		{"fieldname": "to_datetime", "label": _("To"), "fieldtype": "Datetime", "width": 150},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 120},
		{"fieldname": "hours", "label": _("Hours"), "fieldtype": "Float", "precision": 1, "width": 90},
	]


def get_chart(data):
	counts = {}
	for row in data:
		label = row["project_name"] or row["project"] or ""
		counts[label] = counts.get(label, 0) + 1
	ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)
	return {
		"data": {
			"labels": [label for label, total in ordered],
			"datasets": [{"name": _("Assignments"), "values": [total for label, total in ordered]}],
		},
		"type": "bar",
		"colors": [BAR_COLOR],
	}
