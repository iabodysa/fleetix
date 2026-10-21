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
	{"dt": "Role Profile", "filters": [["name", "=", "Fleetix Accountant"]]},
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

override_doctype_class = {"Vehicle": "fleetix.fleetix.vehicle.VehicleService"}

jinja = {"methods": ["fleetix.fleetix.document_qr.document_qr"]}

website_route_rules = [{"from_route": "/maintenance/<path:app_path>", "to_route": "maintenance"}]

after_install = ["fleetix.fleetix.branding.set_navbar_logo", "frappe.clear_cache"]
after_sync = ["fleetix.fleetix.permissions.grant_core_permissions"]
after_migrate = [
	"fleetix.fleetix.permissions.grant_core_permissions",
	"fleetix.fleetix.branding.set_navbar_logo",
]
before_uninstall = ["fleetix.fleetix.permissions.revoke_core_permissions"]

scheduler_events = {"daily": ["fleetix.fleetix.doctype.maintenance.maintenance.create_due_alerts"]}
