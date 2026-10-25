# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from urllib.parse import unquote, urlparse

import frappe
from frappe import _
from frappe.utils import get_url_to_form

SHIFT_SECONDS = 12 * 60 * 60


def shift_key():
	return "fleetix:shift_worker:" + (frappe.session.sid or "")


def badge_employee(code):
	prefix = urlparse(get_url_to_form("Employee", "")).path.lower()
	path = urlparse((code or "").strip()).path
	name = unquote(path[len(prefix) :].strip("/")) if path.lower().startswith(prefix) else ""
	if not name or "/" in name:
		frappe.throw(_("This is not a worker badge"))
	return name


def allowed_worker(employee):
	worker = frappe.db.get_value("Employee", employee, ["name", "employee_name", "status"], as_dict=True)
	if not worker:
		frappe.throw(_("This is not a worker badge"))
	if worker.status != "Active":
		frappe.throw(_("This badge belongs to an inactive worker"))
	if not frappe.has_permission("Employee", "select", worker.name):
		frappe.throw(_("This worker is not allowed on this device"))
	return {"employee": worker.name, "employee_name": worker.employee_name}


def start_shift(code):
	worker = allowed_worker(badge_employee(code))
	frappe.cache.set_value(shift_key(), worker["employee"], expires_in_sec=SHIFT_SECONDS)
	return worker


def end_shift():
	frappe.cache.delete_value(shift_key())


def current_worker():
	employee = frappe.cache.get_value(shift_key())
	if not employee:
		return None
	worker = frappe.db.get_value("Employee", employee, ["name", "employee_name", "status"], as_dict=True)
	if not worker or worker.status != "Active":
		end_shift()
		return None
	return {"employee": worker.name, "employee_name": worker.employee_name}


def stamp_worker(doc, tables):
	if doc.docstatus == 1 and doc._action == "update_after_submit":
		return
	worker = current_worker()
	if not worker:
		return
	doc.worker = worker["employee"]
	for table in tables:
		for row in doc.get(table):
			if not row.get("worker"):
				row.worker = worker["employee"]
