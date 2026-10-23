frappe.ui.form.on("Vehicle", {
	refresh(frm) {
		if (!frm.doc.data_incomplete) return;
		const labels = (frm.doc.missing_fields || "").split(", ").map((label) => __(label));
		frm.set_intro(__("Missing Data: {0}", [labels.join(", ")]), "red");
	},
});
