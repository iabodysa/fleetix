<template>
	<section class="screen">
		<div class="pane">
			<h1>{{ __("Review") }}</h1>
			<div class="review">
				<div class="card review-card">
					<span class="label">{{ __("Vehicle") }}</span>
					<PlateChip :plate="vehicle.plate" />
					<div class="value">{{ vehicle.model }}</div>
					<div class="muted">{{ vehicle.driver_name || vehicle.driver }} · {{ vehicle.project }}</div>
				</div>
				<div class="card review-card">
					<span class="label">{{ __("Odometer") }}</span>
					<div class="value value-big">{{ formatKm(store.checklist.odometer) }}</div>
					<div class="muted">{{ __("Last reading") }} {{ formatKm(vehicle.last_odometer) }}</div>
					<span class="pill pill-ok">{{ statusLabel(store.checklist.status) }}</span>
				</div>
				<div class="card review-card review-wide">
					<span class="label">{{ __("Final check") }}</span>
					<div v-for="row in finalCheck" :key="row.item" class="check-row">
						<span class="check-name">{{ componentLabel(row.item) || row.item }}</span>
						<span class="muted">{{ itemName(row.item) }}</span>
						<div class="seg">
							<button type="button" :class="{ on: row.condition === 'Good' }" @click="row.condition = 'Good'">{{ __("Good") }}</button>
							<button type="button" :class="{ on: row.condition === 'Needs Repair', bad: row.condition === 'Needs Repair' }" @click="row.condition = 'Needs Repair'">
								{{ __("Needs Repair") }}
							</button>
						</div>
						<input v-if="row.condition === 'Needs Repair'" v-model="row.notes" class="input check-note" :placeholder="__('Note')" />
					</div>
				</div>
			</div>
		</div>
		<footer class="foot">
			<button class="btn btn-back" type="button" @click="backToQueue">{{ __("Back") }}</button>
			<p class="error">{{ busy ? __("Finishing") : error }}</p>
			<button class="btn btn-primary btn-final" type="button" :disabled="busy" @click="finish">{{ __("Finish maintenance") }}</button>
		</footer>
	</section>
</template>

<script setup>
import { computed, reactive, ref } from "vue"
import { __, componentLabel, formatKm, statusLabel } from "../translate.js"
import { api, errorText } from "../api.js"
import { backToQueue, store } from "../store.js"
import PlateChip from "../components/PlateChip.vue"

const vehicle = computed(() => store.checklist.vehicle)
const replaced = store.checklist.components.filter((row) => row.ticked)
const finalCheck = reactive(
	store.checklist.final_check.length
		? store.checklist.final_check.map((row) => Object.assign({}, row))
		: replaced.map((row) => ({ item: row.component, condition: "Good", notes: "" }))
)
const busy = ref(false)
const error = ref("")

function itemName(component) {
	const row = replaced.find((r) => r.component === component)
	const item = row && row.items.find((i) => i.item_code === row.item)
	return item ? item.item_name + " × " + row.qty : ""
}
async function finish() {
	if (finalCheck.some((row) => row.condition === "Needs Repair" && !row.notes)) {
		error.value = __("Add a note to every row that needs repair")
		return
	}
	busy.value = true
	error.value = ""
	try {
		store.result = await api.finish(store.visit.maintenance, JSON.stringify(finalCheck))
		store.step = "done"
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
</script>
