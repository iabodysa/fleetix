import { reactive, watch } from "vue"
import { createResource } from "frappe-ui/src/resources/resources.js"
import { api, QUEUE_METHOD } from "../api.js"

export const STEPS = ["queue", "odometer", "parts", "damage", "photos", "signatures", "await", "review"]

export const store = reactive({
	step: "queue",
	flow: "next",
	drawer: false,
	visit: null,
	odometer: "",
	checklist: null,
	damages: [],
	photos: [],
	signatures: { driver: null, inspector: null },
	result: null,
	display: false,
	printed: false,
})

export const queue = createResource({ url: QUEUE_METHOD, auto: false, initialData: [] })

const DRAFT_STEPS = ["odometer", "parts", "damage", "photos", "signatures", "review"]
const draftKey = () => "fleetix.maintenance.draft." + ((window.frappe && window.frappe.boot && window.frappe.boot.user) || "")

function draftFields() {
	return {
		step: store.step,
		visit: store.visit,
		odometer: store.odometer,
		checklist: store.checklist,
		damages: store.damages,
		signatures: store.signatures,
	}
}

function saveDraft() {
	try {
		if (store.visit && DRAFT_STEPS.indexOf(store.step) !== -1) localStorage.setItem(draftKey(), JSON.stringify(draftFields()))
		else localStorage.removeItem(draftKey())
	} catch (e) {
		return
	}
}

watch(draftFields, saveDraft, { deep: true })

function storedDraft() {
	try {
		const draft = JSON.parse(localStorage.getItem(draftKey()) || "null")
		return draft && draft.visit && DRAFT_STEPS.indexOf(draft.step) !== -1 ? draft : null
	} catch (e) {
		return null
	}
}

export async function restoreDraft() {
	const draft = storedDraft()
	const rows = await queue.fetch()
	if (!draft || queue.error || store.step !== "queue") return
	const row = (rows || []).find((r) => r.maintenance === draft.visit.maintenance)
	if (row && row.status === draft.visit.status) {
		Object.assign(store, draft, { damages: (draft.damages || []).filter((spot) => spot.view), drawer: false, flow: "next" })
	}
	else saveDraft()
}

export function stepForStatus(row) {
	if (row.status === "Driver Arrived") return "odometer"
	if (row.status === "Full Inspection") return row.inspection ? "await" : "odometer"
	if (["Approved", "Service", "Final Check"].indexOf(row.status) !== -1) return "review"
	return null
}

export function go(step) {
	store.flow = STEPS.indexOf(step) < STEPS.indexOf(store.step) ? "back" : "next"
	store.step = step
}

export async function openVisit(row) {
	const step = stepForStatus(row)
	if (!step) return
	store.visit = row
	store.odometer = row.odometer ? String(row.odometer) : ""
	store.checklist = null
	store.damages = []
	store.photos = []
	store.signatures = { driver: null, inspector: null }
	store.result = null
	store.printed = false
	store.display = false
	store.drawer = false
	if (step === "review") store.checklist = await api.checklist(row.maintenance)
	go(step)
}

const PREVIOUS_STEP = {
	odometer: "queue",
	parts: "odometer",
	damage: "parts",
	photos: "damage",
	signatures: "photos",
	await: "queue",
	review: "queue",
	done: "queue",
}

export function stepBack() {
	if (store.drawer) {
		store.drawer = false
		return true
	}
	const previous = PREVIOUS_STEP[store.step]
	if (!previous) return false
	if (previous === "queue") backToQueue()
	else go(previous)
	return true
}

export function backToQueue() {
	store.visit = null
	store.flow = "back"
	store.step = "queue"
	store.drawer = false
	queue.fetch()
}
