<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { __ } from "../i18n.js"
import GateIcon from "./GateIcon.vue"
import CameraScanner from "./CameraScanner.vue"

defineProps({ camera: { type: Boolean, default: false } })
const emit = defineEmits(["scan"])
const KEY_GAP_MS = 60
const MIN_LENGTH = 3
const scanning = ref(false)
let buffer = ""
let last = 0

function onKey(event) {
	const target = event.target
	if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA")) return
	const now = Date.now()
	if (now - last > KEY_GAP_MS) buffer = ""
	last = now
	if (event.key === "Enter") {
		if (buffer.length >= MIN_LENGTH) {
			event.preventDefault()
			emit("scan", buffer)
		}
		buffer = ""
		return
	}
	if (event.key.length === 1) buffer += event.key
}
function found(code) {
	scanning.value = false
	emit("scan", code)
}
onMounted(() => window.addEventListener("keydown", onKey))
onBeforeUnmount(() => window.removeEventListener("keydown", onKey))
</script>

<template>
	<button v-if="camera" type="button" class="scan" @click="scanning = true">
		<GateIcon name="scan" />
		<span>{{ __("Scan code") }}</span>
	</button>
	<CameraScanner v-if="scanning" @code="found" @close="scanning = false" />
</template>

<style scoped>
.scan {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 10px;
	min-height: 56px;
	border: 2px dashed var(--line);
	border-radius: var(--radius);
	background: transparent;
	font-weight: 700;
	width: 100%;
}
</style>
