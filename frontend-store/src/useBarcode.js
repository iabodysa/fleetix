import { onBeforeUnmount, onMounted } from "vue"

const KEY_GAP_MS = 60
const MIN_LENGTH = 3

export function useBarcode(onScan) {
	let buffer = ""
	let last = 0

	function typingInField(event) {
		const target = event.target
		return target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)
	}

	function onKey(event) {
		if (typingInField(event)) return
		const now = Date.now()
		if (now - last > KEY_GAP_MS) buffer = ""
		last = now
		if (event.key === "Enter") {
			if (buffer.length >= MIN_LENGTH) {
				event.preventDefault()
				onScan(buffer)
			}
			buffer = ""
			return
		}
		if (event.key.length === 1) buffer += event.key
	}

	onMounted(() => window.addEventListener("keydown", onKey))
	onBeforeUnmount(() => window.removeEventListener("keydown", onKey))
}
