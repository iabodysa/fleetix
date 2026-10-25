<script setup>
import { computed } from "vue"
import { formatKm } from "../i18n.js"
import { go, store } from "../store.js"
import BigButton from "../components/BigButton.vue"
import PlateKeypad from "../components/PlateKeypad.vue"
import VehicleCard from "../components/VehicleCard.vue"

const reading = computed(() => Number(store.odometer || 0))
const below = computed(() => store.odometer !== "" && reading.value < store.vehicle.last_odometer)
const high = computed(() => !!store.vehicle.odometer_limit && reading.value > store.vehicle.odometer_limit)
</script>

<template>
	<div class="page">
		<div class="screen">
			<VehicleCard :vehicle="store.vehicle" />
			<h1 class="screen-title">{{ __("Odometer") }}</h1>
			<output class="reading" :class="{ 'reading-high': high }" dir="ltr">{{ store.odometer ? formatKm(store.odometer) : "-" }}</output>
			<p v-if="below" class="banner banner-bad" role="alert">
				{{ __("Odometer reading is below the last reading {0}", [formatKm(store.vehicle.last_odometer)]) }}
			</p>
			<p v-else-if="store.vehicle.last_odometer" class="last">
				{{ __("Last reading") }} <b dir="ltr">{{ formatKm(store.vehicle.last_odometer) }}</b>
			</p>
			<PlateKeypad v-model="store.odometer" mode="number" :max-digits="7" />
		</div>
		<div class="dock">
			<BigButton icon="next" :label="__('Next')" :disabled="!store.odometer || below" @press="go('photos')" />
		</div>
	</div>
</template>

<style scoped>
.reading {
	display: block;
	text-align: center;
	font-size: 40px;
	font-weight: 800;
	font-variant-numeric: tabular-nums;
	padding: 8px;
	border-radius: var(--radius);
	background: var(--surface);
	border: 1px solid var(--line);
}
.reading-high {
	border: 2px solid var(--warn);
	background: var(--warn-bg);
	color: var(--warn-ink);
}
.last {
	color: var(--ink-2);
	text-align: center;
}
</style>
