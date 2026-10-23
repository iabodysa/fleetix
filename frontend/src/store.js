import { reactive, watch } from "vue"
import { createResource } from "frappe-ui/src/resources/resources.js"
import { api, QUEUE_METHOD } from "./api.js"

export const STEPS = ["queue", "odometer", "components", "photos", "await", "review"]

export const store = reactive({
	step: "queue",
	drawer: false,
	visit: null,
	odometer: "",
	checklist: null,
	photos: [],
	signatures: { driver: null, inspector: null },
	result: null,
	display: false,
	printed: false,
})

export const queue = createResource({ url: QUEUE_METHOD, auto: false, initialData: [] })

const DRAFT_STEPS = ["odometer", "components", "photos", "review"]
const DRAFT_KEY = "fleetix.maintenance.draft." + ((window.frappe && window.frappe.boot && window.frappe.boot.user) || "")

function draftFields() {
	return { step: store.step, visit: store.visit, odometer: store.odometer, checklist: store.checklist, signatures: store.signatures }
}

function saveDraft() {
	try {
		if (store.visit && DRAFT_STEPS.indexOf(store.step) !== -1) localStorage.setItem(DRAFT_KEY, JSON.stringify(draftFields()))
		else localStorage.removeItem(DRAFT_KEY)
	} catch (e) {
		return
	}
}

watch(draftFields, saveDraft, { deep: true })

function storedDraft() {
	try {
		const draft = JSON.parse(localStorage.getItem(DRAFT_KEY) || "null")
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
	if (row && row.status === draft.visit.status) Object.assign(store, draft, { drawer: false })
	else saveDraft()
}

export function stepForStatus(row) {
	if (row.status === "Driver Arrived") return "odometer"
	if (row.status === "Full Inspection") return row.inspection ? "await" : "odometer"
	if (["Approved", "Service", "Final Check"].indexOf(row.status) !== -1) return "review"
	return null
}

export async function openVisit(row) {
	const step = stepForStatus(row)
	if (!step) return
	store.visit = row
	store.odometer = row.odometer ? String(row.odometer) : ""
	store.checklist = null
	store.photos = []
	store.signatures = { driver: null, inspector: null }
	store.result = null
	store.printed = false
	store.display = false
	store.drawer = false
	if (step === "review") store.checklist = await api.checklist(row.maintenance)
	store.step = step
}

const PREVIOUS_STEP = { odometer: "queue", components: "odometer", photos: "components", await: "queue", review: "queue", done: "queue" }

export function stepBack() {
	if (store.drawer) {
		store.drawer = false
		return true
	}
	const previous = PREVIOUS_STEP[store.step]
	if (!previous) return false
	if (previous === "queue") backToQueue()
	else store.step = previous
	return true
}

export function backToQueue() {
	store.visit = null
	store.step = "queue"
	store.drawer = false
	queue.fetch()
}
