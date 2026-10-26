# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe


def execute():
	if not frappe.db.exists("Notification", "Maintenance Awaiting Approval"):
		return
	notification = frappe.get_doc("Notification", "Maintenance Awaiting Approval")
	if notification.enabled:
		notification.enabled = 0
		notification.save()
