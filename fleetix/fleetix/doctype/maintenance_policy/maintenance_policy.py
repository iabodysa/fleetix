# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

ANY = (None, "", "All")
DEFAULT_POLICIES = (
	("Oil", "All", "Summer (Apr-Sep)", 5000, None),
	("Oil", "All", "Winter (Oct-Mar)", 7500, None),
	("Oil Filter", "All", "Summer (Apr-Sep)", 10000, None),
	("Oil Filter", "All", "Winter (Oct-Mar)", 15000, None),
	("Front Tires", "Eastern", "All", 55000, None),
	("Front Tires", "Western", "All", 55000, None),
	("Front Tires", "All", "All", 70000, None),
	("Battery", "All", "All", None, 12),
)


class MaintenancePolicy(Document):
	pass


def get_policy(component, region=None, season=None, on_date=None):
	rows = frappe.get_all(
		"Maintenance Policy",
		filters={"component": component, "effective_from": ("<=", on_date or nowdate())},
		fields=["region", "season", "interval_km", "interval_months", "effective_from"],
	)
	matches = [
		row
		for row in rows
		if (row.region == region or row.region in ANY) and (row.season == season or row.season in ANY)
	]
	if not matches:
		return None
	return max(
		matches,
		key=lambda row: (row.region == region, row.season == season, getdate(row.effective_from)),
	)


def insert_default_policies():
	for component, region, season, interval_km, interval_months in DEFAULT_POLICIES:
		if frappe.db.exists(
			"Maintenance Policy", {"component": component, "region": region, "season": season}
		):
			continue
		frappe.get_doc(
			{
				"doctype": "Maintenance Policy",
				"component": component,
				"region": region,
				"season": season,
				"interval_km": interval_km,
				"interval_months": interval_months,
			}
		).insert()
