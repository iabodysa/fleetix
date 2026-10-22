# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re
from functools import lru_cache

import frappe

UNIT_MM = 0.3
GROUND_Y = 74
MARKER_RADIUS_MM = 2.25
MARKER_STEP_MM = 5
MARKER_FONT_MM = 7 * 0.3528
LINE_MM = 0.75 * 0.3528
HAIRLINE_MM = 0.5 * 0.3528
VIEWS = ("left", "front", "rear", "right")
BODIES = {
	"Car": ("car-side", "car-front", "car-rear"),
	"Pickup Truck": ("pickup-side", "car-front", "pickup-rear"),
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
ROOF = {"Car": (98, 19), "Pickup Truck": (112, 19), "Van": (100, 9), "Bus": (100, 9), "Truck": (76, 10)}
SVG = re.compile(r'<svg[^>]*viewBox="0 0 ([0-9.]+) ([0-9.]+)"[^>]*>(.*)</svg>', re.S)


@lru_cache(maxsize=None)
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
	drawn = "".join(
		f'<circle cx="{cx:g}" cy="{cy:g}" r="{radius:.2f}" fill="#FFFFFF" stroke="#000" stroke-width="{LINE_MM / UNIT_MM:.2f}"/>'
		f'<text x="{cx:g}" y="{cy + font * 0.36:.2f}" text-anchor="middle" font-family="Tajawal,sans-serif" font-weight="700" font-size="{font:.2f}" fill="#000">{no}</text>'
		for no, cx, cy in marks
	)
	return (
		f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" width="{width * UNIT_MM:.1f}mm" height="{height * UNIT_MM:.1f}mm">'
		f'<g fill="none" stroke="#000" stroke-linecap="round" stroke-linejoin="round">{shapes}'
		f'<path d="M0 {GROUND_Y}H{width:g}" stroke-width="{HAIRLINE_MM / UNIT_MM:.2f}"/></g>{drawn}</svg>'
	)


def vehicle_views(vehicle=None, damages=None):
	vehicle_type = frappe.db.get_value("Vehicle", vehicle, "vehicle_type") if vehicle else None
	body = (frappe.db.get_value("Vehicle Type", vehicle_type, "body_type") if vehicle_type else None) or "Car"
	side, front, rear = BODIES.get(body, BODIES["Car"])
	anchors = dict(ANCHORS)
	if body in ROOF:
		anchors["Roof"] = ("right", *ROOF[body])
	spots = {}
	unplaced = []
	for damage in damages or []:
		area = damage.get("area")
		if not area:
			continue
		if area not in anchors:
			unplaced.append((damage.get("no"), area))
			continue
		spots.setdefault(anchors[area], []).append(damage.get("no"))
	step = MARKER_STEP_MM / UNIT_MM
	marks = {view: [] for view in VIEWS}
	for (view, cx, cy), numbers in spots.items():
		marks[view] += [(no, round(cx + (i - (len(numbers) - 1) / 2) * step, 2), cy) for i, no in enumerate(numbers)]
	icons = {"left": side, "front": front, "rear": rear, "right": side}
	rendered = [(view, _view(icons[view], view, marks[view]), _icon(icons[view])[0] * UNIT_MM) for view in VIEWS]
	return {"body": body, "views": rendered, "unplaced": unplaced}
