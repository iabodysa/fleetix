# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import flt

from fleetix.fleetix.maintenance_invoice import vat_rate


class MaintenanceInvoice(Document):
	def validate(self):
		for row in self.items:
			row.amount = flt(row.qty) * flt(row.rate)
		if self.vat_rate is None:
			self.vat_rate = vat_rate(self.company)
		self.net_total = sum(flt(row.amount) for row in self.items)
		self.vat_amount = flt(self.net_total * flt(self.vat_rate) / 100, 2)
		self.grand_total = self.net_total + self.vat_amount
