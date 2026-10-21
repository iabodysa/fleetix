# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from frappe import _


def get_data():
	return {
		"fieldname": "assignment",
		"non_standard_fieldnames": {"Training Record": "temporary_assignment"},
		"transactions": [{"label": _("Fleetix"), "items": ["Project Rental Charge", "Training Record"]}],
	}
