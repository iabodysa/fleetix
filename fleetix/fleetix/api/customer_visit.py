# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import erpnext
import frappe
from frappe import _
from frappe.utils import cint, flt, now_datetime

from fleetix.fleetix.api.maintenance import WORKER_ROLES
from fleetix.fleetix.doctype.customer_visit.customer_visit import (
	PAYMENT_MODES,
	item_rates,
	mobile_digits,
	setup_problems,
	walkin_customer,
	walkin_invoice,
)
from fleetix.fleetix.service_check import checked_rows, finding_rows, last_findings, service_checklist

MIN_MOBILE_DIGITS = 9


@frappe.whitelist()
def get_walkin_setup():
	frappe.only_for(WORKER_ROLES)
	company = erpnext.get_default_company()
	return {
		"company": company,
		"problems": setup_problems(company),
		"modes": [{"mode": mode, "label": _(mode)} for mode in PAYMENT_MODES],
		"service_checklist": service_checklist(),
	}


@frappe.whitelist()
def find_customer(mobile):
	frappe.only_for(WORKER_ROLES)
	digits = mobile_digits(mobile)
	if len(digits) < MIN_MOBILE_DIGITS:
		return None
	return frappe.db.get_value(
		"Maintenance Customer", {"mobile_no": digits, "disabled": 0}, ["name", "customer_name"], as_dict=True
	)


@frappe.whitelist()
def get_item_rates(items):
	frappe.only_for(WORKER_ROLES)
	return item_rates(frappe.parse_json(items) or [])


@frappe.whitelist()
def get_plate_findings(plate):
	frappe.only_for(WORKER_ROLES)
	return last_findings("Customer Visit", {"plate": plate}) if plate else None


@frappe.whitelist(methods=["POST"])
def finish_customer_visit(
	plate, customer_name, mobile_no, items, final_check, findings=None, mode_of_payment=None, odometer=None
):
	frappe.only_for(WORKER_ROLES)
	company = erpnext.get_default_company()
	mobile = mobile_digits(mobile_no)
	rows = [row for row in frappe.parse_json(items) or [] if flt(row.get("qty")) > 0]
	if not plate or not customer_name or len(mobile) < MIN_MOBILE_DIGITS:
		frappe.throw(_("Enter the plate, the customer name and the mobile number"))
	if not rows:
		frappe.throw(_("Add at least one item"))
	if mode_of_payment not in PAYMENT_MODES:
		frappe.throw(_("Choose how the customer pays"))
	problems = setup_problems(company)
	if problems:
		frappe.throw(_("Customer maintenance is not set up: {0}").format("; ".join(problems)))
	stock_items = set(
		frappe.get_all(
			"Item", filters={"name": ("in", [r["item_code"] for r in rows]), "is_stock_item": 1}, pluck="name"
		)
	)
	checked = checked_rows(
		frappe.parse_json(final_check), [r["item_code"] for r in rows if r["item_code"] in stock_items]
	)
	visit = frappe.get_doc(
		{
			"doctype": "Customer Visit",
			"plate": plate.strip(),
			"customer": walkin_customer(customer_name.strip(), mobile),
			"mobile_no": mobile,
			"company": company,
			"visit_datetime": now_datetime(),
			"odometer": cint(odometer),
			"checklist": checked,
			"findings": finding_rows(frappe.parse_json(findings), checked),
		}
	)
	visit.insert()
	invoice = walkin_invoice(visit, rows, mode_of_payment)
	return {
		"visit": visit.name,
		"maintenance_invoice": invoice.name,
		"customer_name": invoice.customer_name,
		"plate": visit.plate,
		"net_total": invoice.net_total,
		"tax": invoice.vat_amount,
		"grand_total": invoice.grand_total,
		"mode_of_payment": _(mode_of_payment),
	}
