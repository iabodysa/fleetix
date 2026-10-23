// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Request", {
	refresh(frm) {
		fleetix.vehicle_type.show(frm, "selected_vehicle");
	},
	selected_vehicle(frm) {
		fleetix.vehicle_type.show(frm, "selected_vehicle");
	},
});
