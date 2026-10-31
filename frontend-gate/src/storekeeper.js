import { reactive } from "vue"
import { api } from "./api.js"

const PREVIOUS = { approvals: "hub", parts: "hub", receive: "hub", approval: "approvals", match: "receive", newPart: "match" }

function emptyReceipt() {
	return { item: null, qty: 0, code: "", serials: [] }
}

export const desk = reactive({
	view: null,
	issue: null,
	receipt: emptyReceipt(),
	unknown: null,
	notice: "",
	models: [],
	groups: [],
	booted: false,
})

export function show(view) {
	desk.view = view
}

export function resetReceipt() {
	desk.receipt = emptyReceipt()
	desk.unknown = null
}

function loadBoot() {
	if (desk.booted) return
	api.storeBoot().then((found) => Object.assign(desk, { models: found.models || [], groups: found.groups || [], booted: true }), () => null)
}

export function openStore(view) {
	desk.issue = null
	desk.notice = ""
	if (view === "receive") {
		resetReceipt()
		loadBoot()
	}
	show(view)
}

export function storeBack() {
	if (!desk.view) return false
	const previous = PREVIOUS[desk.view]
	if (previous) {
		show(previous)
		return true
	}
	if (!window.frappe.boot.is_worker) return false
	show(null)
	return true
}

function startReceipt(item, code) {
	desk.receipt = { item, qty: item.has_serial_no ? 0 : 1, code: code || "", serials: [] }
	desk.unknown = null
	show("receive")
}

function addSerial(code) {
	if (desk.receipt.serials.indexOf(code) === -1) desk.receipt.serials.push(code)
	desk.receipt.qty = desk.receipt.serials.length
}

export async function scanCode(raw) {
	const code = String(raw || "").trim()
	if (!code) return
	const current = desk.receipt.item
	if (current && current.has_serial_no && code !== desk.receipt.code && code !== current.item_code) {
		addSerial(code)
		return
	}
	if (current && !current.has_serial_no && (code === desk.receipt.code || code === current.item_code)) {
		desk.receipt.qty = Number(desk.receipt.qty || 0) + 1
		return
	}
	const found = await api.storeScan(code)
	if (found.unknown) {
		desk.unknown = found
		show("match")
		return
	}
	startReceipt(found, code === found.item_code ? "" : code)
}

export async function pickItem(itemCode) {
	const code = desk.unknown ? desk.unknown.code : ""
	startReceipt(await api.storeScan(itemCode), code)
}
