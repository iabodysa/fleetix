# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from fleetix.fleetix.doctype.project_claim.project_claim import make_project_claim
from fleetix.fleetix.doctype.vehicle_assignment.vehicle_assignment import customer_at


class Damage(Document):
	def validate(self):
		if not self.customer:
			self.customer = customer_at(self.creation or now_datetime(), self.vehicle, self.driver)
		if self.status == "Cost Estimated" and not self.responsibility_set_by:
			self.responsibility_set_by = frappe.session.user

	def on_update(self):
		if self.status == "Claimed from Project" and not self.project_claim:
			self.project_claim = make_project_claim(self)
