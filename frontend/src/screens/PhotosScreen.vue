<template>
	<section class="screen">
		<div class="pane">
			<h1>{{ __("Photos and signatures") }}</h1>
			<div class="phone-photos">
				<div class="qr-card">
					<img v-if="link" class="qr" :src="link.qr" alt="" />
					<p class="qr-text">{{ __("Scan with your phone to add photos") }}</p>
				</div>
				<div class="landed">
					<p class="landed-count">
						<span>{{ __("Photos added") }}</span>
						<strong>{{ store.photos.length }}</strong>
					</p>
					<div class="landed-strip">
						<img v-for="photo in store.photos" :key="photo.name" class="photo-thumb" :src="photo.file_url" alt="" />
					</div>
				</div>
			</div>
			<div class="signs">
				<SignaturePad :label="__('Driver signature')" :value="store.signatures.driver" @change="store.signatures.driver = $event" />
				<SignaturePad :label="__('Inspector signature')" :value="store.signatures.inspector" @change="store.signatures.inspector = $event" />
			</div>
		</div>
		<footer class="foot">
			<button class="btn btn-back" type="button" @click="store.step = 'components'">{{ __("Back") }}</button>
			<p class="error">{{ busy ? __("Sending") : error }}</p>
			<button class="btn btn-primary" type="button" :disabled="busy || !store.photos.length" @click="send">{{ __("Send for approval") }}</button>
		</footer>
	</section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { __ } from "../translate.js"
import { api, errorText } from "../api.js"
import { store } from "../store.js"
import SignaturePad from "../components/SignaturePad.vue"

const busy = ref(false)
const error = ref("")
const link = ref(null)
let timer = null

async function poll() {
	try {
		store.photos = await api.photos(store.visit.maintenance)
	} catch (e) {
		error.value = errorText(e)
	}
}

onMounted(async () => {
	poll()
	timer = setInterval(poll, 5000)
	try {
		link.value = await api.photoLink(store.visit.maintenance)
	} catch (e) {
		error.value = errorText(e)
	}
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
		const photos = store.photos.map((photo, index) => ({ file: photo.name, file_url: photo.file_url, caption: __("Photo {0}", [index + 1]) }))
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
