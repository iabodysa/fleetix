import { showStepOnCustomerDisplay } from "../native.js"

export const CUSTOMER_KEY = "fleetix.maintenance.customer"

function keep(view) {
	try {
		localStorage.setItem(CUSTOMER_KEY, JSON.stringify(view))
	} catch (e) {
		return false
	}
	return true
}

export function publishToCustomer(view) {
	keep(view)
	showStepOnCustomerDisplay(view.plate, view.status)
}

export function readCustomerView() {
	try {
		return JSON.parse(localStorage.getItem(CUSTOMER_KEY) || "null")
	} catch (e) {
		return null
	}
}
