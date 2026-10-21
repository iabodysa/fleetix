// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Claim", {
	source_reference(frm) {
		if (!frm.doc.claim_type || !frm.doc.source_reference) {
			return;
		}
		frappe
			.call("fleetix.fleetix.api.project_claim.get_source_values", {
				claim_type: frm.doc.claim_type,
				source_reference: frm.doc.source_reference,
			})
			.then((r) => frm.set_value(r.message));
	},
});
