# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

HOURS_PER_DAY = 24
DAYS_PER_MONTH = 30


class RentalRate(Document):
	def validate(self):
		days = DAYS_PER_MONTH if self.rate_period == "Monthly" else 1
		self.hourly_rate = flt(flt(self.rate) / days / HOURS_PER_DAY, self.precision("hourly_rate"))


def get_rental_rate(vehicle, usage_type, on_date):
	vehicle_type, company = frappe.db.get_value("Vehicle", vehicle, ["vehicle_type", "company"])
	scopes = [{"vehicle": vehicle}]
	if vehicle_type:
		scopes.append({"vehicle_type": vehicle_type, "vehicle": ("is", "not set")})
	for scope in scopes:
		rates = frappe.get_all(
			"Rental Rate",
			filters={**scope, "company": company, "usage_type": usage_type, "valid_from": ("<=", on_date)},
			or_filters=[["valid_to", "is", "not set"], ["valid_to", ">=", on_date]],
			fields=["hourly_rate", "item"],
			order_by="valid_from desc",
			limit=1,
		)
		if rates:
			return rates[0]
	return None
