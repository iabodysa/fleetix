<script setup>
import { ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { success } from "../../composables/useFeedback.js"
import { go, store } from "../../store/index.js"
import BigButton from "../../components/BigButton.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import SignaturePad from "../../components/SignaturePad.vue"

const busy = ref(false)
const error = ref("")

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
		const photos = store.photos.map((photo, index) => ({ file: photo.name, file_url: photo.file_url, caption: __("Photo {0}", [index + 1]) }))
		const response = await api.send({
			maintenance: store.visit.maintenance,
			odometer: Number(store.odometer),
			components: JSON.stringify(components),
			photos: JSON.stringify(photos),
			damages: JSON.stringify(store.damages),
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
	<ScreenFrame :title="__('Signatures')" :error="error">
		<div class="signs">
			<SignaturePad :label="__('Driver signature')" :value="store.signatures.driver" @change="store.signatures.driver = $event" />
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
</style>
