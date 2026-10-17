# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	inspection_filters = {"status": ["in", ["Due", "Overdue"]]}
	repair_filters = {"status": ["in", ["Open", "In Workshop"]]}
	if filters.due_before:
		inspection_filters["due_date"] = ["<=", filters.due_before]
	if filters.status:
		inspection_filters["status"] = repair_filters["status"] = filters.status
	data = [
		dict(row, document_type="Inspection")
		for row in frappe.get_list(
			"Inspection", filters=inspection_filters, fields=["car", "name as document", "due_date as date", "status"]
		)
	] + [
		dict(row, document_type="Repair")
		for row in frappe.get_list(
			"Repair", filters=repair_filters, fields=["car", "name as document", "open_date as date", "status"]
		)
	]
	return get_columns(), sorted(data, key=lambda row: str(row["date"] or ""))


def get_columns():
	return [
		{"fieldname": "car", "label": _("Car"), "fieldtype": "Link", "options": "Car", "width": 140},
		{"fieldname": "document_type", "label": _("Document Type"), "fieldtype": "Link", "options": "DocType", "width": 120},
		{"fieldname": "document", "label": _("Document"), "fieldtype": "Dynamic Link", "options": "document_type", "width": 140},
		{"fieldname": "date", "label": _("Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 140},
	]
