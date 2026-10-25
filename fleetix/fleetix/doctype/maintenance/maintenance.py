# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import erpnext
import frappe
from erpnext.stock.stock_ledger import get_valuation_rate
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, now_datetime, today

from fleetix.fleetix.vehicle import parse_fieldnames, refresh_schedule, set_next_due

COMPONENT_FIELDS = {
	"Oil": ("last_oil_change_date", "last_oil_change_odometer"),
	"Oil Filter": ("last_filter_change_date", "last_filter_change_odometer"),
	"Front Tires": ("last_front_tires_date", "last_front_tires_odometer"),
	"Rear Tires": ("last_rear_tires_date", "last_rear_tires_odometer"),
	"Battery": ("battery_install_date", None),
}
NEXT_DUE_FIELDS = {
	"Oil": "next_oil_due_odometer",
	"Oil Filter": "next_filter_due_odometer",
	"Front Tires": "next_front_tires_due_odometer",
	"Rear Tires": "next_rear_tires_due_odometer",
}
ISSUE_STATES = ("Service", "Final Check")
DEFAULT_PHOTO_SLOTS = ("Front Side", "Rear Side", "Right Side", "Left Side", "Odometer Photo")
DEFAULT_MAX_QTY = {"Oil Filter": 1, "Battery": 1, "Front Tires": 2, "Rear Tires": 2}


class Maintenance(Document):
	def validate(self):
		if self.status == "Driver Arrived" and not self.visit_datetime:
			self.visit_datetime = now_datetime()
		if self.status == "Approved" and not self.approved_by:
			self.approved_by = frappe.session.user
		if self.has_value_changed("manager_signature"):
			self.manager_signed_by = frappe.session.user if self.manager_signature else None
			self.manager_signed_on = now_datetime() if self.manager_signature else None
		if self.status in ISSUE_STATES and not self.items_issued:
			self.items_issued = issue_items(self)
		if cint(self.odometer) > cint(frappe.db.get_value("Vehicle", self.vehicle, "last_odometer")):
			frappe.db.set_value(
				"Vehicle", self.vehicle, "last_odometer", cint(self.odometer), update_modified=False
			)

	def on_submit(self):
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		replaced_on = getdate(self.visit_datetime)
		vehicle.last_odometer = max(cint(vehicle.last_odometer), cint(self.odometer))
		for row in self.components_replaced:
			date_field, odometer_field = COMPONENT_FIELDS[row.component]
			vehicle.set(date_field, replaced_on)
			if odometer_field:
				vehicle.set(odometer_field, self.odometer)
		set_next_due(vehicle)
		vehicle.flags.ignore_mandatory = True
		vehicle.save()
		for row in self.components_replaced:
			next_due_odometer, next_due_date = next_due(vehicle, row.component)
			frappe.get_doc(
				{
					"doctype": "Component Replacement Log",
					"component": row.component,
					"replacement_date": replaced_on,
					"odometer_at_replacement": self.odometer,
					"item": row.item,
					"maintenance": self.name,
					"next_due_odometer": next_due_odometer,
					"next_due_date": next_due_date,
				}
			).insert(ignore_permissions=True)


def manager_signable(maintenance):
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("write")
	if not visit.has_permlevel_access_to("manager_signature", permission_type="write"):
		raise frappe.PermissionError
	if visit.docstatus != 0:
		frappe.throw(_("This visit is not waiting for a signature"))
	return visit


def issue_items(maintenance):
	rows = [row for row in maintenance.components_replaced if row.item]
	if not rows:
		return None
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	entry = frappe.get_doc(
		{
			"doctype": "Stock Entry",
			"stock_entry_type": "Material Issue",
			"company": maintenance.company,
			"maintenance": maintenance.name,
			"from_warehouse": warehouse,
			"items": [{"item_code": row.item, "qty": row.qty, "s_warehouse": warehouse} for row in rows],
		}
	).insert()
	return entry.name


def component_max_qty(component):
	rules = frappe.get_cached_doc("Fleetix Settings").component_items
	configured = [flt(row.max_qty) for row in rules if row.component == component and flt(row.max_qty)]
	return max(configured) if configured else DEFAULT_MAX_QTY.get(component, 0)


def photo_slots(visit):
	configured = parse_fieldnames(frappe.get_cached_doc("Fleetix Settings").photo_slots)
	slots = [{"slot": name, "label": _(name)} for name in configured or DEFAULT_PHOTO_SLOTS]
	for no, mark in enumerate(frappe.parse_json(visit.damage_marks) or [], start=1):
		label = " - ".join(_(part) for part in (mark["area"], mark.get("kind")) if part)
		slots.append({"slot": f"damage-{no}", "label": f"{no}. {label}", "damage": no})
	return slots


def unpriced_items(item_codes, company):
	if not cint(erpnext.is_perpetual_inventory_enabled(company)):
		return []
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	currency = erpnext.get_company_currency(company)
	return [
		item_code
		for item_code in dict.fromkeys(item_codes)
		if get_valuation_rate(
			item_code,
			warehouse,
			"Stock Entry",
			None,
			currency=currency,
			company=company,
			raise_error_if_no_rate=False,
		)
		is None
	]


def next_due(vehicle, component):
	if component == "Battery":
		return None, vehicle.next_battery_due_date
	return vehicle.get(NEXT_DUE_FIELDS[component]), None


def due_components(vehicle):
	due = []
	for component in COMPONENT_FIELDS:
		due_km, due_date = next_due(vehicle, component)
		if cint(due_km) and cint(vehicle.last_odometer) >= cint(due_km):
			due.append(component)
		elif due_date and getdate(due_date) <= getdate(today()):
			due.append(component)
	return due


def create_due_alerts():
	open_vehicles = set(frappe.get_all("Maintenance", filters={"docstatus": 0}, pluck="vehicle"))
	assigned = set(
		frappe.get_all(
			"Vehicle",
			filters={"active": 1, "current_driver": ("is", "set"), "current_project": ("is", "set")},
			pluck="name",
		)
	)
	with_odometer = frappe.get_all("Vehicle", filters={"last_odometer": (">", 0)}, pluck="name")
	for name in sorted(assigned.union(with_odometer)):
		vehicle = frappe.get_doc("Vehicle", name)
		if refresh_schedule(vehicle):
			vehicle.flags.ignore_mandatory = True
			vehicle.save()
		if name not in assigned or name in open_vehicles:
			continue
		due = due_components(vehicle)
		if not due:
			continue
		frappe.get_doc(
			{
				"doctype": "Maintenance",
				"maintenance_type": "Periodic",
				"vehicle": name,
				"description": ", ".join(due),
			}
		).insert()
