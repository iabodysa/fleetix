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
]

extend_doctype_class = {"Vehicle": ["fleetix.master.vehicle.VehicleService"]}

after_sync = ["fleetix.master.permissions.grant_core_permissions"]
after_migrate = ["fleetix.master.permissions.grant_core_permissions"]
before_uninstall = ["fleetix.master.permissions.revoke_core_permissions"]
