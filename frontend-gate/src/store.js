import { reactive, watch } from "vue"
import { api } from "./api.js"

export const STEPS = ["plate", "odometer", "photos", "route"]
export const SIDES = ["front", "back", "left", "right"]
const PREVIOUS = { odometer: "plate", photos: "odometer", route: "photos" }
const DRAFT_KEY = "fleetix.gate.draft." + ((window.frappe && window.frappe.boot && window.frappe.boot.user) || "")

function emptyPhotos() {
	return { front: null, back: null, left: null, right: null, damage: [] }
}

export const store = reactive({
	step: "plate",
	forward: true,
	vehicle: null,
	odometer: "",
	photos: emptyPhotos(),
	route: null,
	result: null,
	sent: 0,
})

function draft() {
	return { step: store.step, vehicle: store.vehicle, odometer: store.odometer }
}

watch(
	draft,
	(value) => {
		try {
			if (value.vehicle && value.step !== "done") localStorage.setItem(DRAFT_KEY, JSON.stringify(value))
			else localStorage.removeItem(DRAFT_KEY)
		} catch (e) {
			return
		}
	},
	{ deep: true },
)

export function restoreDraft() {
	try {
		const saved = JSON.parse(localStorage.getItem(DRAFT_KEY) || "null")
		if (!saved || !saved.vehicle || STEPS.indexOf(saved.step) === -1) return
		Object.assign(store, saved, { step: saved.step === "route" ? "photos" : saved.step })
	} catch (e) {
		return
	}
}

export function go(step) {
	const order = STEPS.concat("done")
	store.forward = order.indexOf(step) >= order.indexOf(store.step)
	store.step = step
}

export function stepBack() {
	const previous = PREVIOUS[store.step]
	if (!previous) return false
	go(previous)
	return true
}

export async function lookUp(code) {
	const vehicle = await api.find(code)
	if (!vehicle) return false
	store.vehicle = vehicle
	store.odometer = ""
	store.photos = emptyPhotos()
	store.route = null
	go("odometer")
	return true
}

export function photoList() {
	const rows = SIDES.filter((side) => store.photos[side]).map((side) => ({ name: side, photo: store.photos[side] }))
	store.photos.damage.forEach((photo, index) => rows.push({ name: "damage-" + (index + 1), photo }))
	return rows
}

export async function sendEntry() {
	if (!store.result) {
		store.result = await api.record(store.vehicle.vehicle, store.odometer, store.route)
		store.sent = 0
	}
	const rows = photoList()
	for (let index = store.sent; index < rows.length; index++) {
		await api.upload(store.result.doctype, store.result.name, rows[index].photo.blob, rows[index].name + ".jpg")
		store.sent = index + 1
	}
	go("done")
}

export function nextCar() {
	photoList().forEach((row) => URL.revokeObjectURL(row.photo.url))
	Object.assign(store, { vehicle: null, odometer: "", photos: emptyPhotos(), route: null, result: null, sent: 0 })
	go("plate")
}
