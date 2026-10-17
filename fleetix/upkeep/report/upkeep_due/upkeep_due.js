// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Upkeep Due"] = {
	filters: [
		{ fieldname: "due_before", label: __("Due Before"), fieldtype: "Date" },
		{ fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nDue\nOverdue\nOpen\nIn Workshop" },
	],
};
