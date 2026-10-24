# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from fleetix.fleetix.doctype.driver_registration.driver_registration import (
	ATTACHMENTS,
	MAX_FILE_BYTES,
	TOKEN_SECONDS,
	token_key,
)

SIGNATURES = {b"\x89PNG\r\n\x1a\n": "png", b"\xff\xd8\xff": "jpg", b"%PDF-": "pdf"}
UPLOADS_PER_TOKEN = 6


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=10, seconds=600)
def start():
	token = frappe.generate_hash(length=32)
	frappe.cache.set_value(
		token_key(token), {"ip": frappe.local.request_ip, "files": []}, expires_in_sec=TOKEN_SECONDS
	)
	return token


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=20, seconds=600)
def upload(token, fieldname, company_website=None):
	session = frappe.cache.get_value(token_key(token or ""))
	if company_website or not session or session["ip"] != frappe.local.request_ip:
		frappe.throw(_("Registration could not be received"), frappe.PermissionError)
	if fieldname not in ATTACHMENTS or len(session["files"]) >= UPLOADS_PER_TOKEN:
		frappe.throw(_("Registration could not be received"), frappe.PermissionError)
	if (frappe.request.content_length or 0) > MAX_FILE_BYTES + 65536:
		frappe.throw(_("The file must be 5 MB or smaller"))
	upload = frappe.request.files.get("file")
	content = upload.stream.read(MAX_FILE_BYTES + 1) if upload else b""
	if len(content) > MAX_FILE_BYTES:
		frappe.throw(_("The file must be 5 MB or smaller"))
	extension = next((ext for magic, ext in SIGNATURES.items() if content.startswith(magic)), None)
	if not extension:
		frappe.throw(_("The file must be a JPG, PNG or PDF file"))
	file = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"{fieldname}.{extension}",
			"is_private": 1,
			"content": content,
		}
	).insert(ignore_permissions=True)
	session["files"].append(file.file_url)
	frappe.cache.set_value(token_key(token), session, expires_in_sec=TOKEN_SECONDS)
	return file.file_url
