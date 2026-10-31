import { __ } from "./i18n.js"

const M = "/api/method/fleetix.fleetix.api.store."
const TIMEOUT_MS = 30000

function serverMessage(data) {
	try {
		const messages = JSON.parse(data._server_messages || "[]").map((row) => JSON.parse(row).message)
		if (messages.length) return messages.join(" ")
	} catch (e) {
		return data.exception || ""
	}
	return data.exception || data.message || ""
}

async function send(path, body) {
	const controller = window.AbortController ? new AbortController() : null
	const timer = controller && setTimeout(() => controller.abort(), TIMEOUT_MS)
	try {
		const response = await fetch(path, {
			method: "POST",
			credentials: "same-origin",
			headers: { Accept: "application/json", "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.csrf_token || "" },
			body: JSON.stringify(body || {}),
			signal: controller ? controller.signal : undefined,
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
	pending: (start) => send(M + "pending_issues", { start }),
	approve: (stock_entry) => send(M + "approve_issue", { stock_entry }),
	scan: (code) => send(M + "scan", { code }),
	suggest: (txt, model) => send(M + "suggest_items", { txt, model }),
	receive: (args) => send(M + "receive", args),
	newPart: (args) => send(M + "new_part", args),
	setLanguage: (lang) => send("/api/method/fleetix.fleetix.api.gate.set_language", { lang }),
	login: (usr, pwd) => send("/api/method/login", { usr, pwd }),
	logout: () => send("/api/method/logout", {}),
}

export function errorText(error) {
	return String((error && error.message) || error || "").replace(/<[^>]+>/g, "")
}
