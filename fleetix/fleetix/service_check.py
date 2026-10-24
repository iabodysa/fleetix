# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from fleetix.fleetix.vehicle import parse_fieldnames

DEFAULT_SERVICE_CHECKLIST = (
	"Wipers",
	"Washer Fluid",
	"Radiator Coolant",
	"Brake Fluid",
	"Tyre Pressure",
	"Lights",
	"Windscreen Cleaned",
	"Battery Terminals",
	"Belts",
	"Air Filter Check",
)
PART_DONE = "Installed"
SERVICE_ANSWERS = ("Done", "Not Done")
NOT_DONE = "Not Done"


def service_checklist():
	configured = parse_fieldnames(frappe.get_cached_doc("Fleetix Settings").service_checklist)
	return [{"item": name, "label": _(name)} for name in configured or DEFAULT_SERVICE_CHECKLIST]


def checked_rows(rows, parts):
	answers = {row.get("item"): row.get("condition") for row in rows or []}
	unanswered = [_(part) for part in parts if answers.get(part) != PART_DONE]
	unanswered += [
		row["label"] for row in service_checklist() if answers.get(row["item"]) not in SERVICE_ANSWERS
	]
	if unanswered:
		frappe.throw(_("Answer every row of the final check: {0}").format(", ".join(unanswered)))
	return [{"item": item, "condition": condition} for item, condition in answers.items()]


def finding_rows(findings, checked):
	rows = [
		{"part": row.get("part"), "reason": row.get("reason"), "note": row.get("note")}
		for row in findings or []
		if row.get("part")
	]
	noted = {(row["part"], row["reason"]) for row in rows}
	for row in checked:
		if row["condition"] == NOT_DONE and (row["item"], NOT_DONE) not in noted:
			rows.append({"part": row["item"], "reason": NOT_DONE, "note": None})
	return rows


def last_findings(doctype, filters, exclude=None):
	if exclude:
		filters = dict(filters, name=("!=", exclude))
	for name in frappe.get_all(doctype, filters=filters, order_by="creation desc", limit=5, pluck="name"):
		rows = frappe.get_all(
			"Maintenance Finding",
			filters={"parent": name, "parenttype": doctype},
			fields=["part", "reason", "note"],
			order_by="idx asc",
		)
		if rows:
			return {"visit": name, "date": frappe.db.get_value(doctype, name, "creation"), "rows": rows}
	return None
