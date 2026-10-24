// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

frappe.ready(() => {
	const form = frappe.web_form;
	const attachments = ["id_image", "license_image", "photo"];
	const token = frappe
		.call({ method: "fleetix.fleetix.api.driver_registration.start", type: "POST" })
		.then((r) => {
			form.set_value("upload_token", r.message);
			return r.message;
		});
	attachments.forEach((fieldname) => {
		const field = form.fields_dict[fieldname];
		if (!field) {
			return;
		}
		field.$input.prop("readonly", true).addClass("hidden");
		const picker = $('<input type="file" accept=".jpg,.jpeg,.png,.pdf" class="form-control">');
		const status = $('<div class="text-muted small"></div>');
		field.$input.after(picker, status);
		picker.on("change", async () => {
			const file = picker[0].files[0];
			form.set_value(fieldname, "");
			if (!file) {
				return;
			}
			const data = new FormData();
			data.append("token", await token);
			data.append("fieldname", fieldname);
			data.append("company_website", form.get_value("company_website") || "");
			data.append("file", file);
			status.text(__("Uploading..."));
			const response = await fetch(
				"/api/method/fleetix.fleetix.api.driver_registration.upload",
				{ method: "POST", body: data, headers: { Accept: "application/json" } },
			);
			const result = await response.json();
			if (response.ok) {
				form.set_value(fieldname, result.message);
				status.text(__("Uploaded"));
			} else {
				picker.val("");
				status.text(__("The file must be a JPG, PNG or PDF file of 5 MB or smaller"));
			}
		});
	});
});
