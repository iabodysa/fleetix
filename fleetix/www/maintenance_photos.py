# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils.jinja_globals import is_rtl

from fleetix.fleetix.api.maintenance import get_photos, get_vehicle_checklist

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=" + quote(frappe.request.path)
		raise frappe.Redirect(302)
	if not frappe.form_dict.visit:
		raise frappe.PageDoesNotExistError
	visit = get_vehicle_checklist(frappe.form_dict.visit)
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	steps = [_("Vehicle"), _("Odometer"), _("Items and parts"), _("Photos"), _("Approval"), _("Review")]
	current = steps.index(_("Photos"))
	context.csrf_token = csrf_token
	context.lang = frappe.local.lang
	context.direction = "rtl" if is_rtl() else "ltr"
	context.visit = visit
	context.odometer = "{:,}".format(max(visit["odometer"], visit["vehicle"]["last_odometer"]))
	context.photo_count = len(get_photos(visit["maintenance"]))
	context.steps = [
		{"label": label, "state": "done" if index < current else "current" if index == current else ""}
		for index, label in enumerate(steps)
	]
	return context
