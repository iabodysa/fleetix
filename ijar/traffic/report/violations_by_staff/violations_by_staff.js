// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Violations by Staff"] = {
	filters: [
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
		{ fieldname: "deal", label: __("Deal"), fieldtype: "Link", options: "Deal" },
		{ fieldname: "staff", label: __("Employee or Delegate"), fieldtype: "Link", options: "Staff" },
	],
};
