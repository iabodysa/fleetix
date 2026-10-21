// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Expiring Documents"] = {
	filters: [
		{ fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company" },
		{ fieldname: "days", label: __("Within Days"), fieldtype: "Int", default: 30 },
		{ fieldname: "show_missing", label: __("Show Missing"), fieldtype: "Check", default: 1 },
	],
};
