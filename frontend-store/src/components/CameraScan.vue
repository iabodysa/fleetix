<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { BrowserMultiFormatReader } from "@zxing/browser"
import { __ } from "../i18n.js"
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
	<div class="veil" role="dialog" :aria-label="__('Camera')">
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
	top: 35%;
	right: 10%;
	bottom: 35%;
	left: 10%;
	border: 4px solid var(--accent);
	border-radius: 12px;
}
</style>
