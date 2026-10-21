# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe

from fleetix.fleetix.doctype.project_claim.project_claim import source_values


@frappe.whitelist()
def get_source_values(claim_type, source_reference):
	source = frappe.get_doc(claim_type, source_reference)
	source.check_permission("read")
	return source_values(source)
