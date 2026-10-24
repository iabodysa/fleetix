<script setup>
import { onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { backHome, go, store } from "../../store/index.js"
import BigButton from "../../components/BigButton.vue"
import PlateKeypad from "../../components/PlateKeypad.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const MIN_MOBILE = 9
const walkin = store.walkin
const error = ref("")
const busy = ref(false)

async function lookUp() {
	const digits = walkin.mobile.replace(/\D/g, "")
	walkin.customer = null
	if (digits.length < MIN_MOBILE) return
	try {
		walkin.customer = await api.findCustomer(digits)
		if (walkin.customer && !walkin.name) walkin.name = walkin.customer.customer_name
	} catch (e) {
		error.value = errorText(e)
	}
}
async function next() {
	if (!walkin.plate.trim()) return (error.value = __("Enter the plate number"))
	if (!walkin.name.trim()) return (error.value = __("Enter the customer name"))
	if (walkin.mobile.replace(/\D/g, "").length < MIN_MOBILE) return (error.value = __("Enter the mobile number"))
	busy.value = true
	try {
		walkin.last = await api.plateFindings(walkin.plate.trim())
		go("walkinItems")
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
onMounted(async () => {
	if (walkin.setup) return
	try {
		walkin.setup = await api.walkinSetup()
	} catch (e) {
		error.value = errorText(e)
	}
})
</script>

<template>
	<ScreenFrame :title="__('Customer maintenance')" v-model:error="error">
		<div class="card walkin-form">
			<label class="walkin-field">
				<span>{{ __("Plate number") }}</span>
				<input v-model="walkin.plate" class="walkin-input ltr" type="text" autocomplete="off" @input="walkin.plate = walkin.plate.toUpperCase()" />
			</label>
			<label class="walkin-field">
				<span>{{ __("Customer name") }}</span>
				<input v-model="walkin.name" class="walkin-input" type="text" autocomplete="off" />
			</label>
			<label class="walkin-field">
				<span>{{ __("Mobile number") }}</span>
				<input v-model="walkin.mobile" class="walkin-input ltr" type="tel" inputmode="numeric" autocomplete="off" placeholder="05XXXXXXXX" @input="lookUp" />
			</label>
			<span v-if="walkin.customer" class="pill tone-done">{{ __("Existing customer") }}</span>
		</div>
		<template #aside>
			<PlateKeypad v-model="walkin.plate" />
		</template>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="backHome" />
		</template>
		<template #primary>
			<BigButton icon="next" :label="__('Next')" :busy="busy" @press="next" />
		</template>
	</ScreenFrame>
</template>

<style>
.walkin-form {
	display: grid;
	gap: var(--s4);
	padding: var(--s4);
}
.walkin-field {
	display: grid;
	gap: var(--s2);
	font-weight: 800;
}
.walkin-input {
	min-height: var(--tap);
	padding: 0 var(--s3);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface);
	font: inherit;
	font-size: var(--t-lg);
}
</style>
