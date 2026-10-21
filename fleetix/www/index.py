# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import formatdate, getdate, nowdate, strip_html_tags
from frappe.utils.jinja_globals import is_rtl

no_cache = 1


def get_context(context):
	context.lang = frappe.local.lang
	context.layout_direction = "rtl" if is_rtl() else "ltr"
	context.cta = get_cta()
	context.services = get_services()
	context.holidays = get_upcoming_holidays()
	context.switch_lang = get_switch_lang()
	context.year = getdate().year


def get_cta():
	if frappe.session.user == "Guest":
		return {"route": "/login", "label": _("Login")}
	if frappe.get_cached_value("User", frappe.session.user, "user_type") == "System User":
		return {"route": "/app", "label": _("Continue to your workspace")}
	return {"route": "/me", "label": _("Continue to your account")}


def get_services():
	return [
		{
			"title": _("Vehicle Requests"),
			"summary": _("Request a vehicle and follow its assignment and handover."),
			"action": _("Open requests"),
			"route": "/app/transaction",
		},
		{
			"title": _("Operations"),
			"summary": _("Maintenance, accidents and damage in one place."),
			"action": _("Open operations"),
			"route": "/app/operations",
		},
		{
			"title": _("Fleet"),
			"summary": _("Vehicles, rental rates and fleet records."),
			"action": _("Open fleet"),
			"route": "/app/master",
		},
		{
			"title": _("My Account"),
			"summary": _("Update your details and follow your requests."),
			"action": _("Open my account"),
			"route": "/me",
		},
	]


def get_upcoming_holidays():
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	holiday_list = company and frappe.get_cached_value("Company", company, "default_holiday_list")
	if not holiday_list:
		return []

	holidays = frappe.get_all(
		"Holiday",
		filters={
			"parent": holiday_list,
			"parenttype": "Holiday List",
			"weekly_off": 0,
			"holiday_date": (">=", nowdate()),
		},
		fields=["holiday_date", "description"],
		order_by="holiday_date asc",
		limit=4,
	)
	return [
		{"date": formatdate(row.holiday_date, "d MMMM yyyy"), "description": strip_html_tags(row.description)}
		for row in holidays
	]


def get_switch_lang():
	if is_rtl():
		return {"code": "en", "label": "English"}
	return {"code": "ar", "label": frappe.db.get_value("Language", "ar", "language_name")}
