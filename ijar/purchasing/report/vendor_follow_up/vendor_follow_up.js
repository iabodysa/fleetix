// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Vendor Follow-up"] = {
	filters: [
		{ fieldname: "vendor", label: __("Vendor"), fieldtype: "Link", options: "Vendor" },
		{ fieldname: "status", label: __("Status"), fieldtype: "Select", options: "\nDraft\nApproved\nOrdered\nReceived\nRejected" },
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
	],
};
