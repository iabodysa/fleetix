// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Inspection", {
	vehicle(frm) {
		if (!frm.doc.vehicle || (frm.doc.checklist || []).length) {
			return;
		}
		frappe
			.call(
				"fleetix.fleetix.api.vehicle_inspection.last_checklist_items",
				{ vehicle: frm.doc.vehicle }
			)
			.then((r) => {
				if ((frm.doc.checklist || []).length) {
					return;
				}
				(r.message || []).forEach((item) => frm.add_child("checklist", { item }));
				frm.refresh_field("checklist");
			});
	},
});
