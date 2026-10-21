# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from collections import defaultdict

import frappe
from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
from frappe import _
from frappe.utils import flt, formatdate, get_first_day, get_last_day

from fleetix.fleetix.doctype.project_rental_charge.project_rental_charge import attach_statement


@frappe.whitelist()
def create_monthly_invoice(customer, month):
	frappe.has_permission("Sales Invoice", "create", throw=True)
	frappe.has_permission("Project Rental Charge", "write", throw=True)
	start, end = get_first_day(month), get_last_day(month)
	charges = [
		charge
		for charge in frappe.get_list(
			"Project Rental Charge",
			filters={"docstatus": 1, "customer": customer, "period_from": ("between", (start, end))},
			fields=["name", "item", "amount", "sales_invoice"],
			order_by="period_from asc",
			limit_page_length=0,
		)
		if not charge.sales_invoice
		or frappe.db.get_value("Sales Invoice", charge.sales_invoice, "docstatus") in (None, 2)
	]
	if not charges:
		frappe.throw(
			_("No unbilled rental charges for {0} in {1}").format(customer, formatdate(start, "MM-yyyy"))
		)
	if missing := [charge.name for charge in charges if not charge.item]:
		frappe.throw(_("Set the item on rental charges {0}").format(", ".join(missing)))
	totals = defaultdict(float)
	for charge in charges:
		totals[charge.item] += flt(charge.amount)
	invoice = frappe.new_doc("Sales Invoice")
	invoice.customer = customer
	invoice.set_posting_time = 1
	invoice.posting_date = end
	invoice.due_date = end
	invoice.update(get_default_taxes_and_charges("Sales Taxes and Charges Template", company=invoice.company))
	for item, amount in totals.items():
		invoice.append("items", {"item_code": item, "qty": 1, "rate": amount})
	invoice.insert()
	names = [charge.name for charge in charges]
	frappe.db.set_value("Project Rental Charge", {"name": ("in", names)}, "sales_invoice", invoice.name)
	attach_statement(invoice.name, names)
	return invoice.name
