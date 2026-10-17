# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = []
	if filters.get("status"):
		conditions.append("c.status = %(status)s")
	if filters.get("firm"):
		conditions.append("c.firm = %(firm)s")
	if filters.get("deal"):
		conditions.append("c.deal = %(deal)s")
	where = " and ".join(conditions) or "1=1"
	data = frappe.db.sql(
		f"""select c.name as car, c.plate, c.firm, c.deal, c.staff, c.status,
			i.name as istimara, i.expiry_date as istimara_expiry
		from `tabCar` c
		left join `tabIstimara` i on i.name = (
			select x.name from `tabIstimara` x
			where x.car = c.name and x.status = 'Valid'
			order by x.expiry_date desc limit 1
		)
		where {where}
		order by c.name""",
		filters,
		as_dict=True,
	)
	return get_columns(), data


def get_columns():
	return [
		{"fieldname": "car", "label": _("Car"), "fieldtype": "Link", "options": "Car", "width": 140},
		{"fieldname": "plate", "label": _("Plate"), "fieldtype": "Link", "options": "Plate", "width": 140},
		{"fieldname": "firm", "label": _("Firm"), "fieldtype": "Link", "options": "Firm", "width": 140},
		{"fieldname": "deal", "label": _("Deal"), "fieldtype": "Link", "options": "Deal", "width": 140},
		{"fieldname": "staff", "label": _("Employee or Delegate"), "fieldtype": "Link", "options": "Staff", "width": 140},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 140},
		{"fieldname": "istimara", "label": _("Istimara"), "fieldtype": "Link", "options": "Istimara", "width": 140},
		{"fieldname": "istimara_expiry", "label": _("Istimara Expiry"), "fieldtype": "Date", "width": 140},
	]
