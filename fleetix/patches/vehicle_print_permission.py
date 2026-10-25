# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.permissions import update_permission_property

from fleetix.fleetix.permissions import CORE_PERMISSIONS


def execute():
	for role, ptypes in CORE_PERMISSIONS["Vehicle"].items():
		if "print" in ptypes and frappe.db.exists(
			"Custom DocPerm", {"parent": "Vehicle", "role": role, "permlevel": 0, "if_owner": 0}
		):
			update_permission_property("Vehicle", role, 0, "print", 1)
