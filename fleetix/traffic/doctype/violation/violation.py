# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder import Order
from frappe.utils import getdate


class Violation(Document):
	def validate(self):
		if self.car and self.violation_date and not self.permit:
			self.permit = self.find_permit(getdate(self.violation_date))
		if self.permit and not self.staff:
			self.staff = frappe.db.get_value("Permit", self.permit, "staff")

	def find_permit(self, day):
		permit = frappe.qb.DocType("Permit")
		rows = (
			frappe.qb.from_(permit)
			.select(permit.name)
			.where(
				(permit.car == self.car)
				& (permit.docstatus == 1)
				& (permit.from_date <= day)
				& (permit.to_date.isnull() | (permit.to_date >= day))
			)
			.orderby(permit.from_date, order=Order.desc)
			.limit(1)
			.run()
		)
		return rows[0][0] if rows else None
