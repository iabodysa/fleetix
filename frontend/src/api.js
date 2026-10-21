import call from "frappe-ui/src/utils/call.js"

const M = "fleetix.operations.api.maintenance."

export const api = {
	checklist: (maintenance, odometer) => call(M + "get_vehicle_checklist", { maintenance, odometer }),
	send: (args) => call(M + "send_for_approval", args),
	finish: (maintenance, final_check) => call(M + "finish_maintenance", { maintenance, final_check }),
	result: (maintenance) => call(M + "get_visit_result", { maintenance }),
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
	const parts = error && error.messages && error.messages.length ? error.messages : [error && error.message]
	return parts
		.filter(Boolean)
		.join(" ")
		.replace(/<[^>]+>/g, "")
}

function downscale(file, max) {
	return new Promise((resolve, reject) => {
		const reader = new FileReader()
		reader.onerror = reject
		reader.onload = () => {
			const image = new Image()
			image.onerror = reject
			image.onload = () => {
				const scale = Math.min(1, max / Math.max(image.width, image.height))
				const canvas = document.createElement("canvas")
				canvas.width = Math.round(image.width * scale)
				canvas.height = Math.round(image.height * scale)
				canvas.getContext("2d").drawImage(image, 0, 0, canvas.width, canvas.height)
				canvas.toBlob((blob) => resolve({ blob, preview: canvas.toDataURL("image/jpeg", 0.5) }), "image/jpeg", 0.85)
			}
			image.src = reader.result
		}
		reader.readAsDataURL(file)
	})
}

export async function uploadPhoto(file, maintenance, caption) {
	const { blob, preview } = await downscale(file, 1600)
	const form = new FormData()
	form.append("file", blob, caption + "-" + Date.now() + ".jpg")
	form.append("is_private", "1")
	form.append("doctype", "Maintenance")
	form.append("docname", maintenance)
	const response = await fetch("/api/method/upload_file", {
		method: "POST",
		body: form,
		headers: { Accept: "application/json", "X-Frappe-CSRF-Token": window.csrf_token },
	})
	const data = await response.json()
	if (!response.ok) {
		const messages = data._server_messages ? JSON.parse(data._server_messages).map((m) => JSON.parse(m).message) : []
		throw { messages: messages.length ? messages : [data.exc_type || response.statusText] }
	}
	return { file_url: data.message.file_url, preview }
}
