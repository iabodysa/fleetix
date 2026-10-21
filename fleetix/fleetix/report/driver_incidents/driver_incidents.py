# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_months, getdate, today

from fleetix.fleetix.doctype.project_claim.project_claim import claim_amount
from fleetix.fleetix.titles import titles

INCIDENTS = {
	"Accident": ("accident_datetime", ["responsibility_percentage"]),
	"Damage": ("creation", []),
}
CLOSED_CLAIM_STATES = ("Paid", "Rejected")
COLORS = ["#2a78d6", "#eb6834"]


def execute(filters=None):
	filters = frappe._dict(filters or {})
	from_date = getdate(filters.from_date or add_months(today(), -12))
	to_date = getdate(filters.to_date or today())

	incidents = []
	for doctype, (date_field, extra_fields) in INCIDENTS.items():
		conditions = {date_field: ("between", [from_date, to_date])}
		conditions.update({key: filters[key] for key in ("company", "project") if filters.get(key)})
		for row in frappe.get_list(
			doctype,
			filters=conditions,
			fields=[
				"driver",
				"charged_to_driver",
				"estimated_cost",
				f"{date_field} as incident_date",
				*extra_fields,
			],
			limit_page_length=0,
		):
			row.doctype = doctype
			row.party = row.charged_to_driver or row.driver
			if not filters.driver or row.party == filters.driver:
				incidents.append(row)

	summary = {}
	for row in incidents:
		entry = summary_row(summary, row.party)
		entry["accidents" if row.doctype == "Accident" else "damages"] += 1
		if row.charged_to_driver:
			entry["charged_amount"] += claim_amount(row)

	if frappe.has_permission("Project Claim", "read"):
		claim_filters = {"status": ("not in", CLOSED_CLAIM_STATES), "driver": ("is", "set")}
		if filters.driver:
			claim_filters["driver"] = filters.driver
		for claim in frappe.get_list(
			"Project Claim", filters=claim_filters, fields=["driver"], limit_page_length=0
		):
			summary_row(summary, claim.driver)["open_claims"] += 1

	driver_names = titles("Driver", list(summary), "full_name")
	data = sorted(summary.values(), key=lambda entry: entry["accidents"] + entry["damages"], reverse=True)
	for entry in data:
		entry["driver_name"] = driver_names.get(entry["driver"])
	return get_columns(), data, None, get_chart(incidents, from_date, to_date)


def summary_row(summary, driver):
	return summary.setdefault(
		driver,
		{"driver": driver, "accidents": 0, "damages": 0, "charged_amount": 0.0, "open_claims": 0},
	)


def get_columns():
	return [
		{"fieldname": "driver", "label": _("Driver"), "fieldtype": "Link", "options": "Driver", "width": 130},
		{"fieldname": "driver_name", "label": _("Driver Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "accidents", "label": _("Accidents"), "fieldtype": "Int", "width": 100},
		{"fieldname": "damages", "label": _("Damages"), "fieldtype": "Int", "width": 100},
		{"fieldname": "charged_amount", "label": _("Charged Amount"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "open_claims", "label": _("Open Claims"), "fieldtype": "Int", "width": 110},
	]


def get_chart(incidents, from_date, to_date):
	months, cursor = [], from_date.replace(day=1)
	while cursor <= to_date:
		months.append(cursor.strftime("%Y-%m"))
		cursor = getdate(add_months(cursor, 1))
	counts = {doctype: dict.fromkeys(months, 0) for doctype in INCIDENTS}
	for row in incidents:
		month = getdate(row.incident_date).strftime("%Y-%m")
		counts[row.doctype][month] = counts[row.doctype].get(month, 0) + 1
	return {
		"data": {
			"labels": months,
			"datasets": [
				{"name": _("Accidents"), "values": [counts["Accident"][month] for month in months]},
				{"name": _("Damages"), "values": [counts["Damage"][month] for month in months]},
			],
		},
		"type": "bar",
		"colors": COLORS,
	}
