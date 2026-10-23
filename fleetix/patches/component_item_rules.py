import frappe

DEFAULTS = (
	("Oil", "Oil", "زيت محرك\nزيت مكينة\nengine oil\nmotor oil"),
	("Oil Filter", "Oil Filter", "فلتر زيت\noil filter"),
	("Front Tires", "Tires", "كفر\nإطار\nاطار\ntire\ntyre"),
	("Rear Tires", "Tires", "كفر\nإطار\nاطار\ntire\ntyre"),
	("Battery", "Battery", "بطارية\nbattery"),
)


def execute():
	settings = frappe.get_single("Fleetix Settings")
	if settings.component_items:
		return
	for component, group, keywords in DEFAULTS:
		settings.append(
			"component_items",
			{
				"component": component,
				"item_group": group if frappe.db.exists("Item Group", group) else None,
				"keywords": keywords,
			},
		)
	settings.save()
