frappe.listview_settings["Vehicle"] = {
	add_fields: ["data_incomplete", "status"],
	get_indicator(doc) {
		if (doc.data_incomplete) {
			return [__("Missing Data"), "red", "data_incomplete,=,1"];
		}
	},
};
