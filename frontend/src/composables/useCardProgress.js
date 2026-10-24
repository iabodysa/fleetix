import { computed, nextTick, watch } from "vue"
import { __ } from "../i18n/index.js"

const SCROLL_MS = 320
const PULSE_MS = 1600
const GAP = 16

function root() {
	return document.scrollingElement || document.documentElement
}

export function scrollToElement(el) {
	if (!el) return
	const scroller = root()
	const strip = document.querySelector(".card-progress")
	const top = strip ? strip.getBoundingClientRect().bottom : 0
	const start = scroller.scrollTop
	const target = Math.max(0, start + el.getBoundingClientRect().top - top - GAP)
	const began = Date.now()
	function frame() {
		const t = Math.min(1, (Date.now() - began) / SCROLL_MS)
		scroller.scrollTop = start + (target - start) * (1 - Math.pow(1 - t, 3))
		if (t < 1) window.requestAnimationFrame(frame)
	}
	window.requestAnimationFrame(frame)
}

export function scrollByPage() {
	const scroller = root()
	const start = scroller.scrollTop
	const target = start + window.innerHeight * 0.7
	const began = Date.now()
	function frame() {
		const t = Math.min(1, (Date.now() - began) / SCROLL_MS)
		scroller.scrollTop = start + (target - start) * t
		if (t < 1) window.requestAnimationFrame(frame)
	}
	window.requestAnimationFrame(frame)
}

function card(key) {
	return document.querySelector('[data-card="' + String(key).replace(/"/g, '\\"') + '"]')
}

export function useCardProgress(items) {
	const missing = computed(() => items.value.filter((row) => !row.done))

	function show(key) {
		scrollToElement(card(key))
	}
	function showBelow(key) {
		const el = card(key)
		if (el && el.getBoundingClientRect().top > 0) scrollToElement(el)
	}
	function pulse(key) {
		const el = card(key)
		if (!el) return
		el.classList.remove("card-pulse")
		void el.offsetWidth
		el.classList.add("card-pulse")
		window.setTimeout(() => el.classList.remove("card-pulse"), PULSE_MS)
	}
	function guard() {
		if (!missing.value.length) return false
		show(missing.value[0].key)
		pulse(missing.value[0].key)
		return true
	}
	function nextLabel(label) {
		return missing.value.length ? __("{0} left: {1}", [missing.value.length, missing.value[0].label]) : label
	}
	watch(
		() => items.value.filter((row) => row.done).map((row) => row.key),
		(done, before) => {
			const fresh = done.filter((key) => (before || []).indexOf(key) === -1)
			if (fresh.length !== 1) return
			const keys = items.value.map((row) => row.key)
			const answered = keys.indexOf(fresh[0])
			const below = items.value.find((row, index) => index > answered && !row.done)
			if (below) nextTick(() => showBelow(below.key))
		},
	)
	return { missing, show, guard, nextLabel }
}
