<script setup>
import { computed, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { problem, success } from "../../composables/useFeedback.js"
import { backHome } from "../../store/index.js"
import { desk, resetReceipt, scanCode } from "../../store/storekeeper.js"
import BarcodeInput from "../../components/BarcodeInput.vue"
import BigButton from "../../components/BigButton.vue"
import CameraScan from "../../components/CameraScan.vue"
import PartRow from "../../components/PartRow.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import "./store.css"

const typed = ref("")
const camera = ref(false)
const busy = ref(false)
const error = ref("")
const item = computed(() => desk.receipt.item)
const facts = computed(() => {
	const out = [{ label: __("Available"), value: item.value.available }]
	if (desk.receipt.code) out.push({ label: __("Code"), value: desk.receipt.code, ltr: true })
	return out
})

async function run(code) {
	desk.notice = ""
	try {
		await scanCode(code)
		typed.value = ""
		success()
	} catch (e) {
		error.value = errorText(e)
		problem()
	}
}
function fromCamera(code) {
	camera.value = false
	run(code)
}
async function save() {
	const receipt = desk.receipt
	busy.value = true
	try {
		await api.receive({ item_code: receipt.item.item_code, qty: receipt.qty, code: receipt.code, serials: receipt.serials.join("\n") })
		resetReceipt()
		desk.notice = __("Received")
		success()
	} catch (e) {
		error.value = errorText(e)
		problem()
	} finally {
		busy.value = false
	}
}
</script>

<template>
	<ScreenFrame :title="__('Receive')" v-model:error="error">
		<template #meta>
			<span v-if="desk.notice" class="pill tone-done" role="status">{{ desk.notice }}</span>
		</template>
		<div v-if="item" class="store-stack">
			<PartRow :name="item.item_name" :code="item.item_code" :image="item.image || ''" :facts="facts" />
			<label class="store-field">
				<span>{{ __("Qty") }}</span>
				<input v-model.number="desk.receipt.qty" class="store-input ltr" type="number" min="1" inputmode="numeric" :readonly="!!item.has_serial_no" />
			</label>
			<div v-if="desk.receipt.serials.length" class="store-field">
				<span>{{ __("Serial numbers") }}</span>
				<ol class="card store-serials ltr">
					<li v-for="serial in desk.receipt.serials" :key="serial">{{ serial }}</li>
				</ol>
			</div>
		</div>
		<CameraScan v-if="camera" @code="fromCamera" @close="camera = false" />
		<template #aside>
			<div class="store-stack">
				<BarcodeInput :idle-text="__('Scan the part barcode')" :ready-text="__('Ready to scan. Point the scanner at the part barcode')" @scan="(key, raw) => run(raw || key)" />
				<BigButton icon="camera" tone="quiet" :label="__('Camera')" block @press="camera = true" />
				<form class="store-field" @submit.prevent="run(typed)">
					<span>{{ __("Code") }}</span>
					<input v-model="typed" class="store-input ltr" autocomplete="off" enterkeyhint="search" />
				</form>
			</div>
		</template>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="backHome" />
		</template>
		<template #primary>
			<BigButton v-if="item" icon="done" :label="__('Save')" :busy="busy" :disabled="!(desk.receipt.qty > 0)" @press="save" />
		</template>
	</ScreenFrame>
</template>
