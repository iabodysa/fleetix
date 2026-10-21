<template>
	<section class="screen">
		<div class="screen-split">
			<div class="pane pane-center">
				<h1>{{ __("Odometer reading") }}</h1>
				<div class="drum" dir="ltr">
					<span v-for="(digit, index) in cells" :key="index" class="drum-cell" :class="{ lead: digit === '0' && index < lead }">{{ digit }}</span>
					<span class="drum-unit">{{ __("km") }}</span>
				</div>
				<dl class="facts">
					<div>
						<dt>{{ __("Last reading") }}</dt>
						<dd>{{ formatKm(last) }}</dd>
					</div>
					<div>
						<dt>{{ __("Difference") }}</dt>
						<dd dir="ltr">{{ reading ? (diff >= 0 ? "+" : "") + diff.toLocaleString("en-US") : "-" }}</dd>
					</div>
				</dl>
			</div>
			<aside class="side">
				<KeyPad @key="press" @clear="store.odometer = ''" @back="store.odometer = store.odometer.slice(0, -1)" />
			</aside>
		</div>
		<footer class="foot">
			<button class="btn btn-back" type="button" @click="backToQueue">{{ __("Back") }}</button>
			<p class="error">{{ error }}</p>
			<button class="btn btn-primary" type="button" @click="next">{{ confirmBig ? __("Confirm reading") : __("Next") }}</button>
		</footer>
	</section>
</template>

<script setup>
import { computed, ref } from "vue"
import { __, formatKm } from "../translate.js"
import { backToQueue, store } from "../store.js"
import KeyPad from "../components/KeyPad.vue"

const last = computed(() => store.visit.last_odometer || 0)
const reading = computed(() => Number(store.odometer || 0))
const diff = computed(() => reading.value - last.value)
const cells = computed(() => ("0000000" + (store.odometer || "")).slice(-7).split(""))
const lead = computed(() => 7 - (store.odometer || "").length)
const error = ref("")
const confirmBig = ref(false)

function press(key) {
	if (store.odometer.length < 7) store.odometer = (store.odometer + key).replace(/^0+/, "")
	confirmBig.value = false
	error.value = ""
}
function next() {
	if (!reading.value) {
		error.value = __("Enter the odometer reading")
		return
	}
	if (diff.value < 0) {
		error.value = __("Odometer reading is below the last reading {0}", [formatKm(last.value)])
		return
	}
	if (diff.value > 20000 && !confirmBig.value) {
		confirmBig.value = true
		error.value = __("Difference is above 20,000 km")
		return
	}
	store.step = "components"
}
</script>
