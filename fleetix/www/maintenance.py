# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.boot import load_translations
from frappe.utils.jinja_globals import is_rtl

import fleetix
from fleetix.fleetix.api.maintenance import RTL_LANGUAGES, WORKER_ROLES
from fleetix.fleetix.shift_worker import current_worker

no_cache = 1


def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	context.csrf_token = csrf_token
	context.boot = frappe.as_json(get_boot(), indent=None)
	context.lang = frappe.local.lang
	context.direction = "rtl" if is_rtl() or frappe.local.lang in RTL_LANGUAGES else "ltr"
	return context


def get_boot():
	bootinfo = frappe._dict(
		site_name=frappe.local.site,
		user=frappe.session.user,
		lang=frappe.local.lang,
		full_name=frappe.utils.get_fullname(frappe.session.user),
		is_worker=bool(set(frappe.get_roles()) & set(WORKER_ROLES)),
		worker=current_worker(),
		app_version=fleetix.__version__,
	)
	load_translations(bootinfo)
	return bootinfo
