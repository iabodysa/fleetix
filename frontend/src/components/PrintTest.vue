<script setup>
import { onMounted, ref } from "vue"
import { __ } from "../i18n/index.js"
import { api, errorText } from "../api.js"
import { hasPrinter, imageStats, printBitmap, sampleImage } from "../native.js"
import BigButton from "./BigButton.vue"
import ErrorCard from "./ErrorCard.vue"

const emit = defineEmits(["close"])
const samples = ref([])
const busy = ref("")
const error = ref("")
const report = ref("")
const version = window.frappe.boot.app_version || ""

async function print(sample) {
	busy.value = sample.label
	report.value = ""
	try {
		const bitmap = await sampleImage(sample)
		const stats = await imageStats(bitmap)
		report.value = stats ? `${version} | ${stats.width}x${stats.height} | ${stats.kb} KB | ${stats.ink}%` : version
		if (!hasPrinter()) error.value = __("Printer not connected")
		else if (await printBitmap(bitmap)) report.value += " | OK"
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = ""
}
onMounted(async () => {
	try {
		samples.value = await api.printSamples()
	} catch (e) {
		error.value = errorText(e)
	}
})
</script>

<template>
	<div class="card print-test">
		<div class="drawer-head">
			<h2>{{ __("Print test") }}</h2>
			<BigButton icon="close" tone="quiet" :label="__('Close')" @press="emit('close')" />
		</div>
		<div class="print-test-list">
			<BigButton v-for="sample in samples" :key="sample.label" icon="printer" tone="quiet" :label="sample.label" :busy="busy === sample.label" block @press="print(sample)" />
		</div>
		<p v-if="report" class="muted ltr">{{ report }}</p>
		<ErrorCard :error="error" @dismiss="error = ''" />
	</div>
</template>

<style>
.print-test {
	padding: var(--s4);
}
.print-test-list {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr));
	gap: var(--s2);
}
</style>
