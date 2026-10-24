# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re

import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.stock.get_item_details import get_price_list_rate_for
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today

from fleetix.fleetix.units import unit_fields

PAYMENT_MODES = ("Cash", "Mada")


class CustomerVisit(Document):
	pass


def mobile_digits(mobile):
	return re.sub(r"\D", "", mobile or "")


def selling_price_list():
	return frappe.db.get_single_value("Selling Settings", "selling_price_list") or "Standard Selling"


def mode_problem(mode, company):
	if not frappe.db.exists("Mode of Payment", mode):
		return _("Payment method {0} is not set up").format(_(mode))
	if not frappe.db.get_value("Mode of Payment", mode, "enabled"):
		return _("Payment method {0} is disabled").format(_(mode))
	if not frappe.db.get_value(
		"Mode of Payment Account", {"parent": mode, "company": company}, "default_account"
	):
		return _("Payment method {0} has no account for {1}").format(_(mode), company)
	return None


def setup_problems(company):
	problems = []
	if not company:
		problems.append(_("No default company is set"))
		return problems
	if not frappe.db.get_single_value("Stock Settings", "default_warehouse"):
		problems.append(_("No default warehouse is set in Stock Settings"))
	if not frappe.db.exists("Price List", {"name": selling_price_list(), "selling": 1, "enabled": 1}):
		problems.append(_("Selling price list {0} is missing").format(selling_price_list()))
	if not frappe.db.exists("Sales Taxes and Charges Template", {"company": company, "is_default": 1}):
		problems.append(_("No default sales tax template for {0}").format(company))
	return problems


def item_rates(item_codes):
	price_list = selling_price_list()
	rows = []
	for item in frappe.get_all(
		"Item",
		filters={"name": ("in", list(item_codes)), "disabled": 0},
		fields=["name", "item_name", "stock_uom", "is_stock_item"],
	):
		rate = get_price_list_rate_for(
			{"price_list": price_list, "uom": item.stock_uom, "transaction_date": today(), "qty": 1},
			item.name,
		)
		rows.append(
			{
				"item_code": item.name,
				"item_name": item.item_name,
				"stock_uom": item.stock_uom,
				"is_stock_item": item.is_stock_item,
				"rate": flt(rate),
			}
		)
	return unit_fields(rows)


def walkin_customer(customer_name, mobile):
	existing = frappe.db.get_value("Customer", {"mobile_no": mobile, "disabled": 0}, "name")
	if existing:
		return existing
	customer = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": customer_name,
			"customer_type": "Individual",
			"customer_group": frappe.db.get_single_value("Selling Settings", "customer_group"),
			"territory": frappe.db.get_single_value("Selling Settings", "territory"),
			"mobile_no": mobile,
		}
	)
	customer.insert()
	return customer.name


def walkin_invoice(customer, company, items, mode):
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	invoice = frappe.new_doc("Sales Invoice")
	invoice.update(
		{
			"customer": customer,
			"company": company,
			"is_pos": 1,
			"update_stock": 1,
			"set_warehouse": warehouse,
			"selling_price_list": selling_price_list(),
		}
	)
	for row in items:
		invoice.append(
			"items", {"item_code": row["item_code"], "qty": flt(row["qty"]), "warehouse": warehouse}
		)
	invoice.taxes_and_charges = frappe.db.get_value(
		"Sales Taxes and Charges Template", {"is_default": 1, "company": company}
	)
	invoice.append_taxes_from_master()
	invoice.set_missing_values()
	invoice.calculate_taxes_and_totals()
	unpriced = [row.item_name for row in invoice.items if not flt(row.rate)]
	if unpriced:
		frappe.throw(_("No selling price for {0}. Tell the accountant.").format(", ".join(unpriced)))
	invoice.append(
		"payments",
		{
			"mode_of_payment": mode,
			"amount": invoice.rounded_total or invoice.grand_total,
			"account": get_bank_cash_account(mode, company)["account"],
		},
	)
	invoice.insert()
	invoice.submit()
	return invoice
