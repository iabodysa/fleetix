# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re

import frappe
from erpnext.setup.doctype.driver.driver import Driver
from frappe import _

NATIONAL_ID = re.compile(r"[12]\d{9}")


def clean_national_id(value):
	number = "".join(str(int(char)) if char.isdecimal() else char for char in re.sub(r"\s", "", value or ""))
	if not NATIONAL_ID.fullmatch(number):
		frappe.throw(_("National ID or Iqama number must be 10 digits starting with 1 or 2"))
	return number


class DriverService(Driver):
	def before_insert(self):
		self.national_id = clean_national_id(self.national_id)

	def validate(self):
		self.national_id = clean_national_id(self.national_id)


def allow_guest_uploads():
	if frappe.db.get_single_value("System Settings", "allow_guests_to_upload_files"):
		return
	settings = frappe.get_single("System Settings")
	settings.allow_guests_to_upload_files = 1
	settings.flags.ignore_permissions = True
	settings.save()
