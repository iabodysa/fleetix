# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import os
import re

import frappe
from frappe import _
from frappe.utils import cint, date_diff, flt, get_fullname, get_url, getdate, today

from fleetix.fleetix.doctype.maintenance.maintenance import (
	COMPONENT_FIELDS,
	NEXT_DUE_FIELDS,
	component_max_qty,
	due_components,
	next_due,
	photo_slots,
)
from fleetix.fleetix.print_samples import print_samples
from fleetix.fleetix.service_check import checked_rows, finding_rows, last_findings, service_checklist
from fleetix.fleetix.track import SIGN_STATES
from fleetix.fleetix.units import unit_fields
from fleetix.fleetix.vehicle_diagram import VIEWS, body_type, damage_zone, diagram_views

WORKER_ROLES = ("Movement Supervisor", "Rental Manager", "System Manager")
OPEN_STATES = ("Due Alert", "Driver Arrived", "Full Inspection", "Approved", "Service", "Final Check")
FINISH_STATES = ("Full Inspection", "Approved", "Service", "Final Check")
SOON_KM = 1000
SOON_DAYS = 14
APP_LANGUAGES = ("ar", "en", "ur", "hi", "bn")
RTL_LANGUAGES = ("ar", "ur")
DAMAGE_KINDS = ("Scratch", "Dent", "Broken", "Missing")
FIND_LIMIT = 30
FIND_ORDER = {"overdue": 0, "soon": 1, "ok": 2, "none": 3}
VEHICLE_FIELDS = [
	"name",
	"license_plate",
	"make",
	"model",
	"last_odometer",
	"next_battery_due_date",
	*NEXT_DUE_FIELDS.values(),
]
PROFILE_FIELDS = [
	"name",
	"license_plate",
	"make",
	"model",
	"model_year",
	"vehicle_type",
	"color",
	"chassis_no",
	"istimara_no",
	"registration_expiry",
	"status",
	"current_project",
	"current_driver",
	"last_odometer",
]
PROFILE_LIMIT = 20
FRONT_SLOT = "Front Side"
ASSIGNED_STATES = ("Active", "Expiring")
MAINTENANCE_APK = {"version_code": 10, "version_name": "1.9", "file": "fleetix-maintenance.apk"}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def app_version():
	url = None
	if os.path.exists(frappe.get_app_path("fleetix", "public", "apk", MAINTENANCE_APK["file"])):
		url = get_url("/assets/fleetix/apk/" + MAINTENANCE_APK["file"])
	return {
		"version_code": MAINTENANCE_APK["version_code"],
		"version_name": MAINTENANCE_APK["version_name"],
		"url": url,
	}


@frappe.whitelist(methods=["POST"])
def set_language(lang):
	frappe.only_for(WORKER_ROLES)
	if lang not in APP_LANGUAGES or not frappe.db.exists("Language", lang):
		frappe.throw(_("This language is not available"))
	frappe.db.set_value("User", frappe.session.user, "language", lang)


@frappe.whitelist()
def get_boot():
	from fleetix.www.maintenance import get_boot as build_boot

	return {"boot": build_boot(), "csrf_token": frappe.sessions.get_csrf_token()}


@frappe.whitelist()
def get_due_queue():
	frappe.only_for(WORKER_ROLES)
	visits = frappe.get_list(
		"Maintenance",
		filters={"docstatus": 0, "status": ("in", OPEN_STATES)},
		fields=["name", "vehicle", "status", "driver", "project", "inspection", "odometer", "modified"],
		order_by="modified desc",
	)
	vehicles = {
		row.name: row
		for row in frappe.get_all(
			"Vehicle", filters={"name": ("in", [visit.vehicle for visit in visits])}, fields=VEHICLE_FIELDS
		)
	}
	return [queue_row(visit, vehicles[visit.vehicle]) for visit in visits]


