import { reactive, watch } from "vue"
import { api } from "./api.js"
import { __ } from "./i18n.js"
import { dropPhotos, keepPhoto, loadPhoto } from "./photos.js"

export const STEPS = ["plate", "odometer", "photos", "route"]
export const SIDES = ["front", "back", "left", "right"]
const PREVIOUS = { odometer: "plate", photos: "odometer", route: "photos" }
const FIRST_RETRY_MS = 2000
const MAX_RETRY_MS = 60000
const blobs = new Map()
const inflight = new Map()
let retryTimer = null
let retryDelay = FIRST_RETRY_MS
const DRAFT_KEY = "fleetix.gate.draft." + ((window.frappe && window.frappe.boot && window.frappe.boot.user) || "")

function emptyPhotos() {
	return { front: null, back: null, left: null, right: null, damage: [], extra: [] }
}

export const store = reactive({
	step: "plate",
	forward: true,
	vehicle: null,
	odometer: "",
	photos: emptyPhotos(),
	route: null,
	result: null,
})

function photoMeta(photo) {
	return photo && { id: photo.id, slot: photo.slot, file: photo.file }
}

function draft() {
	return {
		step: store.step,
		vehicle: store.vehicle,
		odometer: store.odometer,
		route: store.route,
		photos: {
			front: photoMeta(store.photos.front),
			back: photoMeta(store.photos.back),
			left: photoMeta(store.photos.left),
			right: photoMeta(store.photos.right),
			damage: store.photos.damage.map(photoMeta),
			extra: store.photos.extra.map(photoMeta),
		},
	}
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

async function revive(meta) {
	if (!meta || !meta.id) return null
	const blob = blobs.get(meta.id) || (await loadPhoto(meta.id).catch(() => null))
	if (!blob && !meta.file) return null
	if (blob) blobs.set(meta.id, blob)
	return { ...meta, url: blob ? URL.createObjectURL(blob) : null, state: meta.file ? "uploaded" : "saved" }
}

export async function restoreDraft() {
	let saved = null
	try {
		saved = JSON.parse(localStorage.getItem(DRAFT_KEY) || "null")
	} catch (e) {
		return
	}
	if (!saved || !saved.vehicle || STEPS.indexOf(saved.step) === -1) return
	const photos = emptyPhotos()
	const kept = saved.photos || {}
	for (const side of SIDES) photos[side] = await revive(kept[side])
	for (const list of ["damage", "extra"]) {
		for (const meta of kept[list] || []) {
			const photo = await revive(meta)
			if (photo) photos[list].push(photo)
		}
	}
	Object.assign(store, { step: saved.step, vehicle: saved.vehicle, odometer: saved.odometer || "", route: saved.route || null, photos })
	pump()
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

function forgetPhotos() {
	const rows = photoList()
	rows.forEach((row) => {
		if (row.photo.url) URL.revokeObjectURL(row.photo.url)
		blobs.delete(row.photo.id)
	})
	dropPhotos(rows.map((row) => row.photo.id))
}

export async function lookUp(code) {
	const vehicle = await api.find(code)
	if (!vehicle) return false
	forgetPhotos()
	Object.assign(store, { vehicle, odometer: "", photos: emptyPhotos(), route: null, result: null })
	go("odometer")
	return true
}

export function photoList() {
	const rows = SIDES.filter((side) => store.photos[side]).map((side) => ({ name: side, photo: store.photos[side] }))
	store.photos.damage.concat(store.photos.extra).forEach((photo) => rows.push({ name: photo.slot, photo }))
	return rows
}

export async function addPhoto(slot, shrunk) {
	const photo = reactive({ id: slot + "-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8), slot, url: shrunk.url, state: "saving", file: null })
	blobs.set(photo.id, shrunk.blob)
	if (SIDES.indexOf(slot) === -1) store.photos[slot.indexOf("damage") === 0 ? "damage" : "extra"].push(photo)
	else {
		const old = store.photos[slot]
		if (old) {
			if (old.url) URL.revokeObjectURL(old.url)
			blobs.delete(old.id)
			dropPhotos([old.id])
		}
		store.photos[slot] = photo
	}
	await keepPhoto(photo.id, shrunk.blob).catch(() => null)
	photo.state = "saved"
	pump()
	return photo
}

function uploadOne(photo, vehicle) {
	if (photo.file) return Promise.resolve()
	if (inflight.has(photo.id)) return inflight.get(photo.id)
	const job = (async () => {
		photo.state = "uploading"
		try {
			const blob = blobs.get(photo.id) || (await loadPhoto(photo.id))
			if (!blob) throw new Error(__("The photo could not be read. Take it again."))
			const saved = await api.upload(vehicle, blob, photo.slot + ".jpg")
			photo.file = saved.name
			photo.state = "uploaded"
		} catch (error) {
			photo.state = navigator.onLine === false ? "saved" : "failed"
			throw error
		} finally {
			inflight.delete(photo.id)
		}
	})()
	inflight.set(photo.id, job)
	return job
}

export async function pump() {
	clearTimeout(retryTimer)
	if (!store.vehicle) return null
	const vehicle = store.vehicle.vehicle
	let failure = null
	for (const row of photoList()) {
		try {
			await uploadOne(row.photo, vehicle)
		} catch (error) {
			failure = error
		}
	}
	if (failure) {
		retryTimer = setTimeout(pump, retryDelay)
		retryDelay = Math.min(retryDelay * 2, MAX_RETRY_MS)
	} else retryDelay = FIRST_RETRY_MS
	return failure
}

export function retryNow() {
	retryDelay = FIRST_RETRY_MS
	return pump()
}

window.addEventListener("online", retryNow)

export async function sendEntry() {
	const failure = await pump()
	if (failure) throw failure
	const rows = photoList()
	store.result = await api.record(store.vehicle.vehicle, store.odometer, store.route, rows.map((row) => ({ name: row.photo.file, slot: row.photo.slot })))
	go("done")
	forgetPhotos()
}

export function nextCar() {
	forgetPhotos()
	Object.assign(store, { vehicle: null, odometer: "", photos: emptyPhotos(), route: null, result: null })
	go("plate")
}
