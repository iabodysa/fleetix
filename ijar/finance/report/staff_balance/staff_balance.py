# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = []
	if filters.get("staff"):
		conditions.append("s.name = %(staff)s")
	if filters.get("kind"):
		conditions.append("s.kind = %(kind)s")
	where = " and ".join(conditions) or "1=1"
	data = frappe.db.sql(
		f"""select s.name as staff, s.full_name, s.kind,
			ifnull(a.amount, 0) as advances, ifnull(d.amount, 0) as deductions,
			ifnull(a.amount, 0) - ifnull(d.amount, 0) as balance
		from `tabStaff` s
		left join (select staff, sum(amount) as amount from `tabAdvance` where docstatus = 1 group by staff) a on a.staff = s.name
		left join (select staff, sum(amount) as amount from `tabDeduction` where docstatus = 1 group by staff) d on d.staff = s.name
		where (a.amount is not null or d.amount is not null) and {where}
		order by balance desc""",
		filters,
		as_dict=True,
	)
	return get_columns(), data


def get_columns():
	return [
		{"fieldname": "staff", "label": _("Employee or Delegate"), "fieldtype": "Link", "options": "Staff", "width": 140},
		{"fieldname": "full_name", "label": _("Full Name"), "fieldtype": "Data", "width": 180},
		{"fieldname": "kind", "label": _("Kind"), "fieldtype": "Data", "width": 100},
		{"fieldname": "advances", "label": _("Advances"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "deductions", "label": _("Deductions"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "balance", "label": _("Balance"), "fieldtype": "Currency", "width": 140},
	]
