<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { __ } from "../i18n.js"
import BigButton from "./BigButton.vue"

const emit = defineEmits(["code", "close"])
const video = ref(null)
const failed = ref("")
let stream = null
let frame = 0
let detector = null
let decode = null
const canvas = document.createElement("canvas")

async function reader() {
	if ("BarcodeDetector" in window) {
		try {
			const formats = await window.BarcodeDetector.getSupportedFormats()
			if (formats.length) {
				detector = new window.BarcodeDetector({ formats })
				return
			}
		} catch (e) {
			detector = null
		}
	}
	decode = (await import("jsqr")).default
}

async function tick() {
	const el = video.value
	if (!el || el.readyState < 2) {
		frame = requestAnimationFrame(tick)
		return
	}
	let code = null
	if (detector) {
		const found = await detector.detect(el).catch(() => [])
		code = found.length ? found[0].rawValue : null
	} else if (decode) {
		canvas.width = el.videoWidth
		canvas.height = el.videoHeight
		const ctx = canvas.getContext("2d", { willReadFrequently: true })
		ctx.drawImage(el, 0, 0)
		const image = ctx.getImageData(0, 0, canvas.width, canvas.height)
		const hit = decode(image.data, image.width, image.height, { inversionAttempts: "dontInvert" })
		code = hit ? hit.data : null
	}
	if (code) emit("code", code)
	else frame = requestAnimationFrame(tick)
}

onMounted(async () => {
	try {
		stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false })
		video.value.srcObject = stream
		await video.value.play()
		await reader()
		frame = requestAnimationFrame(tick)
	} catch (e) {
		failed.value = e && e.name === "NotAllowedError" ? __("Camera access is off for this app") : __("This device has no camera")
	}
})
onBeforeUnmount(() => {
	cancelAnimationFrame(frame)
	if (stream) stream.getTracks().forEach((track) => track.stop())
})
</script>

<template>
	<div class="veil" role="dialog" :aria-label="__('Scan code')">
		<div class="frame">
			<video ref="video" playsinline muted></video>
			<span class="aim" aria-hidden="true"></span>
		</div>
		<p v-if="failed" class="banner banner-bad">{{ failed }}</p>
		<BigButton icon="back" tone="soft" :label="__('Close')" @press="emit('close')" />
	</div>
</template>

<style scoped>
.veil {
	position: fixed;
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
	z-index: 30;
	background: rgba(0, 0, 0, 0.92);
	display: flex;
	flex-direction: column;
	justify-content: center;
	gap: 16px;
	padding: 16px;
}
.frame {
	position: relative;
	width: 100%;
	max-width: 520px;
	margin: 0 auto;
	height: calc(100vw - 32px);
	max-height: 520px;
	border-radius: var(--radius);
	overflow: hidden;
	background: #000;
}
video {
	width: 100%;
	height: 100%;
	object-fit: cover;
}
.aim {
	position: absolute;
	top: 18%;
	right: 18%;
	bottom: 18%;
	left: 18%;
	border: 4px solid var(--accent);
	border-radius: 12px;
}
</style>
