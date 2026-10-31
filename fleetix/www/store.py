# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.boot import load_translations

import fleetix
from fleetix.fleetix.api import store
from fleetix.fleetix.api.gate import LANGUAGES

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
	is_store = bool(set(frappe.get_roles()) & set(store.STORE_ROLES))
	bootinfo = frappe._dict(
		site_name=frappe.local.site,
		user=frappe.session.user,
		full_name=frappe.utils.get_fullname(frappe.session.user),
		is_store=is_store,
		app_version=fleetix.__version__,
		languages=LANGUAGES,
	)
	if is_store:
		bootinfo.update(store.get_boot())
	load_translations(bootinfo)
	return bootinfo
