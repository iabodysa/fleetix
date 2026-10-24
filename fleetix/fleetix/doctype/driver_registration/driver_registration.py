# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from fleetix.fleetix.driver import clean_national_id

ATTACHMENTS = ("id_image", "license_image", "photo")
FILE_TYPES = (".jpg", ".jpeg", ".png", ".pdf")
MAX_FILE_BYTES = 5 * 1024 * 1024
TOKEN_SECONDS = 3600


class DriverRegistration(Document):
	def before_insert(self):
		if self.company_website:
			frappe.throw(_("Registration could not be received"))
		self.national_id = clean_national_id(self.national_id)
		if frappe.session.user == "Guest":
			self.validate_upload_token()
		self.upload_token = None
		if frappe.db.exists("Driver Registration", {"national_id": self.national_id, "status": "Open"}):
			frappe.throw(_("A registration for this ID number is already under review"))
		self.driver = frappe.db.get_value("Driver", {"national_id": self.national_id})
		self.status = "Linked" if self.driver else "Open"

	def validate_upload_token(self):
		session = frappe.cache.get_value(token_key(self.upload_token or ""))
		files = {self.get(fieldname) for fieldname in ATTACHMENTS if self.get(fieldname)}
		if not (session and files <= set(session["files"])):
			frappe.throw(_("Registration could not be received"))
		key = token_key(self.upload_token)
		frappe.db.after_commit.add(lambda: frappe.cache.delete_value(key))

	def validate(self):
		self.national_id = clean_national_id(self.national_id)
		for fieldname in ATTACHMENTS:
			self.validate_attachment(fieldname)

	def validate_attachment(self, fieldname):
		url = self.get(fieldname)
		if not url:
			return
		file = frappe.db.get_value("File", {"file_url": url}, ["is_private", "file_size"], as_dict=True)
		if not (file and file.is_private and url.lower().endswith(FILE_TYPES)):
			frappe.throw(_("{0} must be a JPG, PNG or PDF file").format(_(self.meta.get_label(fieldname))))
		if file.file_size > MAX_FILE_BYTES:
			frappe.throw(_("{0} must be 5 MB or smaller").format(_(self.meta.get_label(fieldname))))

	def after_insert(self):
		for fieldname in ATTACHMENTS:
			self.claim_file(fieldname)
		if self.driver:
			self.copy_files_to_driver()

	def claim_file(self, fieldname):
		name = frappe.db.get_value(
			"File",
			{
				"file_url": self.get(fieldname),
				"owner": frappe.session.user,
				"attached_to_name": ("is", "not set"),
			},
		)
		if not (self.get(fieldname) and name):
			return
		file = frappe.get_doc("File", name)
		file.update(
			{
				"attached_to_doctype": self.doctype,
				"attached_to_name": self.name,
				"attached_to_field": fieldname,
			}
		)
		file.save(ignore_permissions=True)

	def copy_files_to_driver(self):
		for fieldname in ATTACHMENTS:
			if self.get(fieldname):
				frappe.get_doc(
					{
						"doctype": "File",
						"file_url": self.get(fieldname),
						"attached_to_doctype": "Driver",
						"attached_to_name": self.driver,
						"is_private": 1,
					}
				).insert(ignore_permissions=True)

	@frappe.whitelist()
	def create_driver(self):
		frappe.has_permission("Driver", "create", throw=True)
		if self.driver:
			return self.driver
		driver = frappe.get_doc(
			{
				"doctype": "Driver",
				"national_id": self.national_id,
				"full_name": self.full_name_ar,
				"cell_number": self.cell_number,
				"license_number": self.license_number,
				"expiry_date": self.license_expiry_date,
			}
		).insert()
		self.update({"driver": driver.name, "status": "Linked"})
		self.save()
		self.copy_files_to_driver()
		return driver.name


def token_key(token):
	return f"fleetix:driver-registration:{token}"
