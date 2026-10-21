# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe

from fleetix.operations.fleet_state import BOARD_ROLES, STATES, WAITING_STEPS, classify, count


@frappe.whitelist()
def get_city_grid():
	frappe.only_for(BOARD_ROLES)
	rows = classify()
	regions = dict(frappe.get_all("City", fields=["name", "region"], as_list=True))
	types = (
		dict(
			frappe.get_all(
				"Vehicle",
				filters={"name": ("in", [r.vehicle for r in rows])},
				fields=["name", "vehicle_type"],
				as_list=True,
			)
		)
		if rows
		else {}
	)
	project_city = dict(frappe.get_all("Project", fields=["name", "city"], as_list=True))
	waiting = frappe.get_all(
		"Vehicle Request",
		filters={"workflow_state": ("in", WAITING_STEPS)},
		fields=["name", "project", "required_date", "requested_vehicle_type", "workflow_state"],
		order_by="required_date asc",
	)

	cities = {}
	for row in rows:
		city = cities.setdefault(
			row.city or "", {"city": row.city or "", "vehicles": [], "waiting": [], "matches": []}
		)
		city["vehicles"].append({"vehicle": row.vehicle, "plate": row.plate, "state": row.state})
	for request in waiting:
		city_name = project_city.get(request.project) or ""
		cities.setdefault(city_name, {"city": city_name, "vehicles": [], "waiting": [], "matches": []})
		cities[city_name]["waiting"].append(request)

	idle = [row for row in rows if row.state == "black"]
	for city in cities.values():
		pool = [row for row in idle if (row.city or "") == city["city"]]
		for request in city["waiting"]:
			wanted = request.requested_vehicle_type
			pick = next((row for row in pool if not wanted or types.get(row.vehicle) == wanted), None)
			if pick:
				pool.remove(pick)
				city["matches"].append(
					{
						"request": request.name,
						"vehicle": pick.vehicle,
						"plate": pick.plate,
						"idle_days": pick.idle_days,
					}
				)
		city["region"] = regions.get(city["city"]) or "Other"
		city["counts"] = count(frappe._dict(state=v["state"]) for v in city["vehicles"])
		total = len(city["vehicles"]) or 1
		city["pressure"] = round((total - city["counts"]["green"]) / total, 3)
		city["vehicles"].sort(key=lambda v: (STATES.index(v["state"]), v["plate"]))
	ranked = sorted(cities.values(), key=lambda c: (-c["pressure"], -len(c["waiting"]), c["city"]))
	return {"cities": ranked, "counts": count(rows)}
