# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import os
from urllib.parse import quote

import frappe
from frappe import _
from frappe.model.workflow import apply_workflow
from frappe.utils import cint, date_diff, flt, get_host_name_from_request, get_url, getdate, today

from fleetix.fleetix.doctype.maintenance.maintenance import COMPONENT_FIELDS, due_components, next_due
from fleetix.fleetix.document_qr import qr_data_url

WORKER_ROLES = ("Movement Supervisor", "System Manager")
OPEN_STATES = ("Due Alert", "Driver Arrived", "Full Inspection", "Approved", "Service", "Final Check")
COMPONENT_GROUPS = {
	"Oil": "Oil",
	"Oil Filter": "Oil Filter",
	"Front Tires": "Tires",
	"Rear Tires": "Tires",
	"Battery": "Battery",
}
FINISH_ACTIONS = {"Approved": "Start Service", "Service": "Finish Service", "Final Check": "Complete"}
SOON_KM = 1000
SOON_DAYS = 14
MAINTENANCE_APK = {"version_code": 3, "version_name": "1.2", "file": "fleetix-maintenance.apk"}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def app_version():
	url = None
	if os.path.exists(frappe.get_app_path("fleetix", "public", "apk", MAINTENANCE_APK["file"])):
		url = get_url("/assets/fleetix/apk/" + MAINTENANCE_APK["file"])
	return {"version_code": MAINTENANCE_APK["version_code"], "version_name": MAINTENANCE_APK["version_name"], "url": url}


@frappe.whitelist()
def get_due_queue():
	frappe.only_for(WORKER_ROLES)
	visits = frappe.get_list(
		"Maintenance",
		filters={"docstatus": 0, "status": ("in", OPEN_STATES)},
		fields=["name", "vehicle", "status", "driver", "project", "inspection", "odometer", "modified"],
		order_by="modified desc",
	)
	queue = []
	for visit in visits:
		vehicle = frappe.get_doc("Vehicle", visit.vehicle)
		components = component_states(vehicle, cint(vehicle.last_odometer))
		queue.append(
			{
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
			}
		)
	return queue


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
			"project_name": frappe.db.get_value("Project", visit.project, "project_name") if visit.project else None,
		},
		"components": components,
		"final_check": [
			{"item": row.item, "condition": row.condition, "notes": row.notes} for row in visit.final_check
		],
	}


@frappe.whitelist(methods=["POST"])
def upload_photo(maintenance):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("write")
	upload = frappe.request.files["file"]
	photo = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": upload.filename,
			"attached_to_doctype": "Maintenance",
			"attached_to_name": visit.name,
			"is_private": 1,
			"content": upload.stream.read(),
		}
	).insert()
	return {"name": photo.name, "file_url": photo.file_url}


@frappe.whitelist()
def get_photos(maintenance):
	frappe.only_for(WORKER_ROLES)
	frappe.get_doc("Maintenance", maintenance).check_permission("read")
	return frappe.get_all(
		"File",
		filters={"attached_to_doctype": "Maintenance", "attached_to_name": maintenance},
		fields=["name", "file_url"],
		order_by="creation asc",
	)


@frappe.whitelist()
def get_photo_link(maintenance):
	frappe.only_for(WORKER_ROLES)
	frappe.get_doc("Maintenance", maintenance).check_permission("read")
	url = get_host_name_from_request() + "/maintenance/photos/" + quote(maintenance)
	return {"url": url, "qr": qr_data_url(url)}


@frappe.whitelist(methods=["POST"])
def send_for_approval(maintenance, odometer, components, photos, driver_signature, inspector_signature):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("write")
	components = frappe.parse_json(components) or []
	photos = frappe.parse_json(photos) or []
	odometer = cint(odometer)
	last_odometer = cint(frappe.db.get_value("Vehicle", visit.vehicle, "last_odometer"))
	if odometer < last_odometer:
		frappe.throw(_("Odometer reading is below the last reading {0}").format(last_odometer))
	if not components:
		frappe.throw(_("Select at least one component"))
	if any(not row.get("item") or flt(row.get("qty")) <= 0 for row in components):
		frappe.throw(_("Every selected component needs an item and a quantity"))
	for row in photos:
		if not frappe.db.exists(
			"File",
			{
				"name": row.get("file"),
				"file_url": row.get("file_url"),
				"attached_to_doctype": "Maintenance",
				"attached_to_name": visit.name,
			},
		):
			frappe.throw(_("Photo {0} does not belong to this visit").format(row.get("caption")))
	if visit.status == "Driver Arrived":
		visit = apply_workflow(visit, "Start Inspection")
	if visit.status != "Full Inspection":
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
			"photos": [{"attachment": row["file_url"], "caption": row.get("caption")} for row in photos],
			"driver_signature": driver_signature,
			"inspector_signature": inspector_signature,
		}
	).insert()
	for row in photos:
		frappe.db.set_value(
			"File",
			row["file"],
			{
				"attached_to_doctype": "Vehicle Inspection",
				"attached_to_name": inspection.name,
				"attached_to_field": "photos",
			},
		)
	visit.odometer = odometer
	visit.inspection = inspection.name
	visit.set(
		"components_replaced",
		[{"component": row["component"], "item": row["item"], "qty": flt(row["qty"])} for row in components],
	)
	visit.save()
	return {"maintenance": visit.name, "status": visit.status, "inspection": inspection.name}


@frappe.whitelist(methods=["POST"])
def finish_maintenance(maintenance, final_check):
	frappe.only_for(WORKER_ROLES)
	visit = frappe.get_doc("Maintenance", maintenance)
	visit.check_permission("write")
	if visit.status not in FINISH_ACTIONS:
		frappe.throw(_("This visit is not approved yet"))
	rows = frappe.parse_json(final_check) or []
	if any(row.get("condition") == "Needs Repair" and not row.get("notes") for row in rows):
		frappe.throw(_("Add a note to every row that needs repair"))
	if rows:
		visit.set(
			"final_check",
			[{"item": row["item"], "condition": row["condition"], "notes": row.get("notes")} for row in rows],
		)
		visit.save()
	while visit.status in FINISH_ACTIONS:
		visit = apply_workflow(visit, FINISH_ACTIONS[visit.status])
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
	warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
	items = frappe.get_all(
		"Item",
		filters={"item_group": COMPONENT_GROUPS[component], "disabled": 0, "is_stock_item": 1},
		fields=["item_code", "item_name", "stock_uom"],
		order_by="item_name asc",
	)
	stock = dict(
		frappe.get_all(
			"Bin",
			filters={"warehouse": warehouse, "item_code": ("in", [row.item_code for row in items] or [""])},
			fields=["item_code", "actual_qty"],
			as_list=True,
		)
	)
	last_item = frappe.db.get_value(
		"Component Replacement Log",
		{"vehicle": vehicle, "component": component},
		"item",
		order_by="replacement_date desc, creation desc",
	)
	for row in items:
		row["stock"] = flt(stock.get(row.item_code))
	items.sort(key=lambda row: row.item_code != last_item)
	return items
