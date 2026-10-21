# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_datetime, getdate, time_diff_in_hours
from frappe.utils.print_format import read_multi_pdf
from pypdf import PdfWriter

from fleetix.fleetix.doctype.rental_rate.rental_rate import get_rental_rate
from fleetix.fleetix.doctype.vehicle_assignment.vehicle_assignment import held_until


class ProjectRentalCharge(Document):
	def validate(self):
		self.limit_to_holding()
		self.hours = flt(time_diff_in_hours(self.period_to, self.period_from), self.precision("hours"))
		if self.hours <= 0:
			frappe.throw(
				_("Assignment {0} did not hold the vehicle between {1} and {2}").format(
					self.assignment, self.period_from, self.period_to
				)
			)
		rate = get_rental_rate(self.vehicle, self.usage_type, getdate(self.period_from))
		if rate:
			self.hourly_rate = rate.hourly_rate
			self.item = self.item or rate.item
		self.amount = flt(self.hours * flt(self.hourly_rate), self.precision("amount"))

	def limit_to_holding(self):
		start = get_datetime(frappe.db.get_value("Vehicle Assignment", self.assignment, "handover_date"))
		end = held_until(self.vehicle, self.driver, start)
		self.period_from = max(get_datetime(self.period_from), start)
		if end:
			self.period_to = min(get_datetime(self.period_to), get_datetime(end))

	def before_submit(self):
		self.status = "Posted"


def attach_statement(invoice, charges):
	output = PdfWriter()
	for charge in charges:
		output = frappe.get_print(
			"Project Rental Charge", charge, "Rental Charge Statement", as_pdf=True, output=output
		)
	frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"{invoice} - Rental Charge Statement.pdf",
			"attached_to_doctype": "Sales Invoice",
			"attached_to_name": invoice,
			"is_private": 1,
			"content": read_multi_pdf(output),
		}
	).insert()
