# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import flt


class Requisition(Document):
	def validate(self):
		for line in self.lines:
			line.amount = flt(line.qty) * flt(line.rate)
		self.total = sum(flt(line.amount) for line in self.lines)
