# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.boot import load_translations
from frappe.utils.jinja_globals import is_rtl

from fleetix.fleetix.api.maintenance import WORKER_ROLES

no_cache = 1


def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	context.csrf_token = csrf_token
	context.boot = frappe.as_json(get_boot(), indent=None)
	context.direction = "rtl" if is_rtl() else "ltr"
	return context


def get_boot():
	bootinfo = frappe._dict(
		site_name=frappe.local.site,
		user=frappe.session.user,
		full_name=frappe.utils.get_fullname(frappe.session.user),
		is_worker=bool(set(frappe.get_roles()) & set(WORKER_ROLES)),
	)
	load_translations(bootinfo)
	return bootinfo
