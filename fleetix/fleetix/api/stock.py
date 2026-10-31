# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from erpnext.stock.utils import scan_barcode
from frappe.utils import cint, flt

READ_ROLES = ("Movement Supervisor", "Rental Manager", "System Manager", "Stock Manager", "Stock User")
PAGE = 20
MODELS_FIELD = "fleetix_vehicle_models"
MODEL_SEPARATOR = "،"
STOCK_FILTERS = {"is_stock_item": 1, "disabled": 0}


def default_warehouse():
	return frappe.db.get_single_value("Stock Settings", "default_warehouse")


def split_models(value):
	return [model.strip() for model in (value or "").split(MODEL_SEPARATOR) if model.strip()]


def bin_qty(item_codes, warehouse):
	if not item_codes or not warehouse:
		return {}
	return dict(
		frappe.get_all(
			"Bin",
			filters={"item_code": ("in", item_codes), "warehouse": warehouse},
			fields=["item_code", "actual_qty"],
			as_list=True,
		)
	)


@frappe.whitelist()
def search_stock(txt="", model="", start=0):
	frappe.only_for(READ_ROLES)
	filters = dict(STOCK_FILTERS)
	if model:
		filters[MODELS_FIELD] = ("like", f"%{model}%")
	or_filters = None
	if txt:
		like = ("like", f"%{txt}%")
		or_filters = [
			["Item", "item_name", *like],
			["Item", "item_code", *like],
			["Item", "description", *like],
		]
		parents = frappe.get_list(
			"Item Barcode",
			parent_doctype="Item",
			filters={"barcode": like},
			pluck="parent",
			limit_page_length=0,
		)
		if parents:
			or_filters.append(["Item", "name", "in", parents])
	items = frappe.get_list(
		"Item",
		filters=filters,
		or_filters=or_filters,
		fields=["item_code", "item_name", "image"],
		order_by="item_name asc",
		limit_start=cint(start),
		limit_page_length=PAGE,
	)
	warehouse = default_warehouse()
	qty = bin_qty([item.item_code for item in items], warehouse)
	return [dict(item, qty=flt(qty.get(item.item_code)), warehouse=warehouse) for item in items]


@frappe.whitelist()
def stock_models():
	frappe.only_for(READ_ROLES)
	values = frappe.get_list(
		"Item",
		filters={**STOCK_FILTERS, MODELS_FIELD: ("is", "set")},
		pluck=MODELS_FIELD,
		distinct=True,
		limit_page_length=0,
	)
	return sorted({model for value in values for model in split_models(value)})


@frappe.whitelist()
def stock_item(item_code):
	frappe.only_for(READ_ROLES)
	item = frappe.get_doc("Item", item_code)
	item.check_permission("read")
	warehouse = default_warehouse()
	bins = frappe.get_all(
		"Bin",
		filters={"item_code": item.name, "actual_qty": (">", 0)},
		fields=["warehouse", "actual_qty as qty"],
		order_by="warehouse asc",
	)
	if warehouse and warehouse not in [row.warehouse for row in bins]:
		bins.insert(0, frappe._dict(warehouse=warehouse, qty=0))
	return {
		"item_code": item.name,
		"item_name": item.item_name,
		"item_group": item.item_group,
		"image": item.image,
		"vehicle_models": split_models(item.get(MODELS_FIELD)),
		"barcodes": [row.barcode for row in item.barcodes],
		"bins": [{"warehouse": row.warehouse, "qty": flt(row.qty)} for row in bins],
	}


@frappe.whitelist()
def scan_item(code):
	frappe.only_for(READ_ROLES)
	code = (code or "").strip()
	if not code:
		return {}
	item_code = scan_barcode(code).get("item_code")
	if not item_code and frappe.db.exists("Item", code):
		item_code = code
	return {"item_code": item_code} if item_code else {}
