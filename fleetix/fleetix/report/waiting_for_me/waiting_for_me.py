# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _

FLAGGED = "Odometer Flagged"
SOURCES = (
	("Maintenance", {"docstatus": 0, "status": "Full Inspection", "inspection": ("is", "set")}, "status"),
	("Vehicle Request", {"workflow_state": ("in", ("New", "Pending Vehicle Selection"))}, "workflow_state"),
	("Damage", {"docstatus": ("<", 2), "status": "Detected"}, "status"),
	("Accident", {"docstatus": ("<", 2), "status": ("!=", "Closed")}, "status"),
	("Maintenance", {"docstatus": 0, "odometer_flagged": 1}, None),
	("Vehicle Handover", {"docstatus": 0, "odometer_flagged": 1}, None),
)
VEHICLE_DOCTYPES = ("Maintenance", "Damage", "Accident", "Vehicle Handover")


def execute(filters=None):
	columns = [
		{"fieldname": "waiting_since", "label": _("Waiting Since"), "fieldtype": "Datetime", "width": 170},
		{
			"fieldname": "reference_doctype",
			"label": _("Document Type"),
			"fieldtype": "Link",
			"options": "DocType",
			"width": 150,
		},
		{
			"fieldname": "reference_name",
			"label": _("Document"),
			"fieldtype": "Dynamic Link",
			"options": "reference_doctype",
			"width": 170,
		},
		{
			"fieldname": "vehicle",
			"label": _("Vehicle"),
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 140,
		},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 180},
	]
	rows = []
	for doctype, conditions, status_field in SOURCES:
		fields = ["name", "creation"] + ([status_field] if status_field else [])
		if doctype in VEHICLE_DOCTYPES:
			fields.append("vehicle")
		docs = frappe.get_list(doctype, filters=conditions, fields=fields)
		since = state_since(doctype, [doc.name for doc in docs])
		rows += [
			{
				"waiting_since": since.get(doc.name, doc.creation),
				"reference_doctype": doctype,
				"reference_name": doc.name,
				"vehicle": doc.get("vehicle"),
				"status": _(doc.get(status_field) if status_field else FLAGGED),
			}
			for doc in docs
		]
	rows.sort(key=lambda row: row["waiting_since"])
	return columns, rows


def state_since(doctype, names):
	if not names:
		return {}
	return {
		row.reference_name: row.creation
		for row in frappe.get_all(
			"Comment",
			filters={
				"comment_type": "Workflow",
				"reference_doctype": doctype,
				"reference_name": ("in", names),
			},
			fields=["reference_name", "creation"],
			order_by="creation asc",
		)
	}
