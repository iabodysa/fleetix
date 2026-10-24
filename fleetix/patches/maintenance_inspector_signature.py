# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe


def execute():
	signatures = dict(
		frappe.get_all(
			"Vehicle Inspection",
			filters={"reference_type": "Maintenance", "inspector_signature": ("is", "set")},
			fields=["name", "inspector_signature"],
			as_list=True,
		)
	)
	for name, inspection in frappe.get_all(
		"Maintenance",
		filters={"inspection": ("in", list(signatures) or [""])},
		fields=["name", "inspection"],
		as_list=True,
	):
		frappe.db.set_value(
			"Maintenance", name, "inspector_signature", signatures[inspection], update_modified=False
		)
