import call from "frappe-ui/src/utils/call.js"
import { __ } from "./i18n/index.js"

const M = "fleetix.fleetix.api.maintenance."
const C = "fleetix.fleetix.api.customer_visit."

export const api = {
	checklist: (maintenance, odometer) => call(M + "get_vehicle_checklist", { maintenance, odometer }),
	send: (args) => call(M + "send_for_approval", args),
	finish: (maintenance, finalCheck, findings) =>
		call(M + "finish_maintenance", { maintenance, final_check: JSON.stringify(finalCheck), findings: JSON.stringify(findings) }),
	searchItems: (txt, stock = 1) => call("frappe.desk.search.search_link", { doctype: "Item", txt, filters: { disabled: 0, is_stock_item: stock }, page_length: 20 }),
	walkinSetup: () => call(C + "get_walkin_setup"),
	findCustomer: (mobile) => call(C + "find_customer", { mobile }),
	itemRates: (items) => call(C + "get_item_rates", { items: JSON.stringify(items) }),
	plateFindings: (plate) => call(C + "get_plate_findings", { plate }),
	finishWalkin: (args) => call(C + "finish_customer_visit", args),
	act: (maintenance, action) => call("frappe.model.workflow.apply_workflow", { doc: { doctype: "Maintenance", name: maintenance }, action }),
	result: (maintenance) => call(M + "get_visit_result", { maintenance }),
	photos: (maintenance) => call(M + "get_photos", { maintenance }),
	photoLink: (maintenance) => call(M + "get_photo_link", { maintenance }),
	trackCard: (maintenance) => call("fleetix.fleetix.api.track.get_track_card", { maintenance }),
	diagram: (maintenance) => call(M + "get_vehicle_diagram", { maintenance }),
	printSamples: () => call(M + "get_print_samples"),
	saveMarks: (maintenance, damages) => call(M + "save_damage_marks", { maintenance, damages: JSON.stringify(damages) }),
	findVehicles: (plate, start) => call(M + "find_vehicles", { plate, start }),
	openVehicle: (vehicle) => call(M + "open_vehicle_visit", { vehicle }),
	status: (maintenance) =>
		call("frappe.client.get_value", {
			doctype: "Maintenance",
			filters: maintenance,
			fieldname: ["status", "inspection", "docstatus"],
		}),
	setLanguage: (lang) => call(M + "set_language", { lang }),
	login: (usr, pwd) => call("login", { usr, pwd }),
	logout: () => call("logout"),
	boot: () => call(M + "get_boot"),
}

export const QUEUE_METHOD = M + "get_due_queue"

const LONG_MESSAGE = 160

function shortText(error) {
	if (error && error.exc_type === "NegativeStockError") return __("Not enough stock for this item. Tell the store.")
	return ""
}

export function errorText(error) {
	if (error instanceof TypeError && /fetch/i.test(error.message)) return { text: __("No connection to the server"), detail: "" }
	const parts = error && error.messages && error.messages.length ? error.messages : [error && error.message]
	const raw = parts.filter(Boolean).join(" ")
	const plain = raw.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim()
	const short = shortText(error)
	if (short) return { text: short, detail: plain }
	if (/<[^>]+>/.test(raw) || plain.length > LONG_MESSAGE) return { text: __("This step could not be saved. Show the details to your supervisor."), detail: plain }
	return { text: plain, detail: "" }
}
