# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from frappe import _

FLEETIX_LINKS = {
	"Customer": {
		"Vehicle Assignment": "customer",
		"Vehicle Request": "customer",
		"Project Rental Charge": "customer",
		"Project Claim": "customer",
		"Accident": "customer",
		"Damage": "customer",
	},
	"Driver": {
		"Vehicle Assignment": "driver",
		"Vehicle Handover": "to_driver",
		"Vehicle Request": "driver",
		"Training Record": "driver",
		"Maintenance": "driver",
		"Project Rental Charge": "driver",
		"Project Claim": "driver",
		"Accident": "driver",
		"Damage": "driver",
	},
	"Project": {
		"Vehicle Assignment": "project",
		"Vehicle Handover": "to_project",
		"Vehicle Request": "project",
		"Training Record": "project",
		"Maintenance": "project",
		"Project Rental Charge": "project",
		"Project Claim": "project",
		"Accident": "project",
		"Damage": "project",
	},
	"Vehicle": {
		"Vehicle Assignment": "vehicle",
		"Vehicle Handover": "vehicle",
		"Vehicle Inspection": "vehicle",
		"Vehicle Request": "selected_vehicle",
		"Maintenance": "vehicle",
		"Component Replacement Log": "vehicle",
		"Rental Rate": "vehicle",
		"Project Rental Charge": "vehicle",
		"Insurance Claim": "vehicle",
		"Accident": "vehicle",
		"Damage": "vehicle",
	},
	"Sales Invoice": {
		"Project Rental Charge": "sales_invoice",
	},
}


def extend_dashboard(parent, data):
	links = FLEETIX_LINKS[parent]
	if not data.get("fieldname"):
		data["fieldname"] = next(iter(links.values()))
	transactions = data.setdefault("transactions", [])
	non_standard = data.get("non_standard_fieldnames") or {}
	listed = {item for group in transactions for item in group.get("items", [])}
	items = [doctype for doctype in links if doctype not in listed]
	for doctype in items:
		if links[doctype] != data["fieldname"]:
			non_standard[doctype] = links[doctype]
	data["non_standard_fieldnames"] = non_standard
	if items:
		transactions.append({"label": _("Fleetix"), "items": items})
	return data


def get_dashboard_for_customer(data):
	return extend_dashboard("Customer", data)


def get_dashboard_for_driver(data):
	return extend_dashboard("Driver", data)


def get_dashboard_for_project(data):
	return extend_dashboard("Project", data)


def get_dashboard_for_vehicle(data):
	return extend_dashboard("Vehicle", data)


def get_dashboard_for_sales_invoice(data):
	return extend_dashboard("Sales Invoice", data)
