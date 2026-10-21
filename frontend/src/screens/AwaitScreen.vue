<template>
	<section class="screen">
		<div class="pane pane-center">
			<div class="await-mark"></div>
			<h1>{{ __("Sent for approval") }}</h1>
			<p class="lead">{{ __("Waiting for the rental manager to approve") }}</p>
			<dl class="facts">
				<div>
					<dt>{{ __("Odometer") }}</dt>
					<dd>{{ formatKm(store.visit.odometer || store.odometer) }}</dd>
				</div>
				<div>
					<dt>{{ __("Status") }}</dt>
					<dd>{{ statusLabel(status) }}</dd>
				</div>
			</dl>
			<p class="error">{{ error }}</p>
		</div>
		<footer class="foot">
			<button class="btn btn-back" type="button" @click="backToQueue">{{ __("Other vehicle") }}</button>
			<span></span>
			<button class="btn btn-primary" type="button" @click="check">{{ __("Check now") }}</button>
		</footer>
	</section>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { formatKm, statusLabel } from "../translate.js"
import { api, errorText } from "../api.js"
import { backToQueue, openVisit, store } from "../store.js"

const status = ref(store.visit.status)
const error = ref("")
let timer = null

async function check() {
	try {
		const value = await api.status(store.visit.maintenance)
		status.value = value.status
		if (value.status !== "Full Inspection") {
			await openVisit(Object.assign({}, store.visit, value))
		}
	} catch (e) {
		error.value = errorText(e)
	}
}
onMounted(() => {
	timer = setInterval(check, 15000)
})
onBeforeUnmount(() => clearInterval(timer))
</script>
