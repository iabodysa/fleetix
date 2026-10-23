# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, date_diff, get_datetime, getdate, now_datetime, today

from fleetix.fleetix.doctype.maintenance.maintenance import due_components
from fleetix.fleetix.doctype.vehicle_assignment.vehicle_assignment import LIVE

BOARD_ROLES = (
	"Rental Manager",
	"Movement Supervisor",
	"Maintenance Supervisor",
	"Project Supervisor",
	"Accountant",
	"System Manager",
)
STATES = ("red", "black", "gray", "green")
DELIVERY_STEPS = ("Pending Inspection", "Pending Documentation", "Pending Assignment")
WAITING_STEPS = ("New", "Pending Vehicle Selection")
WORKSHOP_STEPS = ("Driver Arrived", "Full Inspection", "Approved", "Service", "Final Check")
TRAINING = "Temporary (Training)"
HELD = ("In Maintenance", "Suspended")
EXPIRY_WINDOW_DAYS = 14
VEHICLE_FIELDS = [
	"name",
	"license_plate",
	"make",
	"model",
	"city",
	"status",
	"vehicle_type",
	"current_driver",
	"current_project",
	"acquisition_date",
	"creation",
	"last_odometer",
	"registration_expiry",
	"periodic_inspection_expiry",
	"next_oil_due_odometer",
	"next_front_tires_due_odometer",
	"next_rear_tires_due_odometer",
	"next_battery_due_date",
	"last_filter_change_odometer",
	"filter_interval_km",
]


def classify(project=None, city=None):
	filters = {"active": 1, **({"city": city} if city else {})}
	vehicles = frappe.get_list("Vehicle", filters=filters, fields=VEHICLE_FIELDS, limit_page_length=0)
	if not vehicles:
		return []
	names = [v.name for v in vehicles]
	now = now_datetime()
	day_end = get_datetime(f"{today()} 23:59:59")

	live = {}
	for row in frappe.get_list(
		"Vehicle Assignment",
		filters={"docstatus": 1, "status": ("in", LIVE), "vehicle": ("in", names)},
		fields=["name", "vehicle", "driver", "project", "customer", "assignment_type", "from_datetime", "to_datetime"],
		order_by="from_datetime asc",
	):
		live[row.vehicle] = row

	deliveries = {}
	for row in frappe.get_list(
		"Vehicle Request",
		filters={
			"selected_vehicle": ("in", names),
			"workflow_state": ("in", DELIVERY_STEPS),
			"required_date": ("<=", today()),
		},
		fields=["name", "selected_vehicle", "project", "required_date", "workflow_state"],
		order_by="required_date asc",
	):
		deliveries.setdefault(row.selected_vehicle, row)

	in_workshop, due_alerts = set(), {}
	for row in frappe.get_list(
		"Maintenance",
		filters={"docstatus": 0, "vehicle": ("in", names)},
		fields=["name", "vehicle", "status", "maintenance_type", "description", "creation"],
	):
		if row.status in WORKSHOP_STEPS:
			in_workshop.add(row.vehicle)
		elif row.status == "Due Alert" and row.maintenance_type == "Periodic":
			due_alerts[row.vehicle] = row

	notes = {}
	for doctype in ("Accident", "Damage"):
		for row in frappe.get_list(
			doctype,
			filters={"vehicle": ("in", names), "status": ("!=", "Closed")},
			fields=["name", "vehicle"],
		):
			notes.setdefault(row.vehicle, []).append({"doctype": doctype, "name": row.name})

	last_return = dict(
		frappe.get_list(
			"Vehicle Handover",
			filters={"docstatus": 1, "handover_type": "Return", "vehicle": ("in", names)},
			fields=["vehicle", "max(handover_datetime) as at"],
			group_by="vehicle",
			as_list=True,
		)
	)

	rows = []
	for vehicle in vehicles:
		assignment = live.get(vehicle.name)
		row = frappe._dict(
			vehicle=vehicle.name,
			plate=vehicle.license_plate or vehicle.name,
			model=" ".join(filter(None, [vehicle.make, vehicle.model])),
			city=vehicle.city,
			status=vehicle.status,
			driver=assignment.driver if assignment else vehicle.current_driver,
			project=assignment.project if assignment else vehicle.current_project,
			customer=assignment.customer if assignment else None,
			assignment=assignment.name if assignment else None,
			chips=[],
			notes=notes.get(vehicle.name, []),
		)
		delivery = deliveries.get(vehicle.name)
		due = due_components(vehicle)
		if assignment and assignment.to_datetime and get_datetime(assignment.to_datetime) <= day_end:
			late = (now - get_datetime(assignment.to_datetime)).total_seconds() / 3600
			row.update(
				state="red", reason="return_due", due=assignment.to_datetime, late_hours=round(late, 1)
			)
		elif delivery:
			late = (now - get_datetime(delivery.required_date)).total_seconds() / 3600
			row.update(
				state="red",
				reason="deliver_due",
				due=delivery.required_date,
				late_hours=round(late, 1),
				ref_doctype="Vehicle Request",
				ref_name=delivery.name,
				step=delivery.workflow_state,
				project=delivery.project,
			)
		elif assignment and row.notes:
			row.update(state="red", reason="open_note", late_hours=0)
		elif (
			not assignment
			and vehicle.status not in HELD
			and vehicle.name not in in_workshop
			and not row.notes
		):
			since = last_return.get(vehicle.name) or vehicle.acquisition_date or vehicle.creation
			row.update(state="black", reason="idle", idle_days=date_diff(today(), since))
		elif vehicle.name not in in_workshop and (vehicle.name in due_alerts or due):
			alert = due_alerts.get(vehicle.name)
			row.update(
				state="gray",
				reason=alert.description if alert else ", ".join(due),
				ref_doctype="Maintenance" if alert else None,
				ref_name=alert.name if alert else None,
				since_days=date_diff(today(), alert.creation) if alert else 0,
			)
		else:
			row.update(state="green", reason="")
		set_chips(row, vehicle, assignment, in_workshop)
		rows.append(row)

	if project:
		rows = [row for row in rows if row.project == project]
	add_titles(rows)
	rows.sort(key=sort_key)
	return rows


