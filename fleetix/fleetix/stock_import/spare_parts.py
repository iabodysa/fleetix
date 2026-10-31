# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import json
import re
from pathlib import Path

import erpnext
import frappe
from erpnext.stock.stock_ledger import get_valuation_rate
from erpnext.stock.utils import get_stock_balance
from frappe.utils import cint, flt

DATA_FILE = Path(__file__).with_name("spare_parts.json")
MARKER = "fleetix-spare-parts:{}"
MARKER_FIELD = "fleetix_import_revision"
STOCK_UOM = "Nos"
MODELS_SEPARATOR = "\u060c "
ITEM_FIELDS = [
	"name",
	"item_name",
	"image",
	"fleetix_vehicle_models",
	"is_stock_item",
	"has_serial_no",
	"has_batch_no",
]


def normalise(text):
	return re.sub(r"\s+", " ", text or "").strip()


def load_data():
	return json.loads(DATA_FILE.read_text())


def reco_exists(revision):
	return frappe.db.exists(
		"Stock Reconciliation", {MARKER_FIELD: MARKER.format(revision), "docstatus": ("!=", 2)}
	)


def run_pending():
	revision = load_data()["revision"]
	if reco_exists(revision):
		return None
	result = run(0)
	print(f"fleetix spare parts {json.dumps(result, ensure_ascii=False)}")
	return result


def existing_items():
	items = {}
	for item in frappe.get_all(
		"Item",
		filters={"disabled": 0},
		fields=ITEM_FIELDS,
		order_by="creation asc",
	):
		items.setdefault(normalise(item.item_name), item)
	return items


def plan_part(part, item, warehouse, company, currency, perpetual):
	row = {
		"part": part,
		"item": item,
		"item_code": item.name if item else part["item_code"],
		"rate": part.get("rate"),
	}
	if flt(part["qty"]) < 0:
		row["negative"] = True
		return row
	if item and (not item.is_stock_item or item.has_serial_no or item.has_batch_no):
		row["skip"] = True
		return row
	current = flt(get_stock_balance(item.name, warehouse)) if item else 0
	row["delta"] = flt(part["qty"]) - current
	row["changed"] = bool(row["delta"])
	if row["changed"] and flt(part["qty"]) > 0 and row["rate"] is None:
		if item:
			row["rate"] = get_valuation_rate(
				item.name,
				warehouse,
				"Stock Reconciliation",
				None,
				currency=currency,
				company=company,
				raise_error_if_no_rate=False,
			)
		row["unpriced"] = not row["rate"] and perpetual
	return row


def run(dry_run=0):
	data = load_data()
	revision = data["revision"]
	company = erpnext.get_default_company()
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	currency = erpnext.get_company_currency(company)
	perpetual = cint(erpnext.is_perpetual_inventory_enabled(company))
	if not warehouse:
		return {"revision": revision, "warehouse": None, "reco": None}

	groups_new = sorted(
		{p["item_group"] for p in data["parts"]} - set(frappe.get_all("Item Group", pluck="name"))
	)
	by_name = existing_items()
	rows = []
	for part in data["parts"]:
		item = frappe.db.get_value(
			"Item",
			part["item_code"],
			ITEM_FIELDS,
			as_dict=True,
		) or by_name.get(normalise(part["name_ar"]))
		rows.append(plan_part(part, item, warehouse, company, currency, perpetual))

	changed = [r for r in rows if r.get("changed")]
	result = {
		"revision": revision,
		"warehouse": warehouse,
		"groups_new": len(groups_new),
		"items_new": sum(1 for r in rows if not r["item"]),
		"items_matched": sum(1 for r in rows if r["item"]),
		"images_set": sum(1 for r in rows if r["part"]["image"] and not (r["item"] and r["item"].image)),
		"reco_rows_changed": len(changed),
		"qty_in": sum(r["delta"] for r in changed if r["delta"] > 0),
		"qty_out": -sum(r["delta"] for r in changed if r["delta"] < 0),
		"unpriced": [r["item_code"] for r in rows if r.get("unpriced")],
		"skipped": [r["item_code"] for r in rows if r.get("skip")],
		"negative": [r["item_code"] for r in rows if r.get("negative")],
		"reco": None,
	}
	if cint(dry_run) or result["unpriced"]:
		return result

	for group in groups_new:
		frappe.get_doc({"doctype": "Item Group", "item_group_name": group, "is_group": 0}).insert()
	for row in rows:
		row["item_code"] = write_item(row)
	if changed:
		result["reco"] = write_reco(changed, revision, company, warehouse)
	return result


def write_item(row):
	part, item = row["part"], row["item"]
	models = MODELS_SEPARATOR.join(part["vehicle_models"]) or None
	if not item:
		doc = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": part["item_code"],
				"item_name": part["name_ar"],
				"description": part["name_en"],
				"item_group": part["item_group"],
				"stock_uom": STOCK_UOM,
				"is_stock_item": 1,
				"fleetix_vehicle_models": models,
				"image": part["image"],
				"valuation_rate": part.get("rate"),
			}
		).insert()
		return doc.name
	fill = {"image": part["image"], "fleetix_vehicle_models": models}
	empty = {field: value for field, value in fill.items() if value and not item.get(field)}
	if empty:
		doc = frappe.get_doc("Item", item.name)
		doc.update(empty)
		doc.save()
	return item.name


def write_reco(changed, revision, company, warehouse):
	items = []
	for row in changed:
		line = {"item_code": row["item_code"], "warehouse": warehouse, "qty": flt(row["part"]["qty"])}
		if row["rate"]:
			line["valuation_rate"] = flt(row["rate"])
		elif line["qty"]:
			line["allow_zero_valuation_rate"] = 1
		items.append(line)
	doc = frappe.get_doc(
		{
			"doctype": "Stock Reconciliation",
			"purpose": "Stock Reconciliation",
			"company": company,
			"set_warehouse": warehouse,
			MARKER_FIELD: MARKER.format(revision),
			"items": items,
		}
	).insert()
	doc.submit()
	return doc.name
