# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = []
	if filters.get("deal"):
		conditions.append("p.deal = %(deal)s")
	if filters.get("firm"):
		conditions.append("p.firm = %(firm)s")
	if filters.get("staff"):
		conditions.append("p.staff = %(staff)s")
	where = " and ".join(conditions) or "1=1"
	data = frappe.db.sql(
		f"""select p.name as permit, p.handover, p.car, p.staff, p.deal, p.firm, p.from_date,
			datediff(curdate(), p.from_date) + 1 as days_elapsed
		from `tabPermit` p
		where p.docstatus = 1 and p.status = 'Active' and {where}
		order by p.from_date""",
		filters,
		as_dict=True,
	)
	return get_columns(), data


def get_columns():
	return [
		{"fieldname": "permit", "label": _("Permit"), "fieldtype": "Link", "options": "Permit", "width": 140},
		{"fieldname": "handover", "label": _("Handover"), "fieldtype": "Link", "options": "Handover", "width": 140},
		{"fieldname": "car", "label": _("Car"), "fieldtype": "Link", "options": "Car", "width": 140},
		{"fieldname": "staff", "label": _("Employee or Delegate"), "fieldtype": "Link", "options": "Staff", "width": 140},
		{"fieldname": "deal", "label": _("Deal"), "fieldtype": "Link", "options": "Deal", "width": 140},
		{"fieldname": "firm", "label": _("Firm"), "fieldtype": "Link", "options": "Firm", "width": 140},
		{"fieldname": "from_date", "label": _("From Date"), "fieldtype": "Date", "width": 140},
		{"fieldname": "days_elapsed", "label": _("Days Elapsed"), "fieldtype": "Int", "width": 110},
	]
