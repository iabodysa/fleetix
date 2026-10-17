app_name = "fleetix"
app_title = "Fleetix"
app_publisher = "Ittihad"
app_description = "Vehicle leasing operations for Ittihad"
app_email = "afm@afmcoltd.com"
app_license = "mit"

required_apps = ["frappe"]

fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", ["Fleetix Manager", "Fleetix Fleet", "Fleetix Finance", "Fleetix Buyer"]]],
	}
]
