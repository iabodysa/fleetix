# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe

from fleetix.fleetix.api.maintenance import FINISH_ACTIONS, visit_stage
from fleetix.fleetix.doctype.maintenance.maintenance import sync_purchase_request


def execute():
	for name in frappe.get_all(
		"Maintenance",
		filters={"docstatus": 0, "status": ("in", list(FINISH_ACTIONS)), "items_issued": ("is", "set")},
		pluck="name",
		order_by="creation asc",
	):
		job = frappe.get_doc("Maintenance", name)
		if visit_stage(job) != "parts":
			continue
		frappe.db.savepoint("issue_waiting_parts")
		try:
			sync_purchase_request(job)
			frappe.get_doc("Stock Entry", job.items_issued).submit()
		except Exception:
			frappe.db.rollback(save_point="issue_waiting_parts")
			frappe.log_error(
				f"Parts issue failed for {name}", reference_doctype="Maintenance", reference_name=name
			)
			print(f"{name} {job.items_issued} failed")
			continue
		print(f"{name} {job.items_issued} submitted")
