# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.utils import flt

from fleetix.fleetix.units import unit_label

LABOUR_GROUP = re.compile(r"labou?r|service", re.I)


def vat_rate(company):
	template = (
		frappe.db.get_value("Sales Taxes and Charges Template", {"is_default": 1, "company": company})
		if company
		else None
	)
	rates = (
		frappe.get_all(
			"Sales Taxes and Charges",
			filters={"parent": template, "parenttype": "Sales Taxes and Charges Template"},
			pluck="rate",
		)
		if template
		else []
	)
	if rate := sum(flt(rate) for rate in rates):
		return rate
	settings = frappe.get_cached_doc("Fleetix Settings")
	return flt(
		settings.meta.get_field("vat_rate").default if settings.vat_rate is None else settings.vat_rate
	)


def _labour_codes(codes):
	if not codes:
		return set()
	items = frappe.get_all(
		"Item", filters={"name": ("in", list(codes))}, fields=["name", "is_stock_item", "item_group"]
	)
	return {
		item.name for item in items if not item.is_stock_item or LABOUR_GROUP.search(item.item_group or "")
	}


def maintenance_invoice(doc):
	rows = []
	if doc.items_issued:
		rows = [
			(row.item_code, row.item_name or row.item_code, row.qty, unit_label(row.stock_uom))
			for row in frappe.get_all(
				"Stock Entry Detail",
				filters={"parent": doc.items_issued, "parenttype": "Stock Entry"},
				fields=["item_code", "item_name", "qty", "stock_uom"],
				order_by="idx asc",
			)
		]
	if not rows:
		rows = [
			(
				row.item,
				_(row.component) + (f" - {row.item}" if row.item else ""),
				row.qty or 1,
				unit_label(
					frappe.get_cached_value("Item", row.item, "stock_uom") if row.item else None,
					row.component,
				),
			)
			for row in doc.components_replaced or []
		]
	labour_codes = _labour_codes({row[0] for row in rows if row[0]})
	parts = [row[1:] for row in rows if row[0] not in labour_codes]
	labour = [row[1:] for row in rows if row[0] in labour_codes]
	if doc.related_damage:
		labour += [
			(row.description, row.qty, None)
			for row in frappe.get_all(
				"Damage Cost Item",
				filters={"parent": doc.related_damage, "parenttype": "Damage", "item_type": "Labour"},
				fields=["description", "qty"],
				order_by="idx asc",
			)
		]
	company = doc.company or (frappe.db.get_value("Vehicle", doc.vehicle, "company") if doc.vehicle else None)
	return frappe._dict(company=company, parts=parts, labour=labour)