def set_chips(row, vehicle, assignment, in_workshop):
	if vehicle.status == "In Maintenance" or vehicle.name in in_workshop:
		row.chips.append("workshop")
	if vehicle.status == "Suspended":
		row.chips.append("suspended")
	if assignment and assignment.assignment_type == TRAINING:
		row.chips.append("training")
	if row.notes:
		row.chips.append("note")
	limit = getdate(add_days(today(), EXPIRY_WINDOW_DAYS))
	for field in ("registration_expiry", "periodic_inspection_expiry"):
		if vehicle.get(field) and getdate(vehicle.get(field)) <= limit:
			row.expiry_days = min(row.get("expiry_days", 999), date_diff(vehicle.get(field), today()))
	if row.get("expiry_days") is not None:
		row.chips.append("expiry")


def add_titles(rows):
	drivers = {row.driver for row in rows if row.driver}
	projects = {row.project for row in rows if row.project}
	driver_info = {
		d.name: d
		for d in frappe.get_list(
			"Driver", filters={"name": ("in", list(drivers))}, fields=["name", "full_name", "cell_number"]
		)
	}
	project_names = dict(
		frappe.get_list(
			"Project", filters={"name": ("in", list(projects))}, fields=["name", "project_name"], as_list=True
		)
	)
	for row in rows:
		info = driver_info.get(row.driver)
		row.driver_name = info.full_name if info else None
		row.phone = info.cell_number if info else None
		row.project_name = project_names.get(row.project)


def sort_key(row):
	rank = STATES.index(row.state)
	if row.state == "red":
		return (rank, -(row.late_hours or 0), row.plate)
	if row.state == "gray":
		return (rank, -(row.since_days or 0), row.plate)
	if row.state == "black":
		return (rank, -(row.idle_days or 0), row.plate)
	return (rank, row.city or "", row.plate)


def count(rows):
	counts = dict.fromkeys(STATES, 0)
	for row in rows:
		counts[row.state] += 1
	return counts
