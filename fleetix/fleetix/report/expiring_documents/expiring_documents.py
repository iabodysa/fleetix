# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, cint, date_diff, getdate, today

DEFAULT_DAYS = 30


def execute(filters=None):
	filters = frappe._dict(filters or {})
	days = DEFAULT_DAYS if filters.days in (None, "") else cint(filters.days)
	limit = getdate(add_days(today(), days))
	customer = {"customer": filters.customer} if filters.customer else {}

	vehicles = frappe.get_list(
		"Vehicle",
		filters={"active": 1},
		fields=[
			"name",
			"current_driver",
			"registration_expiry",
			"periodic_inspection_expiry",
			"insurance_policy",
		],
		limit_page_length=0,
	)
	customers = dict(
		frappe.get_all(
			"Driver",
			filters={"name": ("in", [v.current_driver for v in vehicles if v.current_driver] or [""])},
			fields=["name", "customer"],
			as_list=True,
		)
	)
	for vehicle in vehicles:
		vehicle.customer = customers.get(vehicle.current_driver)
	if filters.customer:
		vehicles = [vehicle for vehicle in vehicles if vehicle.customer == filters.customer]
	policies = list({vehicle.insurance_policy for vehicle in vehicles if vehicle.insurance_policy})
	policy_end = (
		dict(
			frappe.get_list(
				"Insurance Policy",
				filters={"name": ("in", policies)},
				fields=["name", "end_date"],
				as_list=True,
			)
		)
		if policies
		else {}
	)

	rows = []
	for vehicle in vehicles:
		rows += [
			document_row(
				"Vehicle",
				vehicle.name,
				vehicle.name,
				vehicle.customer,
				_("Istimara"),
				vehicle.registration_expiry,
			),
			document_row(
				"Vehicle",
				vehicle.name,
				vehicle.name,
				vehicle.customer,
				_("Periodic Inspection"),
				vehicle.periodic_inspection_expiry,
			),
			document_row(
				"Vehicle",
				vehicle.name,
				vehicle.name,
				vehicle.customer,
				_("Insurance Policy"),
				policy_end.get(vehicle.insurance_policy),
			),
		]
	for driver in frappe.get_list(
		"Driver",
		filters={"status": ("!=", "Left"), "active": 1, **customer},
		fields=["name", "full_name", "customer", "expiry_date"],
		limit_page_length=0,
	):
		rows.append(
			document_row(
				"Driver",
				driver.name,
				driver.full_name,
				driver.customer,
				_("Driving Licence"),
				driver.expiry_date,
			)
		)

	data = [
		row
		for row in rows
		if (row["expiry"] and getdate(row["expiry"]) <= limit)
		or (not row["expiry"] and cint(filters.show_missing))
	]
	data.sort(key=lambda row: (row["expiry"] is None, row["days_left"] or 0, row["reference"]))
	return get_columns(), data


def document_row(doctype, name, title, customer, document, expiry):
	return {
		"reference_type": doctype,
		"reference": name,
		"title": title,
		"customer": customer,
		"document": document,
		"expiry": expiry,
		"days_left": date_diff(expiry, today()) if expiry else None,
	}


def get_columns():
	return [
		{
			"fieldname": "reference_type",
			"label": _("Type"),
			"fieldtype": "Link",
			"options": "DocType",
			"width": 90,
		},
		{
			"fieldname": "reference",
			"label": _("Reference"),
			"fieldtype": "Dynamic Link",
			"options": "reference_type",
			"width": 140,
		},
		{"fieldname": "title", "label": _("Name"), "fieldtype": "Data", "width": 180},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 140,
		},
		{"fieldname": "document", "label": _("Document"), "fieldtype": "Data", "width": 140},
		{"fieldname": "expiry", "label": _("Expiry"), "fieldtype": "Date", "width": 110},
		{"fieldname": "days_left", "label": _("Days Left"), "fieldtype": "Int", "width": 100},
	]
