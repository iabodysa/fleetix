# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.boot import load_translations

import fleetix
from fleetix.fleetix.api.gate import LANGUAGES
from fleetix.fleetix.api.maintenance import WORKER_ROLES
from fleetix.fleetix.api.store import STORE_ROLES

no_cache = 1
RTL_LANGUAGES = ("ar", "ur")


def get_context(context):
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	context.csrf_token = csrf_token
	context.boot = frappe.as_json(get_boot(), indent=None)
	context.lang = frappe.local.lang
	context.direction = "rtl" if frappe.local.lang in RTL_LANGUAGES else "ltr"
	return context


def get_boot():
	roles = set(frappe.get_roles())
	bootinfo = frappe._dict(
		site_name=frappe.local.site,
		user=frappe.session.user,
		full_name=frappe.utils.get_fullname(frappe.session.user),
		is_worker=bool(roles & set(WORKER_ROLES)),
		is_store=bool(roles & set(STORE_ROLES)),
		app_version=fleetix.__version__,
		languages=LANGUAGES,
	)
	load_translations(bootinfo)
	return bootinfo
