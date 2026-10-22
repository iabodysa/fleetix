# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re
from functools import lru_cache

import frappe

VIEW_HEIGHT_MM = 30
MARKER_RADIUS_MM = 2.25
MARKER_STEP_MM = 5
MARKER_FONT_MM = 7 * 0.3528
LINE_MM = 0.75 * 0.3528
BOXES = {"side": (1, 3.5, 22, 17.5), "front": (1, 2, 22, 20)}
BODIES = {
	"Car": ("car", "car-front"),
	"Pickup Truck": ("truck", "car-front"),
	"Van": ("van", "bus-front"),
	"Bus": ("bus", "bus-front"),
	"Truck": ("truck", "bus-front"),
	"Motorbike": ("motorbike", None),
}
ANCHORS = {
	"Car": {
		"Front": (("front", 12, 13),),
		"Rear": (("right", 3, 13), ("left", 21, 13)),
		"Right Side": (("right", 12, 13),),
		"Left Side": (("left", 12, 13),),
		"Roof": (("right", 12, 8),),
	},
	"Motorbike": {
		"Front": (("right", 21, 11), ("left", 3, 11)),
		"Rear": (("right", 3, 11), ("left", 21, 11)),
		"Right Side": (("right", 12, 13),),
		"Left Side": (("left", 12, 13),),
	},
}
SHAPE = re.compile(r"<(?:path|circle|rect)\b[^>]*/>")
STROKE = re.compile(r'stroke-width="([0-9.]+)"')


@lru_cache(maxsize=None)
def _icon(name):
	path = frappe.get_app_path("fleetix", "public", "images", "vehicles", "outline", f"{name}.svg")
	with open(path) as svg:
		source = svg.read()
	return STROKE.search(source).group(1), "".join(SHAPE.findall(source))


def _unit(view):
	return BOXES["front" if view == "front" else "side"][3] / VIEW_HEIGHT_MM


def _view(icon, view, marks):
	x, y, w, h = BOXES["front" if view == "front" else "side"]
	unit = _unit(view)
	stroke, shapes = _icon(icon)
	if view == "left":
		shapes = f'<g transform="translate(24,0) scale(-1,1)">{shapes}</g>'
	drawn = "".join(
		f'<circle cx="{cx}" cy="{cy}" r="{MARKER_RADIUS_MM * unit:.3f}" fill="#FFFFFF" stroke="#000" stroke-width="{LINE_MM * unit:.3f}"/>'
		f'<text x="{cx}" y="{cy + MARKER_FONT_MM * unit * 0.36:.3f}" text-anchor="middle" font-family="Tajawal,sans-serif" font-weight="700" font-size="{MARKER_FONT_MM * unit:.3f}" fill="#000">{no}</text>'
		for no, cx, cy in marks
	)
	return (
		f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" width="{w / unit:.1f}mm" height="{VIEW_HEIGHT_MM}mm">'
		f'<g fill="none" stroke="#000" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{shapes}</g>'
		f"{drawn}</svg>"
	)


def vehicle_views(vehicle=None, damages=None):
	vehicle_type = frappe.db.get_value("Vehicle", vehicle, "vehicle_type") if vehicle else None
	body = (frappe.db.get_value("Vehicle Type", vehicle_type, "body_type") if vehicle_type else None) or "Car"
	side, front = BODIES.get(body, BODIES["Car"])
	anchors = ANCHORS.get(body, ANCHORS["Car"])
	views = ("left", "right") if front is None else ("left", "front", "right")
	marks = {view: [] for view in views}
	placed = {}
	unplaced = []
	for damage in damages or []:
		area = damage.get("area")
		if not area:
			continue
		spots = anchors.get(area)
		if not spots:
			unplaced.append((damage.get("no"), area))
			continue
		for view, cx, cy in spots:
			shift = placed.get((view, area), 0)
			placed[(view, area)] = shift + 1
			marks[view].append((damage.get("no"), round(cx + shift * MARKER_STEP_MM * _unit(view), 3), cy))
	rendered = [(view, _view(front if view == "front" else side, view, marks[view])) for view in views]
	return {"body": body, "views": rendered, "unplaced": unplaced}
