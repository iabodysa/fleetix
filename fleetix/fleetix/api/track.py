# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import base64
import binascii
import os

import frappe
import pyqrcode
from frappe import _
from frappe.rate_limiter import rate_limit

from fleetix.fleetix.api.maintenance import WORKER_ROLES
from fleetix.fleetix.document_qr import qr_data_url
from fleetix.fleetix.track import SIGN_STATES, keyed_visit, track_url

SIGNATURE_PREFIX = "data:image/png;base64,"
SIGNATURE_MAX = 300_000


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
		"image": qr_data_url(url),
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


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=10 * 60)
def sign(visit, key, signature):
	record = keyed_visit(visit, key)
	if record.driver_signature:
		frappe.throw(_("This visit is already signed"))
	if record.status not in SIGN_STATES:
		frappe.throw(_("This visit is not waiting for a signature"))
	if (
		not isinstance(signature, str)
		or not signature.startswith(SIGNATURE_PREFIX)
		or len(signature) > SIGNATURE_MAX
	):
		frappe.throw(_("Sign in the box"))
	try:
		base64.b64decode(signature[len(SIGNATURE_PREFIX) :], validate=True)
	except binascii.Error:
		frappe.throw(_("Sign in the box"))
	record.db_set("driver_signature", signature)
	return {"signed": 1}


@frappe.whitelist(methods=["POST"])
def get_driver_signature(maintenance):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("read")
	return visit.driver_signature
