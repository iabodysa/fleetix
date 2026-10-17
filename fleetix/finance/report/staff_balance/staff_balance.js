// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Staff Balance"] = {
	filters: [
		{ fieldname: "staff", label: __("Employee or Delegate"), fieldtype: "Link", options: "Staff" },
		{ fieldname: "kind", label: __("Kind"), fieldtype: "Select", options: "\nEmployee\nDelegate" },
	],
};
