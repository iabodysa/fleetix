<script setup>
import { ref } from "vue"
import { api, errorText } from "../api.js"
import { __ } from "../i18n.js"
import { resetReceipt, scanCode, store } from "../store.js"
import { useBarcode } from "../useBarcode.js"
import BigButton from "../components/BigButton.vue"
import CameraScan from "../components/CameraScan.vue"

const typed = ref("")
const camera = ref(false)
const busy = ref(false)
const error = ref("")

async function run(code) {
	error.value = ""
	store.notice = ""
	try {
		await scanCode(code)
		typed.value = ""
	} catch (e) {
		error.value = errorText(e)
	}
}
function fromCamera(code) {
	camera.value = false
	run(code)
}
async function save() {
	const receipt = store.receipt
	busy.value = true
	error.value = ""
	try {
		await api.receive({
			item_code: receipt.item.item_code,
			qty: receipt.qty,
			code: receipt.code,
			serials: receipt.serials.join("\n"),
			rate: receipt.rate || null,
		})
		resetReceipt()
		store.notice = __("Received")
	} catch (e) {
		error.value = errorText(e)
	} finally {
		busy.value = false
	}
}
useBarcode(run)
</script>

<template>
	<div class="page">
		<div class="screen">
			<form class="field" @submit.prevent="run(typed)">
				<span>{{ __("Code") }}</span>
				<input v-model="typed" dir="ltr" autocomplete="off" />
				<button type="submit" hidden></button>
			</form>
			<div class="pair">
				<BigButton icon="scan" tone="soft" :label="__('Scan')" @press="run(typed)" />
				<BigButton icon="camera" tone="soft" :label="__('Camera')" @press="camera = true" />
			</div>
			<p v-if="store.notice" class="banner banner-ok" role="status">{{ store.notice }}</p>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<template v-if="store.receipt.item">
				<div class="card part">
					<img v-if="store.receipt.item.image" :src="store.receipt.item.image" alt="" />
					<span class="grow">
						<strong>{{ store.receipt.item.item_name }}</strong>
						<span class="values">
							<span>{{ __("Available") }}</span><b>{{ store.receipt.item.available }}</b>
							<template v-if="store.receipt.code"><span>{{ __("Code") }}</span><b dir="ltr">{{ store.receipt.code }}</b></template>
						</span>
					</span>
				</div>
				<label class="field">
					<span>{{ __("Qty") }}</span>
					<input v-model.number="store.receipt.qty" type="number" min="1" inputmode="numeric" :readonly="!!store.receipt.item.has_serial_no" />
				</label>
				<div v-if="store.receipt.serials.length" class="field">
					<span>{{ __("Serial numbers") }}</span>
					<ol class="card serials" dir="ltr">
						<li v-for="serial in store.receipt.serials" :key="serial">{{ serial }}</li>
					</ol>
				</div>
				<label v-if="!store.receipt.item.rate_known" class="field">
					<span>{{ __("Unit cost") }}</span>
					<input v-model="store.receipt.rate" type="number" min="0" step="0.01" inputmode="decimal" dir="ltr" />
				</label>
			</template>
			<CameraScan v-if="camera" @code="fromCamera" @close="camera = false" />
		</div>
		<div v-if="store.receipt.item" class="dock">
			<BigButton icon="check" :label="__('Save')" :busy="busy" :disabled="!(store.receipt.qty > 0)" @press="save" />
		</div>
	</div>
</template>

<style scoped>
.pair {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 10px;
}
.serials {
	margin: 0;
	padding-inline-start: 36px;
	display: grid;
	gap: 4px;
}
</style>
