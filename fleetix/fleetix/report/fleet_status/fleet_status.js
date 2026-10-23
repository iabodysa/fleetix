// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Fleet Status"] = {
	filters: [
		{ fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer" },
		{ fieldname: "project", label: __("Project"), fieldtype: "Link", options: "Project" },
		{ fieldname: "city", label: __("City"), fieldtype: "Link", options: "City" },
		{
			fieldname: "vehicle_type",
			label: __("Vehicle Type"),
			fieldtype: "Link",
			options: "Vehicle Type",
		},
	],
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "state" && data && data.state_color) {
			const pill = { red: "red", black: "darkgrey", gray: "gray", suspended: "orange", green: "green" }[
				data.state_color
			];
			return `<span class="indicator-pill ${pill}">${value}</span>`;
		}
		return value;
	},
};
