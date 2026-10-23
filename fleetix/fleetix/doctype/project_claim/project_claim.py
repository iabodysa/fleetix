# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

from fleetix.fleetix.doctype.vehicle_assignment.vehicle_assignment import customer_at


class ProjectClaim(Document):
	def validate(self):
		for fieldname, value in source_values(frappe.get_doc(self.claim_type, self.source_reference)).items():
			if not self.get(fieldname):
				self.set(fieldname, value)
		if not self.customer:
			self.customer = customer_at(self.claim_date, driver=self.driver)

	def after_insert(self):
		if frappe.get_meta(self.claim_type).has_field("project_claim"):
			frappe.db.set_value(
				self.claim_type, self.source_reference, "project_claim", self.name, update_modified=False
			)


def claim_amount(source):
	if source.doctype == "Accident":
		return flt(source.estimated_cost) * flt(source.responsibility_percentage) / 100
	if source.doctype == "Damage":
		return flt(source.estimated_cost)
	return flt(source.cost)


def source_values(source):
	return {
		"project": source.project,
		"customer": source.customer,
		"driver": source.get("charged_to_driver") or source.driver,
		"amount": claim_amount(source),
	}


def make_project_claim(source):
	if not claim_amount(source):
		return None
	claim = frappe.get_doc(
		{"doctype": "Project Claim", "claim_type": source.doctype, "source_reference": source.name}
	).insert()
	return claim.name
