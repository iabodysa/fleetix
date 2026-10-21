<template>
	<section class="screen">
		<div class="pane">
			<h1>{{ __("Photos and signatures") }}</h1>
			<div class="photo-tiles">
				<label v-for="slot in slots" :key="slot.key" class="tile photo" :class="{ ticked: store.photos[slot.key] }">
					<img v-if="store.photos[slot.key]" class="photo-thumb" :src="store.photos[slot.key].preview" alt="" />
					<span class="tile-name">{{ slot.label }}</span>
					<span class="pill" :class="store.photos[slot.key] ? 'pill-ok' : slot.required ? 'pill-bad' : 'pill-muted'">
						{{ store.photos[slot.key] ? __("Retake") : slot.required ? __("Required") : __("Optional") }}
					</span>
					<input class="photo-input" type="file" accept="image/*" capture="environment" :data-slot="slot.key" @change="take(slot, $event)" />
				</label>
			</div>
			<div class="signs">
				<SignaturePad :label="__('Driver signature')" @change="store.signatures.driver = $event" />
				<SignaturePad :label="__('Inspector signature')" @change="store.signatures.inspector = $event" />
			</div>
		</div>
		<footer class="foot">
			<button class="btn btn-back" type="button" @click="store.step = 'components'">{{ __("Back") }}</button>
			<p class="error">{{ busy ? __("Sending") : error }}</p>
			<button class="btn btn-primary" type="button" :disabled="busy" @click="send">{{ __("Send for approval") }}</button>
		</footer>
	</section>
</template>

<script setup>
import { ref } from "vue"
import { __ } from "../translate.js"
import { api, errorText, uploadPhoto } from "../api.js"
import { store } from "../store.js"
import SignaturePad from "../components/SignaturePad.vue"

const slots = [
	{ key: "odometer", label: __("Odometer"), required: true },
	{ key: "front", label: __("Front of vehicle"), required: false },
	{ key: "other", label: __("Other photo"), required: false },
]
const busy = ref(false)
const error = ref("")

async function take(slot, event) {
	const file = event.target.files && event.target.files[0]
	if (!file) return
	busy.value = true
	error.value = ""
	try {
		const uploaded = await uploadPhoto(file, store.visit.maintenance, slot.key)
		store.photos = Object.assign({}, store.photos, { [slot.key]: Object.assign(uploaded, { caption: slot.label }) })
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
	event.target.value = ""
}

async function send() {
	if (!store.photos.odometer) {
		error.value = __("Take the odometer photo")
		return
	}
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
		const photos = Object.keys(store.photos).map((key) => ({ file_url: store.photos[key].file_url, caption: store.photos[key].caption }))
		const response = await api.send({
			maintenance: store.visit.maintenance,
			odometer: Number(store.odometer),
			components: JSON.stringify(components),
			photos: JSON.stringify(photos),
			driver_signature: store.signatures.driver,
			inspector_signature: store.signatures.inspector,
		})
		store.visit = Object.assign({}, store.visit, { status: response.status, inspection: response.inspection, odometer: Number(store.odometer) })
		store.step = "await"
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
</script>
