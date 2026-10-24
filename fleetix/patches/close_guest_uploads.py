# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.utils import cint

FIELD = "allow_guests_to_upload_files"


def execute():
	if cint(frappe.db.get_single_value("System Settings", FIELD)) and opened_by_migrate():
		settings = frappe.get_single("System Settings")
		settings.set(FIELD, 0)
		settings.flags.ignore_permissions = True
		settings.save()


def opened_by_migrate():
	for version in frappe.get_all(
		"Version",
		filters={"ref_doctype": "System Settings", "docname": "System Settings"},
		fields=["owner", "data"],
		order_by="creation desc",
	):
		for field, old, new in json.loads(version.data).get("changed", []):
			if field == FIELD:
				return version.owner == "Administrator" and not cint(old) and cint(new)
	return False
