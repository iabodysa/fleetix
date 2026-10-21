# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import flt

HOURS_PER_DAY = 24
DAYS_PER_MONTH = 30


class RentalRate(Document):
	def validate(self):
		days = DAYS_PER_MONTH if self.rate_period == "Monthly" else 1
		self.hourly_rate = flt(flt(self.rate) / days / HOURS_PER_DAY, self.precision("hourly_rate"))
