// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.listview_settings["Project Rental Charge"] = {
	onload(listview) {
		if (!frappe.model.can_create("Sales Invoice")) return;
		listview.page.add_inner_button(__("Create Monthly Invoice"), () => {
			frappe.prompt(
				[
					{
						fieldname: "customer",
						label: __("Customer"),
						fieldtype: "Link",
						options: "Customer",
						reqd: 1,
					},
					{
						fieldname: "month",
						label: __("Month"),
						fieldtype: "Date",
						reqd: 1,
						default: frappe.datetime.month_start(),
					},
				],
				(values) =>
					frappe
						.call({
							method: "fleetix.fleetix.api.billing.create_monthly_invoice",
							args: values,
							freeze: true,
						})
						.then((r) => frappe.set_route("Form", "Sales Invoice", r.message)),
				__("Create Monthly Invoice")
			);
		});
	},
};
