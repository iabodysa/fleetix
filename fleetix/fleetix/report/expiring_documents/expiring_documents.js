// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Expiring Documents"] = {
	filters: [
		{ fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer" },
		{ fieldname: "days", label: __("Within Days"), fieldtype: "Int", default: 30 },
		{ fieldname: "show_missing", label: __("Show Missing"), fieldtype: "Check", default: 1 },
	],
};
