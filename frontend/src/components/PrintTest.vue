<script setup>
import { onMounted, ref } from "vue"
import { __ } from "../i18n/index.js"
import { api, errorText } from "../api.js"
import { printSample } from "../native.js"
import BigButton from "./BigButton.vue"
import ErrorCard from "./ErrorCard.vue"

const emit = defineEmits(["close"])
const samples = ref([])
const busy = ref("")
const error = ref("")

async function print(sample) {
	busy.value = sample.label
	try {
		if (!(await printSample(sample))) error.value = __("Printer not connected")
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
