// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.ui.form.on("Insurance Claim", {
	refresh(frm) {
		fleetix.vehicle_type.show(frm, "vehicle");
	},
	vehicle(frm) {
		fleetix.vehicle_type.show(frm, "vehicle");
	},
});
