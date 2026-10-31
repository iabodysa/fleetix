import { reactive } from "vue"
import { createResource } from "frappe-ui/src/resources/resources.js"
import { STORE_BOOT_METHOD, api } from "../api.js"
import { go } from "./index.js"

function emptyReceipt() {
	return { item: null, qty: 0, code: "", serials: [] }
}

export const desk = reactive({
	issue: null,
	receipt: emptyReceipt(),
	unknown: null,
	notice: "",
})

export const storeBoot = createResource({ url: STORE_BOOT_METHOD, auto: false, initialData: { models: [], groups: [] } })

export function openApprovals() {
	desk.issue = null
	desk.notice = ""
	go("approvals")
}

export function openReceive() {
	resetReceipt()
	desk.notice = ""
	if (!storeBoot.fetched) storeBoot.fetch()
	go("receive")
}

export function resetReceipt() {
	desk.receipt = emptyReceipt()
	desk.unknown = null
}

function startReceipt(item, code) {
	desk.receipt = { item, qty: item.has_serial_no ? 0 : 1, code: code || "", serials: [] }
	desk.unknown = null
	go("receive")
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
		go("match")
		return
	}
	startReceipt(found, code === found.item_code ? "" : code)
}

export async function pickItem(itemCode) {
	const code = desk.unknown ? desk.unknown.code : ""
	startReceipt(await api.storeScan(itemCode), code)
}
