<template>
	<section class="screen">
		<div class="pane">
			<h1>{{ __("Items and parts") }}</h1>
			<p v-if="!store.checklist" class="empty">{{ error || __("Loading") }}</p>
			<template v-else>
				<div class="tiles">
					<button
						v-for="row in store.checklist.components"
						:key="row.component"
						class="tile"
						:class="['tile-' + row.state, { ticked: row.ticked }]"
						type="button"
						:aria-pressed="row.ticked ? 'true' : 'false'"
						@click="row.ticked = !row.ticked"
					>
						<span class="tile-check">{{ row.ticked ? "✓" : "" }}</span>
						<span class="tile-name">{{ componentLabel(row.component) }}</span>
						<span class="pill" :class="'pill-' + tone[row.state]">{{ stateText[row.state] }}</span>
						<span class="tile-due">{{ dueLine(row) }}</span>
					</button>
				</div>
				<div class="parts">
					<div v-for="row in ticked" :key="row.component" class="part">
						<span class="part-name">{{ componentLabel(row.component) }}</span>
						<select v-model="row.item" class="input part-item">
							<option v-for="item in row.items" :key="item.item_code" :value="item.item_code">
								{{ item.item_name }} · {{ __("Stock") }} {{ item.stock }} {{ item.stock_uom }}
							</option>
						</select>
						<div class="stepper" dir="ltr">
							<button class="step-btn" type="button" @click="row.qty = Math.max(step(row), row.qty - step(row))">−</button>
							<span class="step-val">{{ row.qty }}</span>
							<button class="step-btn" type="button" @click="row.qty = row.qty + step(row)">+</button>
						</div>
					</div>
				</div>
			</template>
		</div>
		<footer class="foot">
			<button class="btn btn-back" type="button" @click="store.step = 'odometer'">{{ __("Back") }}</button>
			<p class="error">{{ store.checklist ? error : "" }}</p>
			<button class="btn btn-primary" type="button" :disabled="!store.checklist" @click="next">{{ __("Next") }}</button>
		</footer>
	</section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue"
import { __, componentLabel, formatKm, isolate } from "../translate.js"
import { api, errorText } from "../api.js"
import { store } from "../store.js"

const error = ref("")
const tone = { overdue: "bad", soon: "warn", ok: "ok" }
const stateText = { overdue: __("Overdue"), soon: __("Due soon"), ok: __("Good") }
const ticked = computed(() => (store.checklist ? store.checklist.components.filter((row) => row.ticked) : []))

function step(row) {
	return row.component === "Oil" ? 0.5 : 1
}
function dueLine(row) {
	if (row.due_km) return __("Due at {0}", [formatKm(row.due_km)])
	if (row.due_date) return __("Due on {0}", [isolate(row.due_date)])
	return __("No schedule")
}
function next() {
	if (!ticked.value.length) {
		error.value = __("Select at least one component")
		return
	}
	const short = ticked.value.find((row) => !row.item || row.qty <= 0)
	if (short) {
		error.value = __("Choose an item for {0}", [componentLabel(short.component)])
		return
	}
	store.step = "photos"
}
onMounted(async () => {
	if (store.checklist) return
	try {
		store.checklist = await api.checklist(store.visit.maintenance, store.odometer)
	} catch (e) {
		error.value = errorText(e)
	}
})
</script>
