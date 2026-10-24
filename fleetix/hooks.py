app_name = "fleetix"
app_title = "Fleetix"
app_publisher = "Ittihad"
app_description = "Vehicle rental management for Etihad"
app_email = "afm@afmcoltd.com"
app_license = "mit"

required_apps = ["frappe", "erpnext"]

home_page = "index"

add_to_apps_screen = [
	{
		"name": "fleetix",
		"logo": "/assets/fleetix/images/fleetix-logo.svg",
		"title": "Fleetix",
		"route": "/app/fleetix",
	}
]

fixtures = [
	{
		"dt": "Role",
		"filters": [
			[
				"name",
				"in",
				[
					"Project Supervisor",
					"Rental Manager",
					"Movement Supervisor",
					"Maintenance Supervisor",
					"Accountant",
					"Driver",
				],
			]
		],
	},
	{"dt": "Role Profile", "filters": [["name", "in", ["Fleetix Accountant", "Fleetix Rental Manager"]]]},
	{"dt": "Module Profile", "filters": [["name", "in", ["Fleetix Field", "Fleetix Finance"]]]},
	{"dt": "Custom Field", "filters": [["module", "=", "Fleetix"]]},
	{"dt": "Property Setter", "filters": [["module", "=", "Fleetix"]]},
	{
		"dt": "Workflow",
		"filters": [
			[
				"name",
				"in",
				[
					"Vehicle Request",
					"Vehicle Handover",
					"Maintenance",
					"Accident",
					"Damage",
					"Project Claim",
				],
			]
		],
	},
	{
		"dt": "Workflow State",
		"filters": [
			[
				"name",
				"in",
				[
					"Assigned",
					"Cancelled",
					"Charged to Driver",
					"Claimed",
					"Claimed from Project",
					"Closed",
					"Completed",
					"Cost Estimated",
					"Detected",
					"Documentation and Signatures",
					"Documented",
					"Draft",
					"Driver Arrived",
					"Due Alert",
					"Final Check",
					"Full Inspection",
					"Inspection",
					"New",
					"Paid",
					"Pending Assignment",
					"Pending Documentation",
					"Pending Inspection",
					"Pending Vehicle Selection",
					"Reported",
					"Requested",
					"Responsibility Set",
					"Sent to Project",
					"Service",
				],
			]
		],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [
			[
				"name",
				"in",
				[
					"Arrive",
					"Assign",
					"Cancel",
					"Charge",
					"Claim",
					"Close",
					"Complete",
					"Document",
					"Estimate Cost",
					"Finish Service",
					"Inspect",
					"Pay",
					"Select Vehicle",
					"Send",
					"Set Responsibility",
					"Start Inspection",
					"Start Service",
					"Submit",
				],
			]
		],
	},
	{
		"dt": "Item Group",
		"filters": [
			[
				"name",
				"in",
				[
					"Oil",
					"Oil Filter",
					"Tires",
					"Battery",
					"Spare Parts",
				],
			]
		],
	},
]

override_doctype_class = {
	"Driver": "fleetix.fleetix.driver.DriverService",
	"Vehicle": "fleetix.fleetix.vehicle.VehicleService",
}

app_include_js = "/assets/fleetix/js/vehicle_type.js"

doctype_js = {"Vehicle": "public/js/vehicle.js"}
doctype_list_js = {"Driver": "public/js/driver_list.js", "Vehicle": "public/js/vehicle_list.js"}

override_doctype_dashboards = {
	"Customer": "fleetix.fleetix.dashboard_overrides.get_dashboard_for_customer",
	"Driver": "fleetix.fleetix.dashboard_overrides.get_dashboard_for_driver",
	"Project": "fleetix.fleetix.dashboard_overrides.get_dashboard_for_project",
	"Vehicle": "fleetix.fleetix.dashboard_overrides.get_dashboard_for_vehicle",
	"Sales Invoice": "fleetix.fleetix.dashboard_overrides.get_dashboard_for_sales_invoice",
}

jinja = {
	"methods": [
		"fleetix.fleetix.document_qr.document_qr",
		"fleetix.fleetix.vehicle_diagram.vehicle_views",
		"fleetix.fleetix.plate.saudi_plate",
		"fleetix.fleetix.doctype.maintenance.maintenance.next_due",
		"fleetix.fleetix.maintenance_invoice.maintenance_invoice",
		"fleetix.fleetix.units.unit_label",
	]
}

website_route_rules = [
	{"from_route": "/maintenance/photos/<visit>", "to_route": "maintenance_photos"},
	{"from_route": "/maintenance/track/<visit>", "to_route": "maintenance_track"},
	{"from_route": "/maintenance/sign/<visit>", "to_route": "maintenance_sign"},
	{"from_route": "/maintenance/<path:app_path>", "to_route": "maintenance"},
	{"from_route": "/gate/<path:app_path>", "to_route": "gate"},
]

after_request = ["fleetix.fleetix.kiosk.revalidate_kiosk_pages"]
after_install = ["fleetix.fleetix.branding.set_navbar_logo", "frappe.clear_cache"]
after_sync = ["fleetix.fleetix.permissions.grant_core_permissions"]
after_migrate = [
	"fleetix.fleetix.permissions.grant_core_permissions",
	"fleetix.fleetix.branding.set_navbar_logo",
]
before_uninstall = ["fleetix.fleetix.permissions.revoke_core_permissions"]

scheduler_events = {"daily": ["fleetix.fleetix.doctype.maintenance.maintenance.create_due_alerts"]}
