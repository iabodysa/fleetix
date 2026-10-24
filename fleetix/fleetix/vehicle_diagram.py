# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re
from functools import cache

import frappe

UNIT_MM = 0.3
GROUND_Y = 74
MARKER_RADIUS_MM = 2.25
MARKER_STEP_MM = 5
MARKER_FONT_MM = 7 * 0.3528
LINE_MM = 0.75 * 0.3528
HAIRLINE_MM = 0.5 * 0.3528
VIEWS = ("left", "front", "rear", "right")
VIEW_AREAS = {"left": "Left Side", "front": "Front", "rear": "Rear", "right": "Right Side"}
ROOF_BAND = 8
SIZE_ATTRS = re.compile(r' width="[^"]*" height="[^"]*"')
BODIES = {
	"Car": ("car-side", "car-front", "car-rear"),
	"SUV": ("suv-side", "suv-front", "suv-rear"),
	"Pickup Truck": ("pickup-side", "pickup-front", "pickup-rear"),
	"Van": ("van-side", "van-front", "van-rear"),
	"Bus": ("bus-side", "bus-front", "bus-rear"),
	"Truck": ("truck-side", "truck-front", "truck-rear"),
	"Motorbike": ("motorbike-side", "motorbike-front", "motorbike-rear"),
}
ANCHORS = {
	"Front": ("front", 45, 46),
	"Rear": ("rear", 45, 46),
	"Right Side": ("right", 100, 46),
	"Left Side": ("left", 100, 46),
}
ROOF = {
	"Car": (98, 19),
	"SUV": (126, 17),
	"Pickup Truck": (112, 19),
	"Van": (100, 9),
	"Bus": (100, 9),
	"Truck": (76, 10),
}
SVG = re.compile(r'<svg[^>]*viewBox="0 0 ([0-9.]+) ([0-9.]+)"[^>]*>(.*)</svg>', re.S)


@cache
def _icon(name):
	path = frappe.get_app_path("fleetix", "public", "images", "vehicles", f"{name}.svg")
	with open(path) as svg:
		width, height, shapes = SVG.search(svg.read()).groups()
	return float(width), float(height), shapes.strip()


def _view(icon, view, marks):
	width, height, shapes = _icon(icon)
	if view == "left":
		shapes = f'<g transform="translate({width:g},0) scale(-1,1)">{shapes}</g>'
	radius, font = MARKER_RADIUS_MM / UNIT_MM, MARKER_FONT_MM / UNIT_MM
	stroke = LINE_MM / UNIT_MM * 2
	drawn = "".join(
		(
			f'<path d="M{cx - radius:.2f} {cy - radius:.2f}L{cx + radius:.2f} {cy + radius:.2f}M{cx + radius:.2f} {cy - radius:.2f}L{cx - radius:.2f} {cy + radius:.2f}" stroke="#000" stroke-width="{stroke:.2f}" stroke-linecap="round"/>'
			f'<text x="{cx + radius * 1.9:.2f}" y="{cy - radius * 0.6:.2f}" text-anchor="middle" font-family="Tajawal,sans-serif" font-weight="700" font-size="{font:.2f}" fill="#000">{no}</text>'
		)
		if exact
		else (
			f'<circle cx="{cx:g}" cy="{cy:g}" r="{radius:.2f}" fill="#FFFFFF" stroke="#000" stroke-width="{LINE_MM / UNIT_MM:.2f}"/>'
			f'<text x="{cx:g}" y="{cy + font * 0.36:.2f}" text-anchor="middle" font-family="Tajawal,sans-serif" font-weight="700" font-size="{font:.2f}" fill="#000">{no}</text>'
		)
		for no, cx, cy, exact in marks
	)
	return (
		f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" width="{width * UNIT_MM:.1f}mm" height="{height * UNIT_MM:.1f}mm">'
		f'<g fill="none" stroke="#000" stroke-linecap="round" stroke-linejoin="round">{shapes}'
		f'<path d="M0 {GROUND_Y}H{width:g}" stroke-width="{HAIRLINE_MM / UNIT_MM:.2f}"/></g>{drawn}</svg>'
	)


def body_type(vehicle):
	vehicle_type = frappe.db.get_value("Vehicle", vehicle, "vehicle_type") if vehicle else None
	return (frappe.db.get_value("Vehicle Type", vehicle_type, "body_type") if vehicle_type else None) or "Car"


def view_icons(body):
	side, front, rear = BODIES.get(body, BODIES["Car"])
	return {"left": side, "front": front, "rear": rear, "right": side}


def damage_zone(body, view, y):
	icon = view_icons(body)[view]
	if view in ("left", "right") and body in ROOF and y * _icon(icon)[1] <= ROOF[body][1] + ROOF_BAND:
		return "Roof"
	return VIEW_AREAS[view]


def diagram_views(vehicle):
	body = body_type(vehicle)
	views = []
	for view, icon in view_icons(body).items():
		width, height, _shapes = _icon(icon)
		svg = SIZE_ATTRS.sub(' width="100%" height="100%"', _view(icon, view, []), count=1)
		views.append({"view": view, "svg": svg, "aspect": round(width / height, 4)})
	return {"body": body, "views": views}


def vehicle_views(vehicle=None, damages=None):
	body = body_type(vehicle)
	icons = view_icons(body)
	anchors = dict(ANCHORS)
	if body in ROOF:
		anchors["Roof"] = ("right", *ROOF[body])
	spots = {}
	unplaced = []
	marks = {view: [] for view in VIEWS}
	for damage in damages or []:
		view = damage.get("view")
		if view in icons and damage.get("x") is not None and damage.get("y") is not None:
			width, height, _shapes = _icon(icons[view])
			marks[view].append(
				(damage.get("no"), round(damage["x"] * width, 2), round(damage["y"] * height, 2), True)
			)
			continue
		area = damage.get("area")
		if not area:
			continue
		if area not in anchors:
			unplaced.append((damage.get("no"), area))
			continue
		spots.setdefault(anchors[area], []).append(damage.get("no"))
	step = MARKER_STEP_MM / UNIT_MM
	for (view, cx, cy), numbers in spots.items():
		marks[view] += [
			(no, round(cx + (i - (len(numbers) - 1) / 2) * step, 2), cy, False)
			for i, no in enumerate(numbers)
		]
	rendered = [
		(view, _view(icons[view], view, marks[view]), _icon(icons[view])[0] * UNIT_MM) for view in VIEWS
	]
	return {"body": body, "views": rendered, "unplaced": unplaced}
