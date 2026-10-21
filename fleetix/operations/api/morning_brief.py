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
		"expiring_assignments": frappe.db.count("Vehicle Assignment", {"docstatus": 1, "status": "Expiring"}),
		"since": {
			"handovers": frappe.db.count(
				"Vehicle Handover", {"status": "Completed", "modified": (">=", since)}
			),
			"maintenance": frappe.db.count("Maintenance", {"status": "Completed", "modified": (">=", since)}),
			"accidents": frappe.db.count("Accident", {"creation": (">=", since)}),
			"requests": frappe.db.count("Vehicle Request", {"creation": (">=", since)}),
		},
	}
