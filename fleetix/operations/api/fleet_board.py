# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe

from fleetix.operations.fleet_state import BOARD_ROLES, classify, count

COUNT_TTL_SECONDS = 60


@frappe.whitelist()
def get_board(project=None, city=None):
	frappe.only_for(BOARD_ROLES)
	frappe.has_permission("Vehicle", "read", throw=True)
	frappe.has_permission("Driver", "read", throw=True)
	rows = classify(city=city)
	projects = sorted({(row.project, row.project_name or row.project) for row in rows if row.project})
	if project:
		rows = [row for row in rows if row.project == project]
	return {
		"rows": rows,
		"counts": count(rows),
		"projects": [{"value": name, "label": label} for name, label in projects],
		"cities": frappe.get_list("City", pluck="name", order_by="name"),
	}


@frappe.whitelist()
def count_state(filters=None):
	frappe.only_for(BOARD_ROLES)
	frappe.has_permission("Vehicle", "read", throw=True)
	filters = frappe.parse_json(filters) or {}
	if isinstance(filters, list):
		filters = {row[1]: row[3] for row in filters if len(row) > 3}
	key = f"fleetix:fleet_counts:{frappe.session.user}"
	counts = frappe.cache.get_value(key)
	if counts is None:
		counts = count(classify())
		frappe.cache.set_value(key, counts, expires_in_sec=COUNT_TTL_SECONDS)
	return {"value": counts.get(filters.get("state"), 0), "fieldtype": "Int"}
