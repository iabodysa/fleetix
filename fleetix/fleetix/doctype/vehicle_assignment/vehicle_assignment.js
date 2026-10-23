// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Assignment", {
	refresh(frm) {
		fleetix.vehicle_type.show(frm, "vehicle");
	},
	vehicle(frm) {
		fleetix.vehicle_type.show(frm, "vehicle");
	},
	project(frm) {
		if (!frm.doc.project || frm.doc.docstatus !== 0) {
			return;
		}
		frm.call("set_default_intervals");
	},
});