@frappe.whitelist()
def find_vehicles(plate=None, start=0):
	frappe.only_for(WORKER_ROLES)
	from fleetix.fleetix.api.gate import PLATE_LETTERS

	text = (plate or "").upper().translate(PLATE_LETTERS)
	digits = "".join(re.findall(r"[0-9]", text))
	letters = "".join(re.findall(r"[A-Z]", text))
	open_visits = dict(
		frappe.get_all(
			"Maintenance",
			filters={"docstatus": 0, "status": ("in", OPEN_STATES)},
			fields=["vehicle", "name"],
			order_by="modified asc",
			as_list=True,
		)
	)
	found = []
	for row in frappe.get_list("Vehicle", fields=VEHICLE_FIELDS, limit_page_length=0):
		key = (row.license_plate or "").upper().translate(PLATE_LETTERS)
		if digits in "".join(re.findall(r"[0-9]", key)) and letters in "".join(re.findall(r"[A-Z]", key)):
			found.append(vehicle_row(row, open_visits.get(row.name)))
	found.sort(
		key=lambda row: (
			FIND_ORDER[row["state"]],
			row["remaining_km"] if row["remaining_km"] is not None else 0,
		)
	)
	start = cint(start)
	return {"rows": found[start : start + FIND_LIMIT], "total": len(found)}


@frappe.whitelist(methods=["POST"])
def open_vehicle_visit(vehicle):
	frappe.only_for(WORKER_ROLES)
	frappe.has_permission("Vehicle", "read", vehicle, throw=True)
	name = frappe.db.get_value(
		"Maintenance",
		{"vehicle": vehicle, "docstatus": 0, "status": ("in", OPEN_STATES)},
		"name",
		order_by="modified desc",
	)
	if name:
		visit = frappe.get_doc("Maintenance", name)
	else:
		visit = frappe.get_doc(
			{"doctype": "Maintenance", "maintenance_type": "Periodic", "vehicle": vehicle}
		).insert()
	if visit.status == "Due Alert":
		visit.status = "Driver Arrived"
		visit.save()
	return queue_row(visit, frappe.get_doc("Vehicle", visit.vehicle))


@frappe.whitelist(methods=["POST"])
def open_scanned_visit(code):
	from fleetix.fleetix.api.gate import vehicle_name

	vehicle = vehicle_name(code)
	if not vehicle:
		frappe.throw(_("No vehicle with this plate"))
	return open_vehicle_visit(vehicle)


def queue_row(visit, vehicle):
	components = component_states(vehicle, cint(vehicle.last_odometer))
	return {
		"maintenance": visit.name,
		"status": visit.status,
		"vehicle": vehicle.name,
		"plate": vehicle.license_plate,
		"model": " ".join(filter(None, (vehicle.make, vehicle.model))),
		"driver": visit.driver,
		"project": visit.project,
		"inspection": visit.inspection,
		"odometer": cint(visit.odometer),
		"last_odometer": cint(vehicle.last_odometer),
		"due": [row["component"] for row in components if row["state"] == "overdue"],
		"worst": worst_overdue(components, cint(vehicle.last_odometer)),
		"findings": visit_findings(visit.name) if visit.status == "Final Check" else [],
	}


def visit_findings(maintenance):
	return frappe.get_all(
		"Maintenance Finding",
		filters={"parent": maintenance, "parenttype": "Maintenance"},
		fields=["part", "reason", "note"],
		order_by="idx asc",
	)


def vehicle_row(vehicle, maintenance):
	components = [
		row
		for row in component_states(vehicle, cint(vehicle.last_odometer))
		if row["due_km"] or row["due_date"]
	]
	remaining = [row["remaining_km"] for row in components if row["remaining_km"] is not None]
	states = {row["state"] for row in components}
	state = next((name for name in ("overdue", "soon", "ok") if name in states), "none")
	return {
		"vehicle": vehicle.name,
		"plate": vehicle.license_plate,
		"model": " ".join(filter(None, (vehicle.make, vehicle.model))),
		"maintenance": maintenance,
		"state": state,
		"remaining_km": min(remaining) if remaining else None,
		"due": [row["component"] for row in components if row["state"] == "overdue"],
		"worst": worst_overdue(components, cint(vehicle.last_odometer)),
	}


