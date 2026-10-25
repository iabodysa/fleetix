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

const DB_NAME = "fleetix-gate"
const STORE = "photos"
let opened = null

function database() {
	if (!opened) {
		opened = new Promise((resolve, reject) => {
			const request = indexedDB.open(DB_NAME, 1)
			request.onupgradeneeded = () => request.result.createObjectStore(STORE, { keyPath: "id" })
			request.onsuccess = () => resolve(request.result)
			request.onerror = () => reject(request.error)
		}).catch((error) => {
			opened = null
			throw error
		})
	}
	return opened
}

async function run(mode, work) {
	const db = await database()
	return new Promise((resolve, reject) => {
		const tx = db.transaction(STORE, mode)
		const request = work(tx.objectStore(STORE))
		tx.oncomplete = () => resolve(request && request.result)
		tx.onerror = () => reject(tx.error)
		tx.onabort = () => reject(tx.error)
	})
}

export function keepPhoto(id, blob) {
	return run("readwrite", (store) => store.put({ id, blob }))
}

export async function loadPhoto(id) {
	const row = await run("readonly", (store) => store.get(id))
	return row ? row.blob : null
}

export function dropPhotos(ids) {
	if (!ids.length) return Promise.resolve()
	return run("readwrite", (store) => {
		ids.forEach((id) => store.delete(id))
	}).catch(() => null)
}
