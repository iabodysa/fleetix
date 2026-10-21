# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate

from fleetix.operations.titles import titles


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = {"docstatus": ("<", 2)}
	conditions.update({key: filters[key] for key in ("company", "project") if filters.get(key)})
	if filters.from_date and filters.to_date:
		conditions["period_from"] = ("between", [filters.from_date, filters.to_date])

	groups = {}
	for row in frappe.get_list(
		"Project Rental Charge",
		filters=conditions,
		fields=["project", "period_from", "hours", "amount", "docstatus"],
		limit_page_length=0,
	):
		month = getdate(row.period_from).strftime("%Y-%m") if row.period_from else ""
		group = groups.setdefault(
			(row.project, month),
			{
				"project": row.project,
				"month": month,
				"charges": 0,
				"hours": 0.0,
				"amount": 0.0,
				"posted_amount": 0.0,
			},
		)
		group["charges"] += 1
		group["hours"] += flt(row.hours)
		group["amount"] += flt(row.amount)
		if row.docstatus == 1:
			group["posted_amount"] += flt(row.amount)

	project_names = titles("Project", [project for project, month in groups], "project_name")
	data = sorted(groups.values(), key=lambda group: (group["month"], group["project"] or ""), reverse=True)
	for group in data:
		group["project_name"] = project_names.get(group["project"])
	return get_columns(), data


def get_columns():
	return [
		{
			"fieldname": "project",
			"label": _("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"width": 120,
		},
		{"fieldname": "project_name", "label": _("Project Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "month", "label": _("Month"), "fieldtype": "Data", "width": 90},
		{"fieldname": "charges", "label": _("Charges"), "fieldtype": "Int", "width": 90},
		{"fieldname": "hours", "label": _("Hours"), "fieldtype": "Float", "precision": 1, "width": 90},
		{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "posted_amount", "label": _("Posted Amount"), "fieldtype": "Currency", "width": 130},
	]
