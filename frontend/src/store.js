import { reactive } from "vue"
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

export function backToQueue() {
	store.visit = null
	store.step = "queue"
	store.drawer = false
	queue.fetch()
}
