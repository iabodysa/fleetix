# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate

from fleetix.finance.rent import permit_lines


@frappe.whitelist()
def get_permits(deal, from_date, to_date):
	return permit_lines(getdate(from_date), getdate(to_date), {"name": deal})
