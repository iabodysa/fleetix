const sheet = document.querySelector(".mp")
const input = sheet.querySelector("input[type=file]")
const label = sheet.querySelector("[data-label]")
const count = sheet.querySelector("[data-count]")
const error = sheet.querySelector("[data-error]")
const method = "/api/method/fleetix.fleetix.api.maintenance."
const idle = label.textContent

function downscale(file, max) {
	return new Promise((resolve, reject) => {
		const url = URL.createObjectURL(file)
		const image = new Image()
		image.onerror = reject
		image.onload = () => {
			URL.revokeObjectURL(url)
			const scale = Math.min(1, max / Math.max(image.width, image.height))
			const canvas = document.createElement("canvas")
			canvas.width = Math.round(image.width * scale)
			canvas.height = Math.round(image.height * scale)
			canvas.getContext("2d").drawImage(image, 0, 0, canvas.width, canvas.height)
			canvas.toBlob(resolve, "image/jpeg", 0.85)
		}
		image.src = url
	})
}

async function upload(file, index) {
	const form = new FormData()
	form.append("file", await downscale(file, 1600), "phone-" + Date.now() + "-" + index + ".jpg")
	form.append("maintenance", sheet.dataset.maintenance)
	const response = await fetch(method + "upload_photo", {
		method: "POST",
		body: form,
		headers: { Accept: "application/json", "X-Frappe-CSRF-Token": sheet.dataset.csrf },
	})
	if (!response.ok) throw new Error(response.statusText)
}

async function refresh() {
	const response = await fetch(method + "get_photos?maintenance=" + encodeURIComponent(sheet.dataset.maintenance), {
		headers: { Accept: "application/json" },
	})
	if (response.ok) count.textContent = (await response.json()).message.length
}

input.addEventListener("change", async () => {
	const files = Array.from(input.files)
	if (!files.length) return
	input.disabled = true
	label.textContent = sheet.dataset.busy
	error.textContent = ""
	let failed = false
	for (let index = 0; index < files.length; index++) {
		try {
			await upload(files[index], index)
		} catch (e) {
			failed = true
		}
	}
	input.value = ""
	input.disabled = false
	label.textContent = idle
	error.textContent = failed ? sheet.dataset.failed : ""
	await refresh()
})
