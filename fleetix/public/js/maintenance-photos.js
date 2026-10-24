const sheet = document.querySelector(".mp")
const error = sheet.querySelector("[data-error]")
const method = "/api/method/fleetix.fleetix.api.maintenance."

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

async function upload(file, slot) {
	const form = new FormData()
	form.append("file", await downscale(file, 1600), "phone-" + slot + "-" + Date.now() + ".jpg")
	form.append("maintenance", sheet.dataset.maintenance)
	form.append("slot", slot)
	const response = await fetch(method + "upload_photo", {
		method: "POST",
		body: form,
		headers: { Accept: "application/json", "X-Frappe-CSRF-Token": sheet.dataset.csrf },
	})
	if (!response.ok) throw new Error(response.statusText)
}

sheet.querySelectorAll("input[type=file]").forEach((input) => {
	input.addEventListener("change", async () => {
		const file = input.files[0]
		if (!file) return
		const label = input.parentNode.querySelector(".mp-slot-label")
		const idle = label.textContent
		input.disabled = true
		label.textContent = sheet.dataset.busy
		error.textContent = ""
		try {
			await upload(file, input.dataset.slot)
			window.location.reload()
		} catch (e) {
			input.value = ""
			input.disabled = false
			label.textContent = idle
			error.textContent = sheet.dataset.failed
		}
	})
})
