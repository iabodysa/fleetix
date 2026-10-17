# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = []
	if filters.get("from_date"):
		conditions.append("date(a.accident_date) >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("date(a.accident_date) <= %(to_date)s")
	if filters.get("deal"):
		conditions.append("a.deal = %(deal)s")
	if filters.get("firm"):
		conditions.append("a.firm = %(firm)s")
	if filters.get("status"):
		conditions.append("a.status = %(status)s")
	where = " and ".join(conditions) or "1=1"
	data = frappe.db.sql(
		f"""select a.name as accident, a.accident_date, a.car, a.plate, a.deal, a.firm, a.staff, a.city, a.status,
			c.name as claim, c.status as claim_status, c.amount as claim_amount, c.approved,
			(select count(*) from `tabBond` b where b.accident = a.name and b.docstatus < 2) as bonds,
			(select ifnull(sum(v.amount), 0) from `tabAdvance` v where v.accident = a.name and v.docstatus = 1) as advances
		from `tabAccident` a
		left join `tabClaim` c on c.accident = a.name and c.docstatus < 2
		where a.docstatus < 2 and {where}
		order by a.accident_date desc""",
		filters,
		as_dict=True,
	)
	return get_columns(), data


def get_columns():
	return [
		{"fieldname": "accident", "label": _("Accident"), "fieldtype": "Link", "options": "Accident", "width": 140},
		{"fieldname": "accident_date", "label": _("Accident Date"), "fieldtype": "Datetime", "width": 140},
		{"fieldname": "car", "label": _("Car"), "fieldtype": "Link", "options": "Car", "width": 140},
		{"fieldname": "plate", "label": _("Plate"), "fieldtype": "Link", "options": "Plate", "width": 140},
		{"fieldname": "deal", "label": _("Deal"), "fieldtype": "Link", "options": "Deal", "width": 140},
		{"fieldname": "firm", "label": _("Firm"), "fieldtype": "Link", "options": "Firm", "width": 140},
		{"fieldname": "staff", "label": _("Employee or Delegate"), "fieldtype": "Link", "options": "Staff", "width": 140},
		{"fieldname": "city", "label": _("City"), "fieldtype": "Data", "width": 140},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 140},
		{"fieldname": "claim", "label": _("Claim"), "fieldtype": "Link", "options": "Claim", "width": 140},
		{"fieldname": "claim_status", "label": _("Claim Status"), "fieldtype": "Data", "width": 140},
		{"fieldname": "claim_amount", "label": _("Claim Amount"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "approved", "label": _("Approved Amount"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "bonds", "label": _("Bonds"), "fieldtype": "Int", "width": 90},
		{"fieldname": "advances", "label": _("Advances"), "fieldtype": "Currency", "width": 140},
	]
