# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import os
import re
from urllib.parse import unquote, urlparse

import frappe
from frappe import _
from frappe.model.workflow import apply_workflow
from frappe.utils import cint, get_url

from fleetix.fleetix.api.maintenance import WORKER_ROLES
from fleetix.fleetix.doctype.maintenance.maintenance import DEFAULT_PHOTO_SLOTS
from fleetix.fleetix.vehicle import odometer_limit

GATE_APK = {"version_code": 3, "version_name": "1.2", "file": "fleetix-gate.apk"}
LANGUAGES = ("ar", "en", "ur", "hi", "bn")
ARRIVAL_STATES = ("Due Alert", "Driver Arrived")
ROUTES = ("maintenance", "handover")
GATE_SLOTS = dict(zip(("front", "back", "right", "left"), DEFAULT_PHOTO_SLOTS))
PLATE_LETTERS = str.maketrans(
	"\u0627\u0623\u0625\u0622\u0628\u062d\u062f\u0631\u0633\u0635\u0637\u0639\u0642\u0643\u0644\u0645\u0646\u0647\u0648\u0649\u064a"
	"\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669",
	"AAAABJDRSXTEGKLZNHUVV0123456789",
)


@frappe.whitelist(allow_guest=True, methods=["GET"])
def app_version():
	url = None
	if os.path.exists(frappe.get_app_path("fleetix", "public", "apk", GATE_APK["file"])):
		url = get_url("/assets/fleetix/apk/" + GATE_APK["file"])
	return {"version_code": GATE_APK["version_code"], "version_name": GATE_APK["version_name"], "url": url}


@frappe.whitelist(methods=["POST"])
def set_language(lang):
	if lang not in LANGUAGES:
		frappe.throw(_("Choose one of the listed languages"))
	frappe.db.set_value("User", frappe.session.user, "language", lang)
	frappe.clear_cache(user=frappe.session.user)


@frappe.whitelist()
def find_vehicle(code):
	frappe.only_for(WORKER_ROLES)
	name = vehicle_name(code)
	if not name:
		return None
	vehicle = frappe.get_doc("Vehicle", name)
	vehicle.check_permission("read")
	visit = frappe.get_list(
		"Maintenance",
		filters={"vehicle": name, "docstatus": 0},
		fields=["name", "status"],
		order_by="creation desc",
		limit=1,
	)
	handover = frappe.get_list(
		"Vehicle Handover",
		filters={"vehicle": name, "docstatus": 0, "status": "Requested"},
		fields=["name", "handover_type"],
		order_by="creation desc",
		limit=1,
	)
	return {
		"vehicle": vehicle.name,
		"plate": vehicle.license_plate,
		"model": " ".join(filter(None, (vehicle.make, vehicle.model))),
		"last_odometer": cint(vehicle.last_odometer),
		"odometer_limit": odometer_limit(name),
		"driver_name": frappe.db.get_value("Driver", vehicle.current_driver, "full_name")
		if vehicle.get("current_driver")
		else None,
		"project_name": frappe.db.get_value("Project", vehicle.current_project, "project_name")
		if vehicle.get("current_project")
		else None,
		"maintenance": visit[0] if visit else None,
		"handover": handover[0] if handover else None,
	}


@frappe.whitelist(methods=["POST"])
def record_entry(vehicle, odometer, route, photos=None):
	frappe.only_for(WORKER_ROLES)
	if route not in ROUTES:
		frappe.throw(_("Choose where the car goes next"))
	odometer = cint(odometer)
	last_odometer = cint(frappe.db.get_value("Vehicle", vehicle, "last_odometer"))
	if odometer < last_odometer:
		frappe.throw(_("Odometer reading is below the last reading {0}").format(last_odometer))
	limit = odometer_limit(vehicle)
	doc = arrive_for_maintenance(vehicle) if route == "maintenance" else start_handover(vehicle)
	doc.odometer = odometer
	doc.odometer_flagged = 1 if limit and odometer > limit else 0
	attach_photos(doc, frappe.parse_json(photos) if isinstance(photos, str) else photos or [])
	doc.save()
	return {"doctype": doc.doctype, "name": doc.name, "status": doc.status}


@frappe.whitelist(methods=["POST"])
def upload_photo(vehicle):
	frappe.only_for(WORKER_ROLES)
	frappe.get_doc("Vehicle", vehicle).check_permission("read")
	upload = frappe.request.files["file"]
	photo = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": vehicle + "-" + upload.filename,
			"is_private": 1,
			"content": upload.stream.read(),
		}
	).insert()
	return {"name": photo.name, "file_url": photo.file_url}


def attach_photos(doc, photos):
	keeps_rows = doc.meta.get_field("photos")
	for entry in photos:
		name, side = (entry, None) if isinstance(entry, str) else (entry["name"], entry.get("slot"))
		photo = frappe.get_doc("File", name)
		if photo.owner != frappe.session.user:
			frappe.throw(_("This photo was not taken by you"))
		if photo.attached_to_name == doc.name and photo.attached_to_doctype == doc.doctype:
			continue
		if photo.attached_to_name:
			frappe.throw(_("This photo is already attached to another record"))
		photo.attached_to_doctype = doc.doctype
		photo.attached_to_name = doc.name
		photo.save()
		if keeps_rows:
			slot = GATE_SLOTS.get(side, "")
			caption = _(slot) if slot else _("Damage") if (side or "").startswith("damage") else None
			doc.append("photos", {"attachment": photo.file_url, "slot": slot, "caption": caption})


def arrive_for_maintenance(vehicle):
	open_visit = frappe.get_list(
		"Maintenance",
		filters={"vehicle": vehicle, "docstatus": 0},
		fields=["name", "status"],
		order_by="creation desc",
		limit=1,
	)
	if open_visit and open_visit[0].status not in ARRIVAL_STATES:
		frappe.throw(_("This car is already in the workshop"))
	if open_visit:
		visit = frappe.get_doc("Maintenance", open_visit[0].name)
	else:
		visit = frappe.get_doc({"doctype": "Maintenance", "maintenance_type": "Emergency", "vehicle": vehicle}).insert()
	visit.check_permission("write")
	if visit.status == "Due Alert":
		visit.status = "Driver Arrived"
		visit.save()
	return visit


def start_handover(vehicle):
	requested = frappe.get_list(
		"Vehicle Handover",
		filters={"vehicle": vehicle, "docstatus": 0, "status": "Requested"},
		pluck="name",
		order_by="creation desc",
		limit=1,
	)
	if not requested:
		frappe.throw(_("No handover request for this car"))
	handover = frappe.get_doc("Vehicle Handover", requested[0])
	handover.check_permission("write")
	return apply_workflow(handover, "Start Inspection")


def vehicle_name(code):
	code = (code or "").strip()
	if re.search(r"/(app|desk)/vehicle/", code):
		code = unquote(urlparse(code).path.rstrip("/").rsplit("/", 1)[-1])
	if code and frappe.db.exists("Vehicle", code):
		return code
	key = plate_key(code)
	if not key:
		return None
	for row in frappe.get_list("Vehicle", fields=["name", "license_plate"], limit_page_length=0):
		if plate_key(row.license_plate) == key:
			return row.name
	return None


def plate_key(plate):
	text = (plate or "").upper().translate(PLATE_LETTERS)
	digits = "".join(re.findall(r"[0-9]", text))
	letters = "".join(re.findall(r"[A-Z]", text))
	return digits + "-" + letters if digits else None
