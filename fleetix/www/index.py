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
	context.client_logos = get_client_logos()
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
			"icon": "calendar",
			"title": _("Long-term supply"),
			"summary": _("Vehicles stay with your project month after month, not one-day rentals."),
		},
		{
			"icon": "van",
			"title": _("Vans and light vehicles"),
			"summary": _("Toyota Hiace in high-roof and low-roof, and Toyota Lite Ace for crews and delivery."),
		},
		{
			"icon": "swap",
			"title": _("Handover and replacement at our offices"),
			"summary": _("Collect and swap vehicles through our dedicated rental offices."),
		},
		{
			"icon": "shield",
			"title": _("Centrally managed insurance"),
			"summary": _("One cooperative policy for the fleet, checked against traffic records before every renewal."),
		},
		{
			"icon": "statement",
			"title": _("Monthly statement per project"),
			"summary": _("A usage and rental statement reaches you each month for matching before invoicing."),
		},
		{
			"icon": "pin",
			"title": _("Tracked by project"),
			"summary": _("Every vehicle is logged against its project, so you know what each project holds."),
		},
	]


CLIENT_LOGOS = (
	"client-01.webp",
	"client-03.webp",
	"client-04.webp",
	"client-05.webp",
	"client-07.webp",
	"client-09.webp",
	"client-10.webp",
	"client-11.webp",
	"client-12.webp",
	"client-15.webp",
	"client-16.webp",
)


def get_client_logos():
	return [f"/assets/fleetix/images/etihad/clients/{name}" for name in CLIENT_LOGOS]


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
