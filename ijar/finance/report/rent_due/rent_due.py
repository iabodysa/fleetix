# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate

from ijar.finance.rent import permit_lines


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not (filters.from_date and filters.to_date):
		return get_columns(), []
	start, end = getdate(filters.from_date), getdate(filters.to_date)
	deal_filters = {key: filters[key] for key in ("client", "deal_type") if filters.get(key)}
	if filters.deal:
		deal_filters["name"] = filters.deal
	billed = dict(
		frappe.db.sql(
			"""select l.permit, sum(l.days)
			from `tabRent Line` l join `tabRent` r on r.name = l.parent and l.parenttype = 'Rent'
			where r.docstatus = 1 and r.from_date <= %(end)s and r.to_date >= %(start)s
			group by l.permit""",
			{"start": start, "end": end},
		)
	)
	data = []
	for line in permit_lines(start, end, deal_filters):
		line.billed_days = flt(billed.get(line.permit))
		line.due_days = max(line.days - line.billed_days, 0)
		line.amount = line.due_days * flt(line.rate)
		data.append(line)
	return get_columns(), data


def get_columns():
	return [
		{"fieldname": "client", "label": _("Client"), "fieldtype": "Link", "options": "Client", "width": 140},
		{"fieldname": "deal", "label": _("Deal"), "fieldtype": "Link", "options": "Deal", "width": 140},
		{"fieldname": "deal_type", "label": _("Deal Type"), "fieldtype": "Link", "options": "Deal Type", "width": 140},
		{"fieldname": "permit", "label": _("Permit"), "fieldtype": "Link", "options": "Permit", "width": 140},
		{"fieldname": "car", "label": _("Car"), "fieldtype": "Link", "options": "Car", "width": 140},
		{"fieldname": "staff", "label": _("Employee or Delegate"), "fieldtype": "Link", "options": "Staff", "width": 140},
		{"fieldname": "days", "label": _("Days"), "fieldtype": "Int", "width": 80},
		{"fieldname": "billed_days", "label": _("Billed Days"), "fieldtype": "Int", "width": 100},
		{"fieldname": "due_days", "label": _("Due Days"), "fieldtype": "Int", "width": 100},
		{"fieldname": "rate", "label": _("Rate"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 140},
	]
