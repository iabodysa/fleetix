# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.fixtures import sync_fixtures

from fleetix.fleetix.vehicle import missing_data, parse_fieldnames

FIELD = "vehicle_required_fields"


def execute():
	sync_fixtures("fleetix")
	text = frappe.db.get_single_value("Fleetix Settings", FIELD)
	if not text:
		text = frappe.get_meta("Fleetix Settings").get_field(FIELD).default
		frappe.db.set_single_value("Fleetix Settings", FIELD, text)
	fieldnames = parse_fieldnames(text)
	for name in frappe.get_all("Vehicle", pluck="name"):
		values = missing_data(frappe.get_doc("Vehicle", name), fieldnames)
		frappe.db.set_value("Vehicle", name, values, update_modified=False)
