app_name = "ijar"
app_title = "Ijar"
app_publisher = "Ittihad"
app_description = "Vehicle leasing operations for Ittihad"
app_email = "afm@afmcoltd.com"
app_license = "mit"

required_apps = ["frappe"]

fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", ["Ijar Manager", "Ijar Fleet", "Ijar Finance", "Ijar Buyer"]]],
	}
]
