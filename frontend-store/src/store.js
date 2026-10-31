import { reactive } from "vue"
import { api } from "./api.js"

const ORDER = ["pending", "detail", "receive", "match", "newpart"]
const PREVIOUS = { detail: "pending", match: "receive", newpart: "match" }

function emptyReceipt() {
	return { item: null, qty: 0, code: "", serials: [], rate: "" }
}

export const store = reactive({
	step: "pending",
	forward: true,
	issue: null,
	receipt: emptyReceipt(),
	unknown: null,
	notice: "",
})

export function go(step) {
	store.forward = ORDER.indexOf(step) >= ORDER.indexOf(store.step)
	store.step = step
}

export function stepBack() {
	const previous = PREVIOUS[store.step]
	if (!previous) return false
	go(previous)
	return true
}

export function resetReceipt() {
	store.receipt = emptyReceipt()
	store.unknown = null
}

export function startReceipt(item, code) {
	store.receipt = { item, qty: item.has_serial_no ? 0 : 1, code: code || "", serials: [], rate: "" }
	store.unknown = null
	go("receive")
}

function addSerial(code) {
	if (store.receipt.serials.indexOf(code) === -1) store.receipt.serials.push(code)
	store.receipt.qty = store.receipt.serials.length
}

export async function scanCode(raw) {
	const code = String(raw || "").trim()
	if (!code) return
	const current = store.receipt.item
	if (current && current.has_serial_no && code !== store.receipt.code && code !== current.item_code) {
		addSerial(code)
		return
	}
	if (current && !current.has_serial_no && (code === store.receipt.code || code === current.item_code)) {
		store.receipt.qty = Number(store.receipt.qty || 0) + 1
		return
	}
	const found = await api.scan(code)
	if (found.unknown) {
		store.unknown = found
		go("match")
		return
	}
	startReceipt(found, code === found.item_code ? "" : code)
}

export async function pickItem(item_code) {
	const code = store.unknown ? store.unknown.code : ""
	startReceipt(await api.scan(item_code), code)
}
