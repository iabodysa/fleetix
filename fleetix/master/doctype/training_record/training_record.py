# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

DRIVER_TRAINING_STATUS = {"In Training": "In Training", "Eligible for Assignment": "Trained"}


class TrainingRecord(Document):
	def validate(self):
		if self.result == "Passed":
			self.status = "Eligible for Assignment"
		elif self.temporary_assignment:
			self.status = "In Training"
		else:
			self.status = "Registered"

	def on_update(self):
		if not self.has_value_changed("status") or self.status not in DRIVER_TRAINING_STATUS:
			return
		driver = frappe.get_doc("Driver", self.driver)
		driver.training_status = DRIVER_TRAINING_STATUS[self.status]
		driver.save()
		if self.status == "Eligible for Assignment" and self.temporary_assignment:
			frappe.get_doc("Vehicle Assignment", self.temporary_assignment).convert_to_permanent()
