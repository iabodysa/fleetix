<script setup>
import { computed, ref } from "vue"
import { __, componentLabel, formatKm, statusLabel } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { backToQueue, go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import PlateChip from "../../components/PlateChip.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const REASONS = { Leak: __("Leak"), Noise: __("Noise"), Loose: __("Loose"), Worn: __("Worn") }
const vehicle = computed(() => store.checklist.vehicle)
const replaced = store.checklist.components.filter((row) => row.ticked)
if (!store.checklist.final_check.length) {
	store.checklist.final_check = replaced.map((row) => ({ item: row.component, condition: "Good", notes: "" }))
}
const finalCheck = store.checklist.final_check
const busy = ref(false)
const error = ref("")

function itemName(component) {
	const row = replaced.find((r) => r.component === component)
	const item = row && row.items.find((i) => i.item_code === row.item)
	return item ? item.item_name + " × " + row.qty : ""
}
async function finish() {
	if (finalCheck.some((row) => row.condition === "Needs Repair" && !row.notes)) {
		error.value = __("Choose what is wrong for every row that needs repair")
		return
	}
	busy.value = true
	error.value = ""
	try {
		store.result = await api.finish(store.visit.maintenance, JSON.stringify(finalCheck))
		go("done")
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
</script>

<template>
	<ScreenFrame :title="__('Final check')" :error="error">
		<template #meta>
			<span class="pill tone-done">{{ statusLabel(store.checklist.status) }}</span>
		</template>
		<div class="review">
			<div class="card review-vehicle">
				<PlateChip :plate="vehicle.plate" size="lg" />
				<div>
					<p class="review-model">{{ vehicle.model }}</p>
					<p class="muted">{{ formatKm(store.checklist.odometer) }}</p>
				</div>
			</div>
			<div v-for="row in finalCheck" :key="row.item" class="card review-row">
				<div class="review-name">
					<AppIcon :name="row.item" />
					<span>
						<b>{{ componentLabel(row.item) || row.item }}</b>
						<span class="muted review-item">{{ itemName(row.item) }}</span>
					</span>
				</div>
				<div class="review-choice">
					<button type="button" class="review-option" :class="{ 'tone-done': row.condition === 'Good' }" @click="(row.condition = 'Good'), (row.notes = '')">
						<AppIcon name="good" />{{ __("Good") }}
					</button>
					<button type="button" class="review-option" :class="{ 'tone-problem': row.condition === 'Needs Repair' }" @click="row.condition = 'Needs Repair'">
						<AppIcon name="problem" />{{ __("Needs Repair") }}
					</button>
				</div>
				<div v-if="row.condition === 'Needs Repair'" class="review-reasons">
					<button
						v-for="(label, reason) in REASONS"
						:key="reason"
						type="button"
						class="review-option"
						:class="{ 'tone-problem': row.notes === reason }"
						:aria-pressed="row.notes === reason ? 'true' : 'false'"
						@click="row.notes = reason"
					>
						{{ label }}
					</button>
				</div>
			</div>
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="backToQueue" />
		</template>
		<template #primary>
			<BigButton icon="done" tone="done" :label="busy ? __('Finishing') : __('Finish maintenance')" :busy="busy" @press="finish" />
		</template>
	</ScreenFrame>
</template>

<style>
.review {
	display: grid;
	gap: var(--s3);
}
.review-vehicle {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: var(--s4);
	padding: var(--s4);
}
.review-model {
	font-size: var(--t-lg);
	font-weight: 800;
}
.review-row {
	display: grid;
	gap: var(--s3);
	padding: var(--s4);
}
.review-name {
	display: flex;
	align-items: center;
	gap: var(--s3);
}
.review-item {
	display: block;
	font-size: var(--t-sm);
}
.review-choice,
.review-reasons {
	display: flex;
	flex-wrap: wrap;
	gap: var(--s2);
}
.review-option {
	display: inline-flex;
	align-items: center;
	gap: var(--s2);
	min-height: var(--tap);
	padding: 0 var(--s4);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface);
	font-weight: 800;
}
.review-option.tone-done {
	border-color: var(--done);
}
.review-option.tone-problem {
	border-color: var(--problem);
}
</style>