@frappe.whitelist()
def get_vehicle_checklist(maintenance, odometer=None):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("read")
	vehicle = frappe.get_doc("Vehicle", visit.vehicle)
	reading = max(cint(vehicle.last_odometer), cint(odometer) or cint(visit.odometer))
	replaced = {row.component: row for row in visit.components_replaced}
	components = []
	for row in component_states(vehicle, reading):
		items = component_items(row["component"], vehicle.name)
		chosen = replaced.get(row["component"])
		row.update(
			{
				"ticked": bool(chosen) if replaced else row["state"] == "overdue",
				"item": chosen.item if chosen else (items[0]["item_code"] if items else None),
				"qty": flt(chosen.qty) if chosen else 1,
				"max_qty": component_max_qty(row["component"]),
				"items": items,
			}
		)
		components.append(row)
	return {
		"maintenance": visit.name,
		"status": visit.status,
		"odometer": cint(visit.odometer),
		"vehicle": {
			"name": vehicle.name,
			"plate": vehicle.license_plate,
			"model": " ".join(filter(None, (vehicle.make, vehicle.model))),
			"last_odometer": cint(vehicle.last_odometer),
			"driver": visit.driver,
			"driver_name": frappe.db.get_value("Driver", visit.driver, "full_name") if visit.driver else None,
			"project": visit.project,
			"project_name": frappe.db.get_value("Project", visit.project, "project_name")
			if visit.project
			else None,
		},
		"components": components,
		"final_check": [
			{"item": row.item, "condition": row.condition, "notes": row.notes} for row in visit.final_check
		],
		"service_checklist": service_checklist(),
		"findings": visit_findings(visit.name),
		"last_findings": last_findings("Maintenance", {"vehicle": visit.vehicle, "docstatus": 1}, visit.name),
	}


@frappe.whitelist()
def get_print_samples():
	frappe.only_for(WORKER_ROLES)
	return print_samples()


@frappe.whitelist()
def get_vehicle_diagram(maintenance):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("read")
	return diagram_views(visit.vehicle)


@frappe.whitelist(methods=["POST"])
def save_damage_marks(maintenance, damages):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("write")
	damages = frappe.parse_json(damages) or []
	if any(
		row.get("view") not in VIEWS
		or not 0 <= flt(row.get("x")) <= 1
		or not 0 <= flt(row.get("y")) <= 1
		or row.get("kind") not in (None, *DAMAGE_KINDS)
		for row in damages
	):
		frappe.throw(_("Mark the damage on the vehicle drawing"))
	body = body_type(visit.vehicle)
	visit.damage_marks = frappe.as_json(
		[
			{
				"view": row["view"],
				"x": flt(row["x"], 4),
				"y": flt(row["y"], 4),
				"kind": row.get("kind"),
				"area": damage_zone(body, row["view"], flt(row["y"])),
			}
			for row in damages
		]
	)
	visit.save()
	return get_photos(visit.name)


@frappe.whitelist()
def get_photos(maintenance):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("read")
	slots = photo_slots(visit) + [{"slot": "", "label": _("Other photos")}]
	known = {row["slot"] for row in slots}
	taken = {}
	for row in visit.photos:
		taken.setdefault(row.slot if row.slot in known else "", []).append(row.attachment)
	listed = {row.attachment for row in visit.photos}
	attached = frappe.get_all(
		"File",
		filters={"attached_to_doctype": "Maintenance", "attached_to_name": visit.name},
		pluck="file_url",
		order_by="creation asc",
	)
	taken.setdefault("", []).extend(url for url in attached if url not in listed)
	return [dict(row, photos=taken.get(row["slot"], [])) for row in slots]


@frappe.whitelist(methods=["POST"])
def save_odometer(maintenance, odometer):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("write")
	odometer = cint(odometer)
	if visit.status not in SIGN_STATES or odometer < cint(
		frappe.db.get_value("Vehicle", visit.vehicle, "last_odometer")
	):
		return cint(visit.odometer)
	visit.db_set("odometer", odometer)
	return odometer


