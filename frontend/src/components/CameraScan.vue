<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { BrowserMultiFormatReader } from "@zxing/browser"
import { __ } from "../i18n/index.js"
import BigButton from "./BigButton.vue"

const emit = defineEmits(["code", "close"])
const video = ref(null)
const failed = ref("")
let controls = null

function stop() {
	if (controls) controls.stop()
	controls = null
}

onMounted(async () => {
	try {
		const reader = new BrowserMultiFormatReader()
		controls = await reader.decodeFromConstraints({ video: { facingMode: "environment" }, audio: false }, video.value, (result) => {
			if (!result) return
			stop()
			emit("code", result.getText())
		})
	} catch (e) {
		failed.value = e && e.name === "NotAllowedError" ? __("Camera access is off for this app") : __("This device has no camera")
	}
})
onBeforeUnmount(stop)
</script>

<template>
	<div class="camera-scan" role="dialog" :aria-label="__('Camera')">
		<div class="camera-scan-frame">
			<video ref="video" playsinline muted></video>
			<span class="camera-scan-aim" aria-hidden="true"></span>
		</div>
		<p v-if="failed" class="camera-scan-failed">{{ failed }}</p>
		<BigButton icon="close" tone="quiet" :label="__('Close')" block @press="emit('close')" />
	</div>
</template>

<style>
.camera-scan {
	position: fixed;
	inset: 0;
	z-index: 40;
	display: flex;
	flex-direction: column;
	justify-content: center;
	gap: var(--s4);
	padding: var(--s4);
	background: rgba(0, 0, 0, 0.92);
}
.camera-scan-frame {
	position: relative;
	width: 100%;
	max-width: 32rem;
	height: min(calc(100vw - 2rem), 32rem);
	margin: 0 auto;
	border-radius: var(--r-md);
	overflow: hidden;
	background: #000;
}
.camera-scan-frame video {
	width: 100%;
	height: 100%;
	object-fit: cover;
}
.camera-scan-aim {
	position: absolute;
	inset: 35% 10%;
	border: 4px solid var(--done);
	border-radius: var(--r-md);
}
.camera-scan-failed {
	padding: var(--s3);
	border-radius: var(--r-md);
	background: var(--problem-bg);
	color: var(--problem-ink);
	font-weight: 700;
	text-align: center;
}
</style>
