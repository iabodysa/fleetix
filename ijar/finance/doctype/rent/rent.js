// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rent", {
	refresh(frm) {
		if (frm.doc.docstatus !== 0) return;
		frm.add_custom_button(__("Get Permits"), () => {
			frappe
				.call("ijar.finance.api.rent.get_permits", {
					deal: frm.doc.deal,
					from_date: frm.doc.from_date,
					to_date: frm.doc.to_date,
				})
				.then((r) => {
					frm.clear_table("lines");
					(r.message || []).forEach((row) => frm.add_child("lines", row));
					frm.refresh_field("lines");
				});
		});
	},
});
