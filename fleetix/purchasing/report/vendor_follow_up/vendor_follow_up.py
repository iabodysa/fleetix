# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = []
	if filters.get("vendor"):
		conditions.append("r.vendor = %(vendor)s")
	if filters.get("status"):
		conditions.append("r.status = %(status)s")
	if filters.get("from_date"):
		conditions.append("r.req_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("r.req_date <= %(to_date)s")
	where = " and ".join(conditions) or "1=1"
	data = frappe.db.sql(
		f"""select r.vendor, v.status as vendor_status, r.status, count(*) as requisitions, sum(r.total) as total
		from `tabRequisition` r
		left join `tabVendor` v on v.name = r.vendor
		where r.docstatus < 2 and {where}
		group by r.vendor, v.status, r.status
		order by r.vendor""",
		filters,
		as_dict=True,
	)
	return get_columns(), data


def get_columns():
	return [
		{"fieldname": "vendor", "label": _("Vendor"), "fieldtype": "Link", "options": "Vendor", "width": 140},
		{"fieldname": "vendor_status", "label": _("Vendor Status"), "fieldtype": "Data", "width": 120},
		{"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 140},
		{"fieldname": "requisitions", "label": _("Count"), "fieldtype": "Int", "width": 90},
		{"fieldname": "total", "label": _("Total"), "fieldtype": "Currency", "width": 140},
	]
