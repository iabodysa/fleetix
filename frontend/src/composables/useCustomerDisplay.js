import { api } from "../api.js"
import { hasCustomerDisplay, showStepOnCustomerDisplay } from "../native.js"

export const CUSTOMER_KEY = "fleetix.maintenance.customer"

let card = { maintenance: null, value: null }
let latest = 0

function keep(view) {
	try {
		localStorage.setItem(CUSTOMER_KEY, JSON.stringify(view))
	} catch (e) {
		return false
	}
	return true
}

async function trackCard(maintenance) {
	if (card.maintenance === maintenance) return card.value
	const value = await api.trackCard(maintenance).catch(() => null)
	if (value) card = { maintenance, value }
	return value
}

export async function publishToCustomer(view) {
	keep(view)
	const turn = ++latest
	const value = view.plate && view.maintenance && hasCustomerDisplay() ? await trackCard(view.maintenance) : null
	if (turn === latest) showStepOnCustomerDisplay(view.plate, view.status, value)
}

export function readCustomerView() {
	try {
		return JSON.parse(localStorage.getItem(CUSTOMER_KEY) || "null")
	} catch (e) {
		return null
	}
}
