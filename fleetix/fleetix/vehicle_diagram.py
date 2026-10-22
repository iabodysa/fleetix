# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re
from functools import lru_cache

import frappe

DAMAGE_FILL = "#F5A898"
VIEW_ORDER = ("left", "front", "right", "rear")
VIEW = re.compile(r'<svg id="[a-z]+-(left|right|front|rear)" [^>]*?viewBox="([^"]+)">(.*?)</svg>', re.S)


@lru_cache(maxsize=None)
def _views(body):
	path = frappe.get_app_path("fleetix", "public", "images", "vehicles", f"{body}.svg")
	with open(path) as svg:
		return {view: (box, inner) for view, box, inner in VIEW.findall(svg.read())}


def vehicle_views(vehicle=None, areas=None):
	vehicle_type = frappe.db.get_value("Vehicle", vehicle, "vehicle_type") if vehicle else None
	body = (frappe.db.get_value("Vehicle Type", vehicle_type, "body_type") if vehicle_type else None) or "Car"
	views = _views(body.split()[0].lower())
	hit = {area.split()[0].lower() for area in areas or [] if area}
	rendered = []
	for view in VIEW_ORDER:
		box, inner = views[view]
		for area in hit:
			inner = inner.replace(f'data-area="{area}"', f'data-area="{area}" fill="{DAMAGE_FILL}"')
		rendered.append((view, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box}" preserveAspectRatio="xMidYMid meet">{inner}</svg>'))
	return {"body": body, "views": rendered}
