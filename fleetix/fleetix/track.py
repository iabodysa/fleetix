# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from urllib.parse import quote

import frappe
from frappe.utils import get_host_name_from_request, today
from frappe.www.printview import validate_key


def share_key(visit):
	key = frappe.db.get_value(
		"Document Share Key",
		{"reference_doctype": "Maintenance", "reference_docname": visit.name, "expires_on": (">=", today())},
		"key",
		order_by="expires_on desc",
	)
	return key or visit.get_document_share_key()


def track_url(visit):
	return (
		get_host_name_from_request()
		+ "/maintenance/track/"
		+ quote(visit.name)
		+ "?key="
		+ quote(share_key(visit))
	)


def keyed_visit(name, key):
	if not name or not isinstance(key, str) or not frappe.db.exists("Maintenance", name):
		raise frappe.PageDoesNotExistError
	visit = frappe.get_doc("Maintenance", name)
	if validate_key(key, visit) is False:
		raise frappe.PermissionError
	return visit
