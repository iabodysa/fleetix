# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import cint
from frappe.utils.jinja_globals import is_rtl

from fleetix.fleetix.doctype.maintenance.maintenance import manager_signable

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=" + quote(frappe.request.path)
		raise frappe.Redirect(302)
	if not frappe.form_dict.visit or not frappe.db.exists("Maintenance", frappe.form_dict.visit):
		raise frappe.PageDoesNotExistError
	visit = manager_signable(frappe.form_dict.visit)
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	vehicle = frappe.db.get_value(
		"Vehicle", visit.vehicle, ["license_plate", "make", "model", "last_odometer"], as_dict=True
	)
	reading = cint(visit.odometer) or cint(vehicle.last_odometer)
	context.csrf_token = csrf_token
	context.lang = frappe.local.lang
	context.direction = "rtl" if is_rtl() else "ltr"
	context.visit = visit.name
	context.plate = vehicle.license_plate
	context.model = " ".join(filter(None, (vehicle.make, vehicle.model)))
	context.status = _(visit.status)
	context.odometer = "{:,}".format(reading) if reading else None
	context.delegate = frappe.db.get_value("Driver", visit.driver, "full_name") if visit.driver else None
	context.signed = bool(visit.manager_signature)
	return context
