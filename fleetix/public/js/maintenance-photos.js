const sheet = document.querySelector(".mp")
const error = sheet.querySelector("[data-error]")
const start = sheet.querySelector("[data-start]")
const cam = sheet.querySelector("[data-cam]")
const video = cam.querySelector("video")
const camLabel = cam.querySelector("[data-cam-label]")
const camProgress = cam.querySelector("[data-cam-progress]")
const camError = cam.querySelector("[data-cam-error]")
const retake = cam.querySelector("[data-retake]")
const shutter = cam.querySelector("[data-shutter]")
const choice = cam.querySelector("[data-choice]")
const method = "/api/method/fleetix.fleetix.api.maintenance."
const MAX_SIDE = 1600
const slots = Array.prototype.map.call(sheet.querySelectorAll(".mp-slot"), (row) => ({
	key: row.dataset.slot,
	label: row.dataset.label,
	done: row.hasAttribute("data-done"),
	row,
	input: row.querySelector("input"),
}))
const pending = []
let stream = null
let current = null
let last = null
let fallback = false
let extras = 0

function jpeg(source, width, height) {
	const scale = Math.min(1, MAX_SIDE / Math.max(width, height))
	const canvas = document.createElement("canvas")
	canvas.width = Math.round(width * scale)
	canvas.height = Math.round(height * scale)
	canvas.getContext("2d").drawImage(source, 0, 0, canvas.width, canvas.height)
	return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.85))
}

function downscale(file) {
	return new Promise((resolve, reject) => {
		const url = URL.createObjectURL(file)
		const image = new Image()
		image.onerror = reject
		image.onload = () => {
			URL.revokeObjectURL(url)
			resolve(jpeg(image, image.width, image.height))
		}
		image.src = url
	})
}

async function upload(blob, slot) {
	const form = new FormData()
	form.append("file", blob, "phone-" + slot + "-" + Date.now() + ".jpg")
	form.append("maintenance", sheet.dataset.maintenance)
	form.append("slot", slot)
	const response = await fetch(method + "upload_photo", {
		method: "POST",
		body: form,
		headers: { Accept: "application/json", "X-Frappe-CSRF-Token": sheet.dataset.csrf },
	})
	if (!response.ok) throw new Error(response.statusText)
}

function nextSlot() {
	return slots.find((slot) => !slot.done) || null
}

function aim(slot) {
	current = slot
	choice.hidden = true
	shutter.disabled = false
	camLabel.textContent = extras ? slot.label + " +" + extras : slot.label
	camProgress.textContent = slots.filter((row) => row.done).length + (extras ? 0 : 1) + " / " + slots.length
}

function show() {
	extras = 0
	const slot = nextSlot()
	if (!slot) return finish()
	aim(slot)
}

function shoot() {
	const slot = current
	if (!slot || !video.videoWidth) return
	const required = !slot.done
	const job = jpeg(video, video.videoWidth, video.videoHeight)
		.then((blob) => upload(blob, slot.key))
		.catch(() => {
			if (required) slot.done = false
			camError.textContent = sheet.dataset.failed
		})
	pending.push(job)
	slot.done = true
	last = slot
	retake.disabled = false
	camError.textContent = ""
	shutter.disabled = true
	choice.hidden = false
}

async function finish() {
	current = null
	shutter.disabled = true
	camLabel.textContent = sheet.dataset.busy
	camProgress.textContent = ""
	await Promise.all(pending)
	if (nextSlot()) return show()
	close()
}

async function close() {
	if (stream) stream.getTracks().forEach((track) => track.stop())
	stream = null
	await Promise.all(pending)
	window.location.reload()
}

async function openCamera() {
	if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return false
	try {
		stream = await navigator.mediaDevices.getUserMedia({
			video: { facingMode: { ideal: "environment" }, width: { ideal: 1920 }, height: { ideal: 1080 } },
			audio: false,
		})
	} catch (e) {
		return false
	}
	video.srcObject = stream
	cam.hidden = false
	await video.play().catch(() => null)
	show()
	return true
}

function offerNext() {
	const slot = nextSlot()
	if (!slot) return window.location.reload()
	fallback = true
	start.textContent = sheet.dataset.next.replace("{0}", slot.label)
	start.hidden = false
	slot.input.click()
}

start.addEventListener("click", async () => {
	error.textContent = ""
	if (fallback) return nextSlot() && nextSlot().input.click()
	if (!(await openCamera())) offerNext()
})
shutter.addEventListener("click", shoot)
cam.querySelector("[data-extra]").addEventListener("click", () => {
	extras += 1
	aim(last)
})
cam.querySelector("[data-advance]").addEventListener("click", show)
retake.addEventListener("click", () => {
	if (!last) return
	last.done = false
	retake.disabled = true
	show()
})
cam.querySelector("[data-list]").addEventListener("click", close)
window.addEventListener("pagehide", () => stream && stream.getTracks().forEach((track) => track.stop()))

slots.forEach((slot) => {
	slot.input.addEventListener("change", async () => {
		const file = slot.input.files[0]
		if (!file) return
		const label = slot.row.querySelector(".mp-slot-label")
		const count = slot.row.querySelector(".mp-slot-count")
		slot.input.disabled = true
		label.textContent = sheet.dataset.busy
		error.textContent = ""
		try {
			await upload(await downscale(file), slot.key)
			slot.done = true
			slot.row.classList.add("mp-slot-done")
			count.textContent = Number(count.textContent) + 1
			offerNext()
		} catch (e) {
			error.textContent = sheet.dataset.failed
		}
		slot.input.value = ""
		slot.input.disabled = false
		label.textContent = slot.label
	})
})
