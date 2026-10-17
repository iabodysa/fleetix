// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Fleet Status"] = {
	filters: [
		{ fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nAvailable\nLeased\nRepair\nAccident\nStopped\nSold" },
		{ fieldname: "firm", label: __("Firm"), fieldtype: "Link", options: "Firm" },
		{ fieldname: "deal", label: __("Deal"), fieldtype: "Link", options: "Deal" },
	],
};
