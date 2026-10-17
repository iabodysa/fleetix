# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = []
	if filters.get("from_date"):
		conditions.append("date(v.violation_date) >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("date(v.violation_date) <= %(to_date)s")
	if filters.get("deal"):
		conditions.append("p.deal = %(deal)s")
	if filters.get("staff"):
		conditions.append("v.staff = %(staff)s")
	where = " and ".join(conditions) or "1=1"
	data = frappe.db.sql(
		f"""select v.staff, p.deal, count(*) as violations, sum(v.amount) as amount,
			sum(case when v.status in ('Charged', 'Paid') then v.amount else 0 end) as charged_amount,
			sum(case when v.status in ('Open', 'Disputed') then v.amount else 0 end) as open_amount
		from `tabViolation` v
		left join `tabPermit` p on p.name = v.permit
		where {where}
		group by v.staff, p.deal
		order by amount desc""",
		filters,
		as_dict=True,
	)
	return get_columns(), data


def get_columns():
	return [
		{"fieldname": "staff", "label": _("Employee or Delegate"), "fieldtype": "Link", "options": "Staff", "width": 140},
		{"fieldname": "deal", "label": _("Deal"), "fieldtype": "Link", "options": "Deal", "width": 140},
		{"fieldname": "violations", "label": _("Count"), "fieldtype": "Int", "width": 90},
		{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "charged_amount", "label": _("Charged Amount"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "open_amount", "label": _("Open Amount"), "fieldtype": "Currency", "width": 140},
	]
