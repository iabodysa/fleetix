# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re
from difflib import SequenceMatcher

import erpnext
import frappe
from erpnext.stock.utils import scan_barcode
from frappe.utils import cint, flt

from fleetix.fleetix.doctype.maintenance.maintenance import unpriced_items

STORE_ROLES = ("Stock Manager", "Stock User", "Rental Manager", "System Manager")
PAGE_SIZE = 20
SUGGESTIONS = 5
MODELS_FIELD = "fleetix_vehicle_models"
MODELS_SEPARATOR = "\u060c"
TASHKEEL = re.compile("[\u0640\u064b-\u0652\u0670]")
LETTERS = str.maketrans("\u0623\u0625\u0622\u0629\u0649", "\u0627\u0627\u0627\u0647\u064a")


def normalise(text):
	text = TASHKEEL.sub("", str(text or "")).translate(LETTERS).lower()
	return " ".join(text.split())


def default_warehouse():
	return frappe.db.get_single_value("Stock Settings", "default_warehouse")


def available(item_code, warehouse):
	return flt(frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty"))


@frappe.whitelist()
def get_boot():
	frappe.only_for(STORE_ROLES)
	models = set()
	for value in frappe.get_list("Item", filters={"disabled": 0}, pluck=MODELS_FIELD, limit_page_length=0):
		models.update(part.strip() for part in (value or "").split(MODELS_SEPARATOR) if part.strip())
	return {
		"user": frappe.session.user,
		"full_name": frappe.utils.get_fullname(frappe.session.user),
		"lang": frappe.local.lang,
		"warehouse": default_warehouse(),
		"models": sorted(models),
		"groups": frappe.get_list("Item Group", filters={"is_group": 0}, pluck="name", order_by="name"),
	}


@frappe.whitelist()
def pending_issues(start=0):
	frappe.only_for(STORE_ROLES)
	entries = frappe.get_list(
		"Stock Entry",
		filters={"docstatus": 0, "stock_entry_type": "Material Issue", "maintenance": ("is", "set")},
		fields=["name", "maintenance", "vehicle", "creation"],
		order_by="creation asc",
		start=cint(start),
		limit_page_length=PAGE_SIZE,
	)
	rows = frappe.get_list(
		"Stock Entry Detail",
		parent_doctype="Stock Entry",
		filters={"parent": ("in", [entry.name for entry in entries])},
		fields=["parent", "item_code", "item_name", "image", "qty", "s_warehouse"],
		order_by="idx asc",
	)
	return [
		{
			"name": entry.name,
			"maintenance": entry.maintenance,
			"plate": entry.vehicle,
			"creation": entry.creation,
			"items": [
				{
					"item_code": row.item_code,
					"item_name": row.item_name,
					"image": row.image,
					"qty": row.qty,
					"available": available(row.item_code, row.s_warehouse),
				}
				for row in rows
				if row.parent == entry.name
			],
		}
		for entry in entries
	]


@frappe.whitelist(methods=["POST"])
def approve_issue(stock_entry):
	frappe.only_for(STORE_ROLES)
	entry = frappe.get_doc("Stock Entry", stock_entry)
	entry.submit()
	return {"name": entry.name, "docstatus": entry.docstatus}


def rate_known(item_code):
	company = erpnext.get_default_company()
	return not unpriced_items([item_code], company)


@frappe.whitelist()
def scan(code):
	frappe.only_for(STORE_ROLES)
	code = (code or "").strip()
	found = scan_barcode(code)
	item_code = found.get("item_code")
	if not item_code and frappe.db.exists("Item", code):
		item_code = code
	if not item_code:
		item_code = frappe.db.get_value("Item Supplier", {"supplier_part_no": code}, "parent")
	if not item_code:
		return {"unknown": 1, "code": code, "suggestions": suggest_items(code)}
	item = frappe.get_doc("Item", item_code)
	item.check_permission("read")
	return {
		"item_code": item.name,
		"item_name": item.item_name,
		"image": item.image,
		"has_serial_no": item.has_serial_no,
		"serial_no": found.get("serial_no"),
		"rate_known": rate_known(item.name),
		"available": available(item.name, default_warehouse()),
	}


@frappe.whitelist()
def suggest_items(txt, model=""):
	frappe.only_for(STORE_ROLES)
	filters = {"disabled": 0, "is_stock_item": 1}
	if model:
		filters[MODELS_FIELD] = ("like", f"%{model}%")
	wanted = normalise(txt)
	items = frappe.get_list(
		"Item", filters=filters, fields=["name", "item_name", "image"], limit_page_length=0
	)
	scored = sorted(
		items,
		key=lambda item: max(
			SequenceMatcher(None, wanted, normalise(item.item_name)).ratio(),
			SequenceMatcher(None, wanted, normalise(item.name)).ratio(),
		),
		reverse=True,
	)
	return [
		{"item_code": item.name, "item_name": item.item_name, "image": item.image}
		for item in scored[:SUGGESTIONS]
	]


def link_barcode(item_code, code):
	if not code or frappe.db.exists("Item Barcode", {"barcode": code}):
		return
	item = frappe.get_doc("Item", item_code)
	item.append("barcodes", {"barcode": code})
	item.save()


@frappe.whitelist(methods=["POST"])
def receive(item_code, qty, code="", serials="", rate=None):
	frappe.only_for(STORE_ROLES)
	link_barcode(item_code, code)
	warehouse = default_warehouse()
	row = {"item_code": item_code, "qty": flt(qty), "t_warehouse": warehouse}
	if cint(frappe.get_cached_value("Item", item_code, "has_serial_no")):
		row.update(use_serial_batch_fields=1, serial_no=serials)
	if flt(rate):
		row.update(basic_rate=flt(rate), set_basic_rate_manually=1)
	entry = frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Receipt",
			"company": erpnext.get_default_company(),
			"to_warehouse": warehouse,
			"items": [row],
		}
	)
	entry.insert()
	entry.submit()
	return {"stock_entry": entry.name, "qty": flt(qty)}


def next_part_code():
	last = frappe.get_list(
		"Item", filters={"name": ("like", "SP-%")}, pluck="name", order_by="name desc", limit_page_length=1
	)
	number = cint(last[0].split("-", 1)[1]) if last else 0
	return f"SP-{number + 1:05d}"


@frappe.whitelist(methods=["POST"])
def new_part(name_ar, item_group, vehicle_model="", code=""):
	frappe.only_for(STORE_ROLES)
	item = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": next_part_code(),
			"item_name": name_ar,
			"item_group": item_group,
			"stock_uom": "Nos",
			"is_stock_item": 1,
			MODELS_FIELD: vehicle_model,
			"barcodes": [{"barcode": code}] if code else [],
		}
	)
	item.insert()
	return item.name
