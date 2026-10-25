# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re

import frappe
from erpnext.stock.get_item_details import get_price_list_rate_for
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, now_datetime, today

from fleetix.fleetix.shift_worker import stamp_worker
from fleetix.fleetix.units import unit_fields


class CustomerVisit(Document):
	def validate(self):
		stamp_worker(self, ("checklist", "findings"))


def mobile_digits(mobile):
	return re.sub(r"\D", "", mobile or "")


def selling_price_list():
	return frappe.db.get_single_value("Selling Settings", "selling_price_list") or "Standard Selling"


def setup_problems(company):
	problems = []
	if not company:
		problems.append(_("No default company is set"))
		return problems
	if not frappe.db.exists("Price List", {"name": selling_price_list(), "selling": 1, "enabled": 1}):
		problems.append(_("Selling price list {0} is missing").format(selling_price_list()))
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
	existing = frappe.db.get_value("Maintenance Customer", {"mobile_no": mobile}, "name")
	if existing:
		return existing
	customer = frappe.get_doc(
		{"doctype": "Maintenance Customer", "customer_name": customer_name, "mobile_no": mobile}
	)
	customer.insert()
	return customer.name


def walkin_invoice(visit, items):
	priced = {row["item_code"]: row for row in item_rates({row["item_code"] for row in items})}
	unpriced = [row["item_code"] for row in items if not flt(priced.get(row["item_code"], {}).get("rate"))]
	if unpriced:
		frappe.throw(
			_("No selling price for {0}. Tell the accountant.").format(
				", ".join(priced[code]["item_name"] if code in priced else code for code in unpriced)
			)
		)
	invoice = frappe.get_doc(
		{
			"doctype": "Maintenance Invoice",
			"customer": visit.customer,
			"plate": visit.plate,
			"company": visit.company,
			"posting_datetime": now_datetime(),
			"customer_visit": visit.name,
			"status": "Issued",
			"mode_of_payment": "Cash",
			"paid": 1,
		}
	)
	for row in items:
		item = priced[row["item_code"]]
		invoice.append(
			"items",
			{
				"item_code": item["item_code"],
				"description": item["item_name"],
				"kind": "Part" if item["is_stock_item"] else "Labour",
				"qty": flt(row["qty"]),
				"uom": item["stock_uom"],
				"rate": item["rate"],
			},
		)
	invoice.insert()
	return invoice
