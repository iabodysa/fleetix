// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.ui.form.on("Driver Registration", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.driver) {
			return;
		}
		frm.add_custom_button(__("Create Driver"), () =>
			frm.call("create_driver").then((r) => frappe.set_route("Form", "Driver", r.message))
		);
	},
});
