// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.query_reports["Rent Due"] = {
	filters: [
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date", reqd: 1, default: frappe.datetime.month_start() },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date", reqd: 1, default: frappe.datetime.month_end() },
		{ fieldname: "client", label: __("Client"), fieldtype: "Link", options: "Client" },
		{ fieldname: "deal", label: __("Deal"), fieldtype: "Link", options: "Deal" },
		{ fieldname: "deal_type", label: __("Deal Type"), fieldtype: "Link", options: "Deal Type" },
	],
};
