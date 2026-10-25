# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe


def execute():
	frappe.db.set_single_value("Stock Settings", "allow_negative_stock", 1)
