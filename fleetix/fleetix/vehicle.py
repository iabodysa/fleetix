# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from erpnext.setup.doctype.vehicle.vehicle import Vehicle
from frappe.utils import add_months, cint, date_diff, getdate, today

from fleetix.fleetix.doctype.maintenance_policy.maintenance_policy import get_policy

SUMMER = "Summer (Apr-Sep)"
WINTER = "Winter (Oct-Mar)"
SUMMER_MONTHS = range(4, 10)

POLICY_DEFAULTS = (
	("oil_interval_summer_km", "Oil", SUMMER, "interval_km"),
	("oil_interval_winter_km", "Oil", WINTER, "interval_km"),
	("filter_interval_km", "Oil Filter", None, "interval_km"),
	("tire_interval_km", "Front Tires", None, "interval_km"),
	("battery_interval_months", "Battery", None, "interval_months"),
)
SCHEDULE_FIELDS = (
	*(row[0] for row in POLICY_DEFAULTS),
	"next_oil_due_odometer",
	"next_filter_due_odometer",
	"next_front_tires_due_odometer",
	"next_rear_tires_due_odometer",
	"next_battery_due_date",
)
JUMP_FACTOR = 3
MIN_JUMP_KM = 1000
JUMP_READINGS = 10


class VehicleService(Vehicle):
	def validate(self):
		super().validate()
		self.set_policy_intervals()
		set_next_due(self)
		settings = frappe.get_cached_doc("Fleetix Settings")
		self.update(missing_data(self, parse_fieldnames(settings.vehicle_required_fields)))

	def set_policy_intervals(self):
		region, tire_interval = (
			frappe.db.get_value("City", self.city, ["region", "default_tire_interval_km"])
			if self.city
			else None
		) or (None, None)
		intervals = policy_intervals(region)
		if cint(tire_interval):
			intervals["tire_interval_km"] = cint(tire_interval)
		self.update(intervals)


def current_season():
	return SUMMER if getdate().month in SUMMER_MONTHS else WINTER


def policy_intervals(region):
	intervals = {}
	for fieldname, component, season, unit in POLICY_DEFAULTS:
		policy = get_policy(component, region, season or current_season())
		if policy:
			intervals[fieldname] = policy[unit]
	return intervals


def set_next_due(vehicle):
	in_summer = getdate().month in SUMMER_MONTHS
	oil_interval = vehicle.oil_interval_summer_km if in_summer else vehicle.oil_interval_winter_km
	for recorded, interval, fieldname in (
		(vehicle.last_oil_change_odometer, oil_interval, "next_oil_due_odometer"),
		(vehicle.last_filter_change_odometer, vehicle.filter_interval_km, "next_filter_due_odometer"),
		(vehicle.last_front_tires_odometer, vehicle.tire_interval_km, "next_front_tires_due_odometer"),
		(vehicle.last_rear_tires_odometer, vehicle.tire_interval_km, "next_rear_tires_due_odometer"),
	):
		if cint(recorded):
			vehicle.set(fieldname, due_odometer(recorded, interval))
		elif not cint(vehicle.get(fieldname)):
			vehicle.set(fieldname, due_odometer(vehicle.last_odometer, interval))
	months = cint(vehicle.battery_interval_months)
	if vehicle.battery_install_date:
		vehicle.next_battery_due_date = add_months(vehicle.battery_install_date, months) if months else None
	elif not vehicle.next_battery_due_date and months:
		vehicle.next_battery_due_date = add_months(today(), months)


def refresh_schedule(vehicle):
	before = [str(vehicle.get(fieldname) or "") for fieldname in SCHEDULE_FIELDS]
	vehicle.set_policy_intervals()
	set_next_due(vehicle)
	return [str(vehicle.get(fieldname) or "") for fieldname in SCHEDULE_FIELDS] != before


def odometer_limit(vehicle):
	readings = frappe.get_all(
		"Maintenance",
		filters={"vehicle": vehicle, "docstatus": 1, "odometer": (">", 0), "visit_datetime": ("is", "set")},
		fields=["odometer", "visit_datetime"],
		order_by="visit_datetime desc",
		limit=JUMP_READINGS,
	)
	if len(readings) < 2:
		return None
	newest, oldest = readings[0], readings[-1]
	days = max(date_diff(newest.visit_datetime, oldest.visit_datetime), 1)
	daily = max(cint(newest.odometer) - cint(oldest.odometer), 0) / days
	elapsed = max(date_diff(today(), newest.visit_datetime), 1)
	base = max(cint(newest.odometer), cint(frappe.db.get_value("Vehicle", vehicle, "last_odometer")))
	return base + max(cint(daily * elapsed * JUMP_FACTOR), MIN_JUMP_KM)


def due_odometer(last_odometer, interval):
	if cint(last_odometer) and cint(interval):
		return cint(last_odometer) + cint(interval)
	return None


def parse_fieldnames(text):
	return [line.strip() for line in (text or "").splitlines() if line.strip()]


def missing_data(vehicle, fieldnames):
	meta = frappe.get_meta("Vehicle")
	missing = [meta.get_label(f) for f in fieldnames if meta.has_field(f) and not vehicle.get(f)]
	return {"data_incomplete": 1 if missing else 0, "missing_fields": ", ".join(missing)}
