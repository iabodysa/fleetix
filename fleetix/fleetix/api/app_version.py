# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe

import fleetix


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_app_version():
	return fleetix.__version__
