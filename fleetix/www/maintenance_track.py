# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from urllib.parse import urlencode

import frappe
from frappe import _
from frappe.utils import cint
from frappe.utils.jinja_globals import is_rtl

from fleetix.fleetix.maintenance_invoice import maintenance_invoice
from fleetix.fleetix.track import SIGN_STATES, keyed_visit

no_cache = 1

STAGES = ("Driver Arrived", "Full Inspection", "Approved", "Service", "Final Check", "Completed")
INVOICE_FORMAT = "Thermal Maintenance Invoice"


def get_context(context):
	key = frappe.form_dict.key
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	visit = keyed_visit(frappe.form_dict.visit, key)
	vehicle = frappe.db.get_value(
		"Vehicle", visit.vehicle, ["license_plate", "make", "model", "last_odometer"], as_dict=True
	)
	bill = maintenance_invoice(visit)
	current = STAGES.index(visit.status) if visit.status in STAGES else -1
	context.lang = frappe.local.lang
	context.direction = "rtl" if is_rtl() else "ltr"
	context.plate = vehicle.license_plate
	context.model = " ".join(filter(None, (vehicle.make, vehicle.model)))
	reading = cint(visit.odometer) or cint(vehicle.last_odometer)
	context.odometer = "{:,}".format(reading) if reading else None
	context.status = _(visit.status)
	context.delegate = frappe.db.get_value("Driver", visit.driver, "full_name") if visit.driver else None
	context.stages = [
		{"label": _(stage), "state": "done" if index < current else "current" if index == current else ""}
		for index, stage in enumerate(STAGES)
	]
	context.parts = [line_row(row) for row in bill.parts]
	context.labour = [line_row(row) for row in bill.labour]
	context.findings = findings(visit)
	context.visit = visit.name
	context.key = key
	context.csrf_token = csrf_token
	context.sign = visit.status in SIGN_STATES and not visit.driver_signature
	context.signed = bool(visit.driver_signature)
	context.photos = [
		{
			"caption": row.caption,
			"src": "/api/method/fleetix.fleetix.api.track.photo?"
			+ urlencode({"visit": visit.name, "key": key, "file_url": row.attachment}),
		}
		for row in visit.photos
	]
	phone = frappe.get_cached_value("Company", bill.company, "phone_no") if bill.company else None
	context.phone = phone
	context.invoice_url = (
		"/api/method/frappe.utils.print_format.download_pdf?"
		+ urlencode({"doctype": "Maintenance", "name": visit.name, "format": INVOICE_FORMAT, "key": key})
		if visit.status == "Completed"
		else None
	)
	return context


def line_row(row):
	return {"label": row[0], "qty": "{:g}".format(row[1] or 0)}


def findings(visit):
	rows = [_(row.component) for row in visit.components_replaced]
	rows += [
		f"{_(row.item)}: {row.notes}"
		for row in visit.final_check
		if row.condition == "Needs Repair" and row.notes
	]
	rows += frappe.get_all(
		"Damage", filters={"source": "Maintenance", "source_reference": visit.name}, pluck="description"
	)
	return rows
