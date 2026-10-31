<script setup>
import { onBeforeUnmount, ref } from "vue"
import { scanKey, useBarcode } from "../composables/useBarcode.js"
import AppIcon from "./AppIcon.vue"

const READY_MS = 10000
const READ_MS = 1500
defineProps({ idleText: { type: String, default: "" }, readyText: { type: String, default: "" } })
const emit = defineEmits(["scan"])
const state = ref("idle")
let timer = 0

function settle(next, ms) {
	clearTimeout(timer)
	state.value = next
	timer = setTimeout(() => (state.value = "idle"), ms)
}
function arm(event) {
	event.currentTarget.focus()
	settle("ready", READY_MS)
}
useBarcode((code) => {
	settle("read", READ_MS)
	emit("scan", scanKey(code), code)
})
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
	<button class="barcode-input" :class="'barcode-input-' + state" type="button" @click="arm">
		<span class="barcode-input-mark"><AppIcon :name="state === 'read' ? 'done' : 'scan'" size="lg" /></span>
		<span class="barcode-input-text" aria-live="polite">
			{{ state === "ready" ? readyText || __("Ready to scan. Point the scanner at the vehicle barcode") : idleText || __("Scan the vehicle barcode") }}
		</span>
	</button>
</template>

<style>
.barcode-input {
	display: flex;
	align-items: center;
	gap: var(--s3);
	width: 100%;
	min-height: var(--button);
	padding: var(--s2) var(--s4);
	border: 2px dashed var(--line);
	border-radius: var(--r-md);
	background: var(--surface);
	font-weight: 700;
	text-align: start;
	transition: background-color 160ms var(--ease), border-color 160ms var(--ease);
}
.barcode-input-mark {
	display: inline-flex;
	color: var(--done);
	animation: barcode-input-pulse 1.6s ease-in-out infinite;
}
.barcode-input-ready {
	border-style: solid;
	border-color: var(--done);
	background: var(--done-bg);
	color: var(--done-ink);
	animation: barcode-input-ready 1.2s ease-in-out infinite;
}
.barcode-input-ready .barcode-input-mark {
	animation-duration: 0.8s;
}
.barcode-input-read {
	border-style: solid;
	border-color: var(--done);
	background: var(--done);
	color: var(--on-done);
}
.barcode-input-read .barcode-input-mark {
	color: var(--on-done);
	animation: none;
}
@keyframes barcode-input-pulse {
	50% {
		opacity: 0.45;
	}
}
@keyframes barcode-input-ready {
	50% {
		box-shadow: 0 0 0 6px var(--done-bg);
	}
}
</style>
