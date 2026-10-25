import { onBeforeUnmount, onMounted, ref } from "vue"
import { api, errorText } from "../api.js"
import { store } from "../store/index.js"
import { useBarcode } from "./useBarcode.js"

const IDLE_MS = 30 * 60 * 1000
const CHECK_MS = 60 * 1000
const ACTIVITY = ["pointerdown", "keydown"]

export function useShift() {
	const error = ref("")
	const busy = ref(false)
	let last = Date.now()
	let timer = 0

	async function scan(code) {
		if (busy.value || !window.frappe.boot.is_worker) return
		busy.value = true
		error.value = ""
		try {
			store.worker = await api.scanBadge(code)
		} catch (e) {
			error.value = errorText(e)
		}
		busy.value = false
	}
	async function end() {
		store.worker = null
		await api.leaveShift().catch(() => null)
	}
	function touch() {
		last = Date.now()
	}
	function check() {
		if (store.worker && Date.now() - last > IDLE_MS) end()
	}
	function onVisible() {
		if (document.visibilityState === "visible") check()
	}

	useBarcode(scan, true)
	onMounted(() => {
		ACTIVITY.forEach((name) => window.addEventListener(name, touch, { capture: true, passive: true }))
		document.addEventListener("visibilitychange", onVisible)
		timer = setInterval(check, CHECK_MS)
	})
	onBeforeUnmount(() => {
		ACTIVITY.forEach((name) => window.removeEventListener(name, touch, { capture: true }))
		document.removeEventListener("visibilitychange", onVisible)
		clearInterval(timer)
	})
	return { error, busy, end }
}
