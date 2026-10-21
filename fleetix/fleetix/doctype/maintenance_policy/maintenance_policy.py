# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

ANY = (None, "", "All")


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
