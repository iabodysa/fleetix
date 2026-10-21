# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe


@frappe.whitelist()
def last_checklist_items(vehicle):
	frappe.has_permission("Vehicle Inspection", "read", throw=True)
	last = frappe.get_all(
		"Vehicle Inspection",
		filters={"vehicle": vehicle, "docstatus": ("<", 2)},
		order_by="inspection_datetime desc, creation desc",
		limit=1,
		pluck="name",
	)
	if not last:
		return []
	return frappe.get_all(
		"Vehicle Checklist Item",
		filters={"parent": last[0], "parenttype": "Vehicle Inspection", "parentfield": "checklist"},
		order_by="idx asc",
		pluck="item",
	)
