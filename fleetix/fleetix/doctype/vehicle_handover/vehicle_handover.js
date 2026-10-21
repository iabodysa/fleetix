// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Handover", {
	setup(frm) {
		frm.set_query("inspection", () => ({
			filters: { vehicle: frm.doc.vehicle, docstatus: ["<", 2] },
		}));
	},
	refresh(frm) {
		if (frm.is_new()) {
			frm.trigger("vehicle");
		}
	},
	vehicle(frm) {
		if (!frm.doc.vehicle || frm.doc.inspection || frm.doc.docstatus !== 0) {
			return;
		}
		frappe.db
			.get_list("Vehicle Inspection", {
				filters: { vehicle: frm.doc.vehicle },
				fields: ["name"],
				order_by: "inspection_datetime desc",
				limit: 1,
			})
			.then((rows) => {
				if (rows.length && !frm.doc.inspection) {
					frm.set_value("inspection", rows[0].name);
				}
			});
	},
});
