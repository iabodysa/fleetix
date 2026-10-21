# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, today

from fleetix.operations.fleet_state import BOARD_ROLES, classify, count

BRIEF_WINDOW_DAYS = 7
LIST_SIZE = 5


@frappe.whitelist()
def get_brief():
	frappe.only_for(BOARD_ROLES)
	frappe.has_permission("Vehicle", "read", throw=True)
	frappe.has_permission("Driver", "read", throw=True)
	rows = classify()
	since = add_days(today(), -1)
	expiring = [r for r in rows if r.get("expiry_days") is not None and r.expiry_days <= BRIEF_WINDOW_DAYS]
	expiring.sort(key=lambda r: r.expiry_days)
	return {
		"user": frappe.utils.get_fullname(),
		"counts": count(rows),
		"first": [r for r in rows if r.state == "red"][:3],
		"gray": [r for r in rows if r.state == "gray"][:LIST_SIZE],
		"idle": [r for r in rows if r.state == "black"][:LIST_SIZE],
		"expiring": expiring[:LIST_SIZE],
		"expiring_assignments": len(
			frappe.get_list(
				"Vehicle Assignment", filters={"docstatus": 1, "status": "Expiring"}, pluck="name"
			)
		),
		"since": {
			"handovers": len(
				frappe.get_list(
					"Vehicle Handover",
					filters={"status": "Completed", "modified": (">=", since)},
					pluck="name",
				)
			),
			"maintenance": len(
				frappe.get_list(
					"Maintenance", filters={"status": "Completed", "modified": (">=", since)}, pluck="name"
				)
			),
			"accidents": len(frappe.get_list("Accident", filters={"creation": (">=", since)}, pluck="name")),
			"requests": len(
				frappe.get_list("Vehicle Request", filters={"creation": (">=", since)}, pluck="name")
			),
		},
	}
