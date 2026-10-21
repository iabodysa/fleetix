# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from erpnext.setup.doctype.vehicle.vehicle import Vehicle
from frappe.utils import add_months, cint, getdate

from fleetix.fleetix.doctype.maintenance_policy.maintenance_policy import get_policy

SUMMER = "Summer (Apr-Sep)"
WINTER = "Winter (Oct-Mar)"
SUMMER_MONTHS = range(4, 10)

POLICY_DEFAULTS = (
	("oil_interval_summer_km", "Oil", SUMMER, "interval_km"),
	("oil_interval_winter_km", "Oil", WINTER, "interval_km"),
	("filter_interval_km", "Oil Filter", None, "interval_km"),
	("battery_interval_months", "Battery", None, "interval_months"),
)


class VehicleService(Vehicle):
	def validate(self):
		super().validate()
		self.set_policy_intervals()
		set_next_due(self)

	def set_policy_intervals(self):
		region = frappe.db.get_value("City", self.city, "region") if self.city else None
		for fieldname, value in policy_intervals(region).items():
			if not self.get(fieldname):
				self.set(fieldname, value)


def policy_intervals(region):
	intervals = {}
	for fieldname, component, season, unit in POLICY_DEFAULTS:
		policy = get_policy(component, region, season)
		if policy:
			intervals[fieldname] = policy[unit]
	return intervals


def set_next_due(vehicle):
	in_summer = getdate().month in SUMMER_MONTHS
	oil_interval = vehicle.oil_interval_summer_km if in_summer else vehicle.oil_interval_winter_km
	vehicle.next_oil_due_odometer = due_odometer(vehicle.last_oil_change_odometer, oil_interval)
	vehicle.next_front_tires_due_odometer = due_odometer(
		vehicle.last_front_tires_odometer, vehicle.tire_interval_km
	)
	vehicle.next_rear_tires_due_odometer = due_odometer(
		vehicle.last_rear_tires_odometer, vehicle.tire_interval_km
	)
	vehicle.next_battery_due_date = (
		add_months(vehicle.battery_install_date, cint(vehicle.battery_interval_months))
		if vehicle.battery_install_date and cint(vehicle.battery_interval_months)
		else None
	)


def due_odometer(last_odometer, interval):
	if cint(last_odometer) and cint(interval):
		return cint(last_odometer) + cint(interval)
	return None
