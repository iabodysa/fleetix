frappe.ui.form.on("Vehicle", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Vehicle Label"), () =>
				frappe.utils.print(frm.doctype, frm.docname, "Thermal Vehicle Label", "")
			);
		}
		if (!frm.doc.data_incomplete) return;
		const labels = (frm.doc.missing_fields || "").split(", ").map((label) => __(label));
		frm.set_intro(__("Missing Data: {0}", [labels.join(", ")]), "red");
	},
});
