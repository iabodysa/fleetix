// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Accident Register"] = {
	filters: [
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
		{ fieldname: "deal", label: __("Deal"), fieldtype: "Link", options: "Deal" },
		{ fieldname: "firm", label: __("Firm"), fieldtype: "Link", options: "Firm" },
		{ fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nOpen\nClaimed\nClosed" },
	],
};
