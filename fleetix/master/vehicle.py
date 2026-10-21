# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, cint, getdate

from fleetix.settings.doctype.maintenance_policy.maintenance_policy import get_policy

SUMMER = "Summer (Apr-Sep)"
WINTER = "Winter (Oct-Mar)"
SUMMER_MONTHS = range(4, 10)

POLICY_DEFAULTS = (
	("oil_interval_summer_km", "Oil", SUMMER, "interval_km"),
	("oil_interval_winter_km", "Oil", WINTER, "interval_km"),
	("filter_interval_km", "Oil Filter", None, "interval_km"),
	("battery_interval_months", "Battery", None, "interval_months"),
)


class VehicleService(Document):
	def validate(self):
		super().validate()
		self.set_policy_intervals()
		self.set_next_due()

	def set_policy_intervals(self):
		region = frappe.db.get_value("City", self.city, "region") if self.city else None
		for fieldname, component, season, unit in POLICY_DEFAULTS:
			if self.get(fieldname):
				continue
			policy = get_policy(component, region, season)
			if policy:
				self.set(fieldname, policy[unit])

	def set_next_due(self):
		in_summer = getdate().month in SUMMER_MONTHS
		oil_interval = self.oil_interval_summer_km if in_summer else self.oil_interval_winter_km
		self.next_oil_due_odometer = due_odometer(self.last_oil_change_odometer, oil_interval)
		self.next_front_tires_due_odometer = due_odometer(self.last_front_tires_odometer, self.tire_interval_km)
		self.next_rear_tires_due_odometer = due_odometer(self.last_rear_tires_odometer, self.tire_interval_km)
		self.next_battery_due_date = (
			add_months(self.battery_install_date, cint(self.battery_interval_months))
			if self.battery_install_date and cint(self.battery_interval_months)
			else None
		)


def due_odometer(last_odometer, interval):
	if cint(last_odometer) and cint(interval):
		return cint(last_odometer) + cint(interval)
	return None
