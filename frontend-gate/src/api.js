import { __ } from "./i18n.js"

const M = "fleetix.fleetix.api.gate."
const TIMEOUT_MS = 30000

function headers(json) {
	const out = { Accept: "application/json", "X-Frappe-CSRF-Token": window.csrf_token || "" }
	if (json) out["Content-Type"] = "application/json"
	return out
}

function serverMessage(data) {
	try {
		const messages = JSON.parse(data._server_messages || "[]").map((row) => JSON.parse(row).message)
		if (messages.length) return messages.join(" ")
	} catch (e) {
		return data.exception || ""
	}
	return data.exception || data.message || ""
}

async function send(path, body, json) {
	const controller = new AbortController()
	const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)
	try {
		const response = await fetch(path, {
			method: "POST",
			credentials: "same-origin",
			headers: headers(json),
			body: json ? JSON.stringify(body || {}) : body,
			signal: controller.signal,
		})
		const data = await response.json().catch(() => ({}))
		if (!response.ok) throw new Error(serverMessage(data) || __("The server returned an error"))
		return data.message
	} catch (error) {
		if (error.name === "AbortError" || error instanceof TypeError) throw new Error(__("No connection to the server"))
		throw error
	} finally {
		clearTimeout(timer)
	}
}

export const api = {
	find: (code) => send("/api/method/" + M + "find_vehicle", { code }, true),
	record: (vehicle, odometer, route) => send("/api/method/" + M + "record_entry", { vehicle, odometer, route }, true),
	setLanguage: (lang) => send("/api/method/" + M + "set_language", { lang }, true),
	upload(doctype, name, blob, filename) {
		const form = new FormData()
		form.append("doctype", doctype)
		form.append("name", name)
		form.append("file", blob, filename)
		return send("/api/method/" + M + "upload_photo", form, false)
	},
	login: (usr, pwd) => send("/api/method/login", { usr, pwd }, true),
	logout: () => send("/api/method/logout", {}, true),
}

export function errorText(error) {
	return String((error && error.message) || error || "").replace(/<[^>]+>/g, "")
}
