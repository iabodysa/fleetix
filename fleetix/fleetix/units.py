# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

LITRE_UOMS = {"l", "lt", "ltr", "litre", "liter", "litres", "liters"}
COUNT_UOMS = {"nos", "no", "unit", "units", "each", "pcs", "pc", "piece", "pieces"}
TYRE_COMPONENTS = {"Front Tires", "Rear Tires"}


def is_litre(uom):
	return (uom or "").strip().lower() in LITRE_UOMS


def unit_label(uom, component=None):
	key = (uom or "").strip().lower()
	if key in LITRE_UOMS:
		return _("litre")
	if not key or key in COUNT_UOMS:
		return _("tyre") if component in TYRE_COMPONENTS else _("piece")
	return _(uom)


def pack_sizes(item_codes):
	sizes = {}
	for row in frappe.get_all(
		"UOM Conversion Detail",
		filters={
			"parent": ("in", list(item_codes) or [""]),
			"parenttype": "Item",
			"conversion_factor": (">", 1),
		},
		fields=["parent", "uom", "conversion_factor"],
		order_by="conversion_factor desc",
	):
		sizes.setdefault(row.parent, []).append({"uom": _(row.uom), "factor": flt(row.conversion_factor)})
	return sizes


def unit_fields(rows, component=None):
	sizes = pack_sizes([row["item_code"] for row in rows])
	for row in rows:
		row["unit"] = unit_label(row.get("stock_uom"), component)
		row["litres"] = is_litre(row.get("stock_uom"))
		row["packs"] = sizes.get(row["item_code"], [])
	return rows
