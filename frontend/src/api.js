import call from "frappe-ui/src/utils/call.js"
import { __ } from "./translate.js"

const M = "fleetix.fleetix.api.maintenance."

export const api = {
	checklist: (maintenance, odometer) => call(M + "get_vehicle_checklist", { maintenance, odometer }),
	send: (args) => call(M + "send_for_approval", args),
	finish: (maintenance, final_check) => call(M + "finish_maintenance", { maintenance, final_check }),
	result: (maintenance) => call(M + "get_visit_result", { maintenance }),
	photos: (maintenance) => call(M + "get_photos", { maintenance }),
	photoLink: (maintenance) => call(M + "get_photo_link", { maintenance }),
	status: (maintenance) =>
		call("frappe.client.get_value", {
			doctype: "Maintenance",
			filters: maintenance,
			fieldname: ["status", "inspection", "docstatus"],
		}),
	login: (usr, pwd) => call("login", { usr, pwd }),
	logout: () => call("logout"),
}

export const QUEUE_METHOD = M + "get_due_queue"

export function errorText(error) {
	if (error instanceof TypeError && /fetch/i.test(error.message)) return __("No connection to the server")
	const parts = error && error.messages && error.messages.length ? error.messages : [error && error.message]
	return parts
		.filter(Boolean)
		.join(" ")
		.replace(/<[^>]+>/g, "")
}
