const MAX_SIDE = 1600

function loadImage(file) {
	return new Promise((resolve, reject) => {
		const url = URL.createObjectURL(file)
		const image = new Image()
		image.onload = () => resolve({ image, url })
		image.onerror = () => {
			URL.revokeObjectURL(url)
			reject(new Error("image"))
		}
		image.src = url
	})
}

export async function shrink(file) {
	const { image, url } = await loadImage(file)
	const scale = Math.min(1, MAX_SIDE / Math.max(image.naturalWidth, image.naturalHeight))
	const canvas = document.createElement("canvas")
	canvas.width = Math.round(image.naturalWidth * scale)
	canvas.height = Math.round(image.naturalHeight * scale)
	canvas.getContext("2d").drawImage(image, 0, 0, canvas.width, canvas.height)
	URL.revokeObjectURL(url)
	const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.82))
	return { blob: blob || file, url: URL.createObjectURL(blob || file) }
}