@frappe.whitelist(methods=["POST"])
def save_inspection(maintenance, odometer, components, driver_signature):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("write")
	components = frappe.parse_json(components) or []
	odometer = cint(odometer)
	last_odometer = cint(frappe.db.get_value("Vehicle", visit.vehicle, "last_odometer"))
	if odometer < last_odometer:
		frappe.throw(_("Odometer reading is below the last reading {0}").format(last_odometer))
	if not components:
		frappe.throw(_("Select at least one component"))
	if any(not row.get("item") or flt(row.get("qty")) <= 0 for row in components):
		frappe.throw(_("Every selected component needs an item and a quantity"))
	for row in components:
		max_qty = component_max_qty(row["component"])
		if max_qty and flt(row["qty"]) > max_qty:
			frappe.throw(_("{0} allows at most {1}").format(_(row["component"]), f"{max_qty:g}"))
	damages = frappe.parse_json(visit.damage_marks) or []
	if visit.status not in SIGN_STATES or visit.inspection:
		frappe.throw(_("This visit is not waiting for inspection"))
	ticked = {row["component"] for row in components}
	inspection = frappe.get_doc(
		{
			"doctype": "Vehicle Inspection",
			"reference_type": "Maintenance",
			"reference_name": visit.name,
			"vehicle": visit.vehicle,
			"odometer": odometer,
			"checklist": [
				{"item": component, "condition": "Needs Repair" if component in ticked else "Good"}
				for component in COMPONENT_FIELDS
			],
			"photos": [
				{"attachment": row.attachment, "caption": row.caption, "slot": row.slot}
				for row in visit.photos
			],
			"driver_signature": driver_signature,
		}
	).insert()
	for photo in frappe.get_all(
		"File", filters={"attached_to_doctype": "Maintenance", "attached_to_name": visit.name}, pluck="name"
	):
		frappe.db.set_value(
			"File",
			photo,
			{
				"attached_to_doctype": "Vehicle Inspection",
				"attached_to_name": inspection.name,
				"attached_to_field": "photos",
			},
		)
	visit.status = "Service"
	visit.odometer = odometer
	visit.inspection = inspection.name
	visit.set(
		"components_replaced",
		[{"component": row["component"], "item": row["item"], "qty": flt(row["qty"])} for row in components],
	)
	visit.save()
	record_language = frappe.get_system_settings("language")
	for no, row in enumerate(damages, start=1):
		frappe.get_doc(
			{
				"doctype": "Damage",
				"vehicle": visit.vehicle,
				"source": "Maintenance",
				"source_reference": visit.name,
				"driver": visit.driver,
				"project": visit.project,
				"area": row["area"],
				"diagram_view": row["view"],
				"mark_x": row["x"],
				"mark_y": row["y"],
				"description": _(row.get("kind") or row["area"], lang=record_language),
				"photos": [
					{"attachment": photo.attachment, "caption": photo.caption, "slot": photo.slot}
					for photo in visit.photos
					if photo.slot == f"damage-{no}"
				],
				"status": "Detected",
			}
		).insert()
	return {"maintenance": visit.name, "status": visit.status, "inspection": inspection.name}


@frappe.whitelist(methods=["POST"])
def finish_maintenance(maintenance, final_check, findings=None):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("write")
	if visit.status not in FINISH_STATES or not visit.inspection:
		frappe.throw(_("This visit has no inspection yet"))
	checked = checked_rows(
		frappe.parse_json(final_check), [row.component for row in visit.components_replaced]
	)
	visit.set("final_check", checked)
	visit.set("findings", finding_rows(frappe.parse_json(findings), checked))
	visit.submit()
	return get_visit_result(visit.name)


@frappe.whitelist()
def get_visit_result(maintenance):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("read")
	vehicle = frappe.get_doc("Vehicle", visit.vehicle)
	replaced = {row.component for row in visit.components_replaced}
	return {
		"maintenance": visit.name,
		"status": visit.status,
		"docstatus": visit.docstatus,
		"plate": vehicle.license_plate,
		"model": " ".join(filter(None, (vehicle.make, vehicle.model))),
		"odometer": cint(visit.odometer),
		"visit_date": getdate(visit.visit_datetime) if visit.visit_datetime else getdate(),
		"items_issued": visit.items_issued,
		"next_due": [
			dict(row, replaced=row["component"] in replaced)
			for row in component_states(vehicle, cint(vehicle.last_odometer))
		],
	}


