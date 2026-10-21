# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from frappe import _


def get_data():
	return {
		"fieldname": "insurance_policy",
		"transactions": [{"label": _("Fleetix"), "items": ["Insurance Claim"]}],
	}
