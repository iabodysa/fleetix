# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe


def titles(doctype, names, field):
	names = list({name for name in names if name})
	if not names:
		return {}
	return dict(
		frappe.get_list(
			doctype,
			filters={"name": ("in", names)},
			fields=["name", field],
			as_list=True,
			limit_page_length=0,
		)
	)
