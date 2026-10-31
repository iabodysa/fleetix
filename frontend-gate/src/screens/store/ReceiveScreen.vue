<script setup>
import { computed, onMounted, ref } from "vue"
import { api, errorText } from "../../api.js"
import { __ } from "../../i18n.js"
import { hasCamera } from "../../native.js"
import { desk, resetReceipt, scanCode } from "../../storekeeper.js"
import BarcodeInput from "../../components/BarcodeInput.vue"
import BigButton from "../../components/BigButton.vue"
import PartRow from "../../components/PartRow.vue"
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
	error.value = ""
	try {
		await scanCode(code)
		typed.value = ""
	} catch (e) {
		error.value = errorText(e)
	}
}
async function save() {
	const receipt = desk.receipt
	busy.value = true
	error.value = ""
	try {
		await api.receive({ item_code: receipt.item.item_code, qty: receipt.qty, code: receipt.code, serials: receipt.serials.join("\n") })
		resetReceipt()
		desk.notice = __("Received")
	} catch (e) {
		error.value = errorText(e)
	} finally {
		busy.value = false
	}
}
onMounted(async () => {
	camera.value = await hasCamera()
})
</script>

<template>
	<div class="page">
		<div class="screen">
			<h1 class="screen-title">{{ __("Receive") }}</h1>
			<p v-if="desk.notice" class="banner banner-ok" role="status">{{ desk.notice }}</p>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<template v-if="item">
				<PartRow :name="item.item_name" :code="item.item_code" :image="item.image || ''" :facts="facts" />
				<label class="store-field">
					<span>{{ __("Qty") }}</span>
					<input v-model.number="desk.receipt.qty" class="store-input" dir="ltr" type="number" min="1" inputmode="numeric" :readonly="!!item.has_serial_no" />
				</label>
				<div v-if="desk.receipt.serials.length" class="store-field">
					<span>{{ __("Serial numbers") }}</span>
					<ol class="card store-serials" dir="ltr">
						<li v-for="serial in desk.receipt.serials" :key="serial">{{ serial }}</li>
					</ol>
				</div>
			</template>
			<BarcodeInput :camera="camera" @scan="run" />
			<form class="store-field" @submit.prevent="run(typed)">
				<span>{{ __("Code") }}</span>
				<input v-model="typed" class="store-input" dir="ltr" autocomplete="off" enterkeyhint="search" />
			</form>
		</div>
		<div v-if="item" class="dock">
			<BigButton icon="check" tone="ok" :label="__('Save')" :busy="busy" :disabled="!(desk.receipt.qty > 0)" @press="save" />
		</div>
	</div>
</template>