@frappe.whitelist()
def get_history(vehicle):
	frappe.only_for(WORKER_ROLES)
	frappe.has_permission("Vehicle", "read", vehicle, throw=True)
	return {
		"visits": frappe.get_list(
			"Maintenance",
			filters={"vehicle": vehicle},
			fields=["name", "status", "docstatus", "visit_datetime", "odometer"],
			order_by="creation desc",
			limit=20,
		),
		"replacements": frappe.get_list(
			"Component Replacement Log",
			filters={"vehicle": vehicle},
			fields=[
				"component",
				"replacement_date",
				"odometer_at_replacement",
				"item",
				"next_due_odometer",
				"next_due_date",
			],
			order_by="replacement_date desc, creation desc",
			limit=50,
		),
	}


@frappe.whitelist()
def get_vehicle_profile(vehicle):
	frappe.only_for(WORKER_ROLES)
	frappe.has_permission("Vehicle", "read", vehicle, throw=True)
	car = frappe.db.get_value("Vehicle", vehicle, PROFILE_FIELDS, as_dict=True)
	visits = frappe.get_list(
		"Maintenance",
		filters={"vehicle": vehicle, "docstatus": ("<", 2)},
		fields=["name", "maintenance_type", "status", "docstatus", "odometer", "visit_datetime", "creation"],
		order_by="creation desc",
		limit=PROFILE_LIMIT,
	)
	inspections = frappe.get_list(
		"Vehicle Inspection",
		filters={"vehicle": vehicle},
		fields=["name", "odometer", "inspection_datetime", "creation"],
		order_by="creation desc",
		limit=PROFILE_LIMIT,
	)
	handovers = frappe.get_list(
		"Vehicle Handover",
		filters={"vehicle": vehicle, "docstatus": ("<", 2), "odometer": (">", 0)},
		fields=["name", "odometer", "handover_datetime", "creation"],
		order_by="creation desc",
		limit=PROFILE_LIMIT,
	)
	photos = {}
	for row in frappe.get_all(
		"Vehicle Inspection Photo",
		filters={
			"parenttype": ("in", ("Maintenance", "Vehicle Inspection")),
			"parent": ("in", [row.name for row in visits + inspections] or [""]),
			"attachment": ("is", "set"),
		},
		fields=["parent", "slot", "attachment"],
		order_by="idx asc",
	):
		photos.setdefault(row.parent, []).append(row)
	readings = [
		(row.visit_datetime or row.creation, "Maintenance", row) for row in visits
	] + [
		(row.inspection_datetime or row.creation, "Vehicle Inspection", row) for row in inspections
	] + [(row.handover_datetime or row.creation, "Vehicle Handover", row) for row in handovers]
	readings.sort(key=lambda reading: reading[0], reverse=True)
	front = next(
		(
			photo.attachment
			for _when, _doctype, row in readings
			for photo in photos.get(row.name, [])
			if photo.slot == FRONT_SLOT
		),
		None,
	)
	odometer = next(
		(
			{"date": str(getdate(when)), "doctype": doctype, "name": row.name}
			for when, doctype, row in readings
			if cint(row.odometer) and cint(row.odometer) == cint(car.last_odometer)
		),
		{},
	)
	done = sorted(
		(row for row in visits if row.docstatus == 1), key=lambda row: row.visit_datetime or row.creation
	)
	assignment = frappe.get_list(
		"Vehicle Assignment",
		filters={"vehicle": vehicle, "docstatus": 1, "status": ("in", ASSIGNED_STATES)},
		fields=["name", "driver", "approved_by", "assignment_type", "from_datetime", "to_datetime"],
		order_by="from_datetime desc",
		limit=1,
	)
	return {
		"vehicle": car,
		"driver": driver_title(car.current_driver),
		"project_name": frappe.db.get_value("Project", car.current_project, "project_name")
		if car.current_project
		else None,
		"front_photo": front,
		"odometer": dict(odometer, value=cint(car.last_odometer)),
		"last_maintenance": profile_visit(done[-1], photos) if done else None,
		"assignment": profile_assignment(assignment[0]) if assignment else None,
		"visits": [profile_visit(row, photos) for row in visits],
		"prints": profile_prints(vehicle, visits, inspections),
	}


