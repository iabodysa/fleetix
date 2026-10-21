# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe

APP_LOGO = "/assets/fleetix/images/fleetix-logo.svg"


def set_navbar_logo():
	if not frappe.db.get_single_value("Navbar Settings", "app_logo"):
		frappe.db.set_single_value("Navbar Settings", "app_logo", APP_LOGO)
