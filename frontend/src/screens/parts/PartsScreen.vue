<script setup>
import { computed, onMounted, ref } from "vue"
import { __, componentLabel, formatKm, isolate } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { offerUndo } from "../../composables/useUndo.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import IconTile from "../../components/IconTile.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const error = ref("")
const TONE = { overdue: "problem", soon: "wait", ok: "done" }
const STATE_TEXT = { overdue: __("Overdue"), soon: __("Due soon"), ok: __("Good") }
const ticked = computed(() => (store.checklist ? store.checklist.components.filter((row) => row.ticked) : []))

function step(row) {
	return row.component === "Oil" ? 0.5 : 1
}
function dueLine(row) {
	if (row.due_km) return __("Due at {0}", [formatKm(row.due_km)])
	if (row.due_date) return __("Due on {0}", [isolate(row.due_date)])
	return __("No schedule")
}
function toggle(row) {
	if (!row.ticked) {
		row.ticked = true
		if (!row.item && row.items.length === 1) row.item = row.items[0].item_code
		return
	}
	row.ticked = false
	offerUndo(__("{0} removed", [componentLabel(row.component)]), () => (row.ticked = true))
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
	go("damage")
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

<template>
	<ScreenFrame :title="__('Items and parts')" :error="error">
		<p v-if="!store.checklist" class="muted">{{ __("Loading") }}</p>
		<template v-else>
			<div class="tile-grid">
				<IconTile
					v-for="row in store.checklist.components"
					:key="row.component"
					:icon="row.component"
					:label="componentLabel(row.component)"
					:note="dueLine(row)"
					:tone="TONE[row.state]"
					:pressed="row.ticked"
					@press="toggle(row)"
				>
					<span class="pill" :class="'tone-' + TONE[row.state]">{{ STATE_TEXT[row.state] }}</span>
				</IconTile>
			</div>
			<div v-for="row in ticked" :key="row.component" class="card part">
				<h2 class="part-name"><AppIcon :name="row.component" />{{ componentLabel(row.component) }}</h2>
				<div class="part-items">
					<button
						v-for="item in row.items"
						:key="item.item_code"
						class="part-item"
						:class="{ pressed: row.item === item.item_code }"
						type="button"
						:aria-pressed="row.item === item.item_code ? 'true' : 'false'"
						@click="row.item = item.item_code"
					>
						<span class="part-item-name">{{ item.item_name }}</span>
						<span class="muted">{{ __("Stock") }} <span class="ltr">{{ item.stock }}</span> {{ item.stock_uom }}</span>
					</button>
				</div>
				<div class="stepper ltr">
					<button class="stepper-button" type="button" :aria-label="__('Less')" @click="row.qty = Math.max(step(row), row.qty - step(row))"><AppIcon name="minus" size="lg" /></button>
					<span class="stepper-value">{{ row.qty }}</span>
					<button class="stepper-button" type="button" :aria-label="__('More')" @click="row.qty = row.qty + step(row)"><AppIcon name="plus" size="lg" /></button>
				</div>
			</div>
		</template>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('odometer')" />
		</template>
		<template #primary>
			<BigButton icon="next" :label="__('Next')" :disabled="!store.checklist" @press="next" />
		</template>
	</ScreenFrame>
</template>

<style>
.part {
	display: grid;
	gap: var(--s3);
	margin-top: var(--s4);
	padding: var(--s4);
}
.part-name {
	display: flex;
	align-items: center;
	gap: var(--s2);
}
.part-items {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr));
	gap: var(--s2);
}
.part-item {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	gap: var(--s1);
	min-height: var(--button);
	padding: var(--s3);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface);
	text-align: start;
}
.part-item.pressed {
	border-color: var(--primary);
	box-shadow: inset 0 0 0 2px var(--primary);
}
.part-item-name {
	font-weight: 800;
}
.stepper {
	display: flex;
	align-items: center;
	gap: var(--s3);
}
.stepper-button {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: var(--button);
	height: var(--button);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface-2);
}
.stepper-value {
	min-width: 4rem;
	font-size: var(--t-xl);
	font-weight: 800;
	text-align: center;
}
</style>
