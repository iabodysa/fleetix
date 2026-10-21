# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from fleetix.insurance.doctype.project_claim.project_claim import make_project_claim
from fleetix.transaction.doctype.vehicle_assignment.vehicle_assignment import holder_at


class Accident(Document):
	def validate(self):
		holder = holder_at(self.vehicle, self.accident_datetime)
		if holder:
			self.driver, self.project = holder.driver, holder.project
		if self.status == "Responsibility Set" and not self.responsibility_set_by:
			self.responsibility_set_by = frappe.session.user

	def on_update(self):
		if self.status == "Claimed" and not self.project_claim:
			self.project_claim = make_project_claim(self)
