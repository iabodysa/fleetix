// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.provide("fleetix.vehicle_type");

Object.assign(fleetix.vehicle_type, {
	types: {},

	show(frm, fieldname) {
		const vehicle = frm.doc[fieldname];
		if (!vehicle || !frappe.model.can_read("Vehicle")) {
			frm.set_df_property(fieldname, "description", "");
			return;
		}
		frappe.db.get_value("Vehicle", vehicle, "vehicle_type").then((r) => {
			if (frm.doc[fieldname] === vehicle) {
				frm.set_df_property(fieldname, "description", r.message?.vehicle_type || "");
			}
		});
	},

	list_settings(doctype, fieldname) {
		const types = this.types;
		return {
			formatters: {
				[fieldname](value) {
					const label = types[value] ? `${value} · ${types[value]}` : value;
					if (frappe.get_meta(doctype).title_field === fieldname) {
						return label;
					}
					const escaped = frappe.utils.escape_html(value);
					const text = frappe.utils.escape_html(label);
					return `<a class="filterable ellipsis" data-filter="${fieldname},=,${escaped}">${text}</a>`;
				},
			},
			refresh(listview) {
				const missing = [...new Set(listview.data.map((d) => d[fieldname]))].filter(
					(v) => v && !(v in types)
				);
				if (!missing.length || !frappe.model.can_read("Vehicle")) {
					return;
				}
				missing.forEach((v) => (types[v] = ""));
				frappe.db
					.get_list("Vehicle", {
						filters: { name: ["in", missing] },
						fields: ["name", "vehicle_type"],
						limit: missing.length,
					})
					.then((rows) => {
						rows.forEach((r) => (types[r.name] = r.vehicle_type || ""));
						listview.render();
					});
			},
		};
	},
});
