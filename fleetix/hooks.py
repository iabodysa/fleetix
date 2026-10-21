app_name = "fleetix"
app_title = "Fleetix"
app_publisher = "Ittihad"
app_description = "Vehicle rental management for Etihad"
app_email = "afm@afmcoltd.com"
app_license = "mit"

required_apps = ["frappe", "erpnext"]

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
	{"dt": "Custom Field", "filters": [["module", "=", "Master"]]},
	{"dt": "Property Setter", "filters": [["module", "=", "Master"]]},
	{"dt": "Workflow", "filters": [["name", "in", ["Vehicle Request", "Vehicle Handover", "Maintenance"]]]},
	{
		"dt": "Workflow State",
		"filters": [
			[
				"name",
				"in",
				[
					"Assigned",
					"Cancelled",
					"Completed",
					"Documentation and Signatures",
					"Driver Arrived",
					"Due Alert",
					"Final Check",
					"Full Inspection",
					"Inspection",
					"New",
					"Pending Assignment",
					"Pending Documentation",
					"Pending Inspection",
					"Pending Vehicle Selection",
					"Requested",
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
					"Complete",
					"Document",
					"Finish Service",
					"Inspect",
					"Select Vehicle",
					"Start Inspection",
					"Start Service",
					"Submit",
				],
			]
		],
	},
]

override_doctype_class = {"Vehicle": "fleetix.master.vehicle.VehicleService"}

after_sync = ["fleetix.master.permissions.grant_core_permissions"]
after_migrate = ["fleetix.master.permissions.grant_core_permissions"]
before_uninstall = ["fleetix.master.permissions.revoke_core_permissions"]

scheduler_events = {"daily": ["fleetix.operations.doctype.maintenance.maintenance.create_due_alerts"]}
