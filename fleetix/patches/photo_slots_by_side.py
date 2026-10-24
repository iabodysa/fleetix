# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe

from fleetix.fleetix.doctype.maintenance.maintenance import DEFAULT_PHOTO_SLOTS
from fleetix.fleetix.vehicle import parse_fieldnames

SHIPPED_SLOTS = ["Odometer", "Front", "Rear", "Left Side", "Right Side", "Engine Bay"]


def execute():
	current = frappe.db.get_single_value("Fleetix Settings", "photo_slots")
	if parse_fieldnames(current) == SHIPPED_SLOTS:
		frappe.db.set_single_value("Fleetix Settings", "photo_slots", "\n".join(DEFAULT_PHOTO_SLOTS))
