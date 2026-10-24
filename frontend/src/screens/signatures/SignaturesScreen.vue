<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText, isBusy } from "../../api.js"
import { success } from "../../composables/useFeedback.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import SignaturePad from "../../components/SignaturePad.vue"

const POLL_MS = 3000
const busy = ref(false)
const error = ref("")
const onPhone = ref(true)
const card = ref(null)
let timer = null

async function pollDriver() {
	if (store.signatures.driver || busy.value) return
	try {
		const signature = await api.driverSignature(store.visit.maintenance)
		if (!signature || store.signatures.driver) return
		store.signatures.driver = signature
		onPhone.value = false
		if (store.signatures.inspector) await send()
	} catch (e) {
		if (!isBusy(e)) error.value = errorText(e)
	}
}
onMounted(async () => {
	pollDriver()
	timer = setInterval(pollDriver, POLL_MS)
	card.value = await api.trackCard(store.visit.maintenance).catch(() => null)
})
onBeforeUnmount(() => clearInterval(timer))

async function send() {
	if (!store.signatures.driver || !store.signatures.inspector) {
		error.value = __("Both signatures are required")
		return
	}
	busy.value = true
	error.value = ""
	try {
		const components = store.checklist.components
			.filter((row) => row.ticked)
			.map((row) => ({ component: row.component, item: row.item, qty: row.qty }))
		const response = await api.send({
			maintenance: store.visit.maintenance,
			odometer: Number(store.odometer),
			components: JSON.stringify(components),
			driver_signature: store.signatures.driver,
			inspector_signature: store.signatures.inspector,
		})
		store.visit = Object.assign({}, store.visit, { status: response.status, inspection: response.inspection, odometer: Number(store.odometer) })
		success()
		go("await")
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
</script>

<template>
	<ScreenFrame :title="__('Signatures')" v-model:error="error">
		<div class="signs">
			<div v-if="onPhone && !store.signatures.driver" class="card signs-phone">
				<span class="sign-label"><AppIcon name="signature" />{{ __("Driver signature") }}</span>
				<img v-if="card" class="signs-qr" :src="card.image" alt="" />
				<p class="signs-wait">{{ __("Waiting for the driver to sign") }}</p>
				<BigButton icon="signature" tone="quiet" :label="__('Sign on this device')" @press="onPhone = false" />
			</div>
			<SignaturePad v-else :label="__('Driver signature')" :value="store.signatures.driver" @change="store.signatures.driver = $event" />
			<SignaturePad :label="__('Inspector signature')" :value="store.signatures.inspector" @change="store.signatures.inspector = $event" />
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('photos')" />
		</template>
		<template #primary>
			<BigButton icon="send" :label="busy ? __('Sending') : __('Send for approval')" :busy="busy" @press="send" />
		</template>
	</ScreenFrame>
</template>

<style>
.signs {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
	gap: var(--s4);
}
.signs-phone {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: var(--s3);
	padding: var(--s4);
}
.signs-qr {
	width: 100%;
	max-width: 13rem;
	aspect-ratio: 1;
	background: var(--plate);
	border-radius: var(--r-sm);
}
.signs-wait {
	font-weight: 800;
}
</style>
