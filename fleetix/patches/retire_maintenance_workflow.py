# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe


def execute():
	if not frappe.db.exists("Workflow", "Maintenance"):
		return
	workflow = frappe.get_doc("Workflow", "Maintenance")
	if workflow.is_active:
		workflow.is_active = 0
		workflow.save()
