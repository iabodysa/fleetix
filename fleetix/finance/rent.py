# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate


def permit_lines(start, end, deal_filters):
	deals = {d.name: d for d in frappe.get_all("Deal", filters=deal_filters, fields=["name", "client", "deal_type"])}
	if not deals:
		return []
	rates = dict(frappe.get_all("Deal Type", fields=["name", "rate"], as_list=True))
	permits = frappe.get_list(
		"Permit",
		filters={"deal": ["in", list(deals)], "docstatus": 1, "from_date": ["<=", end]},
		fields=["name", "car", "staff", "deal", "from_date", "to_date"],
		order_by="from_date",
	)
	lines = []
	for permit in permits:
		first = max(getdate(permit.from_date), start)
		last = min(getdate(permit.to_date) if permit.to_date else end, end)
		if last < first:
			continue
		deal = deals[permit.deal]
		lines.append(
			frappe._dict(
				permit=permit.name,
				car=permit.car,
				staff=permit.staff,
				deal=permit.deal,
				client=deal.client,
				deal_type=deal.deal_type,
				from_date=first,
				to_date=last,
				days=(last - first).days + 1,
				rate=rates.get(deal.deal_type) or 0,
			)
		)
	return lines
