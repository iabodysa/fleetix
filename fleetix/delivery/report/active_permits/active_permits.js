// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Active Permits"] = {
	filters: [
		{ fieldname: "deal", label: __("Deal"), fieldtype: "Link", options: "Deal" },
		{ fieldname: "firm", label: __("Firm"), fieldtype: "Link", options: "Firm" },
		{ fieldname: "staff", label: __("Employee or Delegate"), fieldtype: "Link", options: "Staff" },
	],
};
