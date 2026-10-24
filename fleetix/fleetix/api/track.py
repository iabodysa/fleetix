# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import os

import frappe
import pyqrcode

from fleetix.fleetix.api.maintenance import WORKER_ROLES
from fleetix.fleetix.track import keyed_visit, track_url


@frappe.whitelist(methods=["POST"])
def get_track_card(maintenance):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("read")
	url = track_url(visit)
	delegate = frappe.db.get_value("Driver", visit.driver, "full_name") if visit.driver else ""
	return {
		"url": url,
		"qr": pyqrcode.create(url).text(quiet_zone=2).split(),
		"delegate": delegate or "",
	}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def photo(visit, key, file_url):
	record = keyed_visit(visit, key)
	if file_url not in {row.attachment for row in record.photos}:
		raise frappe.PermissionError
	file = frappe.get_doc("File", {"file_url": file_url})
	frappe.local.response.filename = os.path.basename(file.file_name or file_url)
	frappe.local.response.filecontent = file.get_content()
	frappe.local.response.type = "download"
	frappe.local.response.display_content_as = "inline"