def driver_title(driver):
	return frappe.db.get_value("Driver", driver, "full_name") if driver else None


def profile_visit(row, photos):
	return {
		"name": row.name,
		"date": str(getdate(row.visit_datetime or row.creation)),
		"type": row.maintenance_type,
		"status": row.status,
		"odometer": cint(row.odometer),
		"photos": [{"slot": photo.slot, "url": photo.attachment} for photo in photos.get(row.name, [])],
	}


def profile_assignment(row):
	return {
		"name": row.name,
		"driver": driver_title(row.driver),
		"approved_by": get_fullname(row.approved_by) if row.approved_by else None,
		"type": row.assignment_type,
		"from_date": str(getdate(row.from_datetime)) if row.from_datetime else None,
		"to_date": str(getdate(row.to_datetime)) if row.to_datetime else None,
	}


def profile_prints(vehicle, visits, inspections):
	targets = [
		("Vehicle", vehicle, "Thermal Vehicle Card"),
		("Vehicle", vehicle, "Thermal Vehicle Label"),
	]
	if visits:
		targets += [
			("Maintenance", visits[0].name, "Thermal Gate Entry Pass"),
			("Maintenance", visits[0].name, "Thermal Gate Exit Pass"),
		]
	if inspections:
		targets.append(("Vehicle Inspection", inspections[0].name, "Thermal Damage Sheet"))
	return [
		{"doctype": doctype, "name": name, "format": print_format}
		for doctype, name, print_format in targets
		if frappe.has_permission(doctype, "print", name)
	]


def component_states(vehicle, reading):
	vehicle.last_odometer = reading
	due = set(due_components(vehicle))
	rows = []
	for component in COMPONENT_FIELDS:
		due_km, due_date = next_due(vehicle, component)
		rows.append(
			{
				"component": component,
				"due_km": cint(due_km) or None,
				"due_date": due_date,
				"remaining_km": cint(due_km) - reading if cint(due_km) else None,
				"remaining_days": date_diff(due_date, today()) if due_date else None,
				"state": component_state(component in due, due_km, due_date, reading),
			}
		)
	return rows


def component_state(is_due, due_km, due_date, reading):
	if is_due:
		return "overdue"
	if cint(due_km) and cint(due_km) - reading <= SOON_KM:
		return "soon"
	if due_date and date_diff(due_date, today()) <= SOON_DAYS:
		return "soon"
	return "ok"


def worst_overdue(components, reading):
	overdue_km = [
		reading - row["due_km"] for row in components if row["state"] == "overdue" and row["due_km"]
	]
	overdue_days = [
		-row["remaining_days"] for row in components if row["state"] == "overdue" and row["due_date"]
	]
	if overdue_km:
		return {"km": max(overdue_km)}
	if overdue_days:
		return {"days": max(overdue_days)}
	return None


def component_items(component, vehicle):
	rules = [
		row for row in frappe.get_single("Fleetix Settings").component_items if row.component == component
	]
	groups = [row.item_group for row in rules if row.item_group]
	words = [word.strip() for row in rules for word in (row.keywords or "").splitlines() if word.strip()]
	if not groups and not words:
		return []
	matches = [["item_group", "in", groups]] if groups else []
	matches += [["item_name", "like", f"%{word}%"] for word in words]
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	items = frappe.get_all(
		"Item",
		filters={"disabled": 0, "is_stock_item": 1},
		or_filters=matches,
		fields=["item_code", "item_name", "stock_uom"],
		order_by="item_name asc",
	)
	bins = {
		row.item_code: row
		for row in frappe.get_all(
			"Bin",
			filters={"warehouse": warehouse, "item_code": ("in", [row.item_code for row in items] or [""])},
			fields=["item_code", "actual_qty"],
		)
	}
	last_item = frappe.db.get_value(
		"Component Replacement Log",
		{"vehicle": vehicle, "component": component},
		"item",
		order_by="replacement_date desc, creation desc",
	)
	for row in items:
		stock = bins.get(row.item_code) or {}
		row["stock"] = flt(stock.get("actual_qty"))
	items.sort(key=lambda row: row.item_code != last_item)
	return unit_fields(items, component)
