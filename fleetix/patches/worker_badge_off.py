# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe


def execute():
	if frappe.db.exists("Print Format", "Worker Badge"):
		frappe.db.set_value("Print Format", "Worker Badge", "disabled", 1, update_modified=False)
