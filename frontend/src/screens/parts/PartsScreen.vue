<script setup>
import { computed, onMounted, reactive, ref } from "vue"
import { __, componentLabel, formatKm, isolate } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { offerUndo } from "../../composables/useUndo.js"
import { success } from "../../composables/useFeedback.js"
import { useCardProgress } from "../../composables/useCardProgress.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import CardProgress from "../../components/CardProgress.vue"
import BigButton from "../../components/BigButton.vue"
import IconTile from "../../components/IconTile.vue"
import LastFindings from "../../components/LastFindings.vue"
import OtherParts from "../../components/OtherParts.vue"
import StockChoice from "../../components/StockChoice.vue"
import QtyStepper from "../../components/QtyStepper.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const error = ref("")
const requested = reactive({})
const TONE = { overdue: "problem", soon: "wait", ok: "done" }
const STATE_TEXT = { overdue: __("Overdue"), soon: __("Due soon"), ok: __("Good") }
const ticked = computed(() => (store.checklist ? store.checklist.components.filter((row) => row.ticked) : []))

const FALLBACK_UNIT = { Oil: __("litre"), "Front Tires": __("tyre"), "Rear Tires": __("tyre") }
function chosen(row) {
	return row.items.concat(row.found || []).find((i) => i.item_code === row.item)
}
function unitOf(row) {
	const item = chosen(row)
	return (item && item.unit) || FALLBACK_UNIT[row.component] || __("piece")
}
function litresOf(row) {
	const item = chosen(row)
	return item && item.unit ? !!item.litres : row.component === "Oil"
}
const cards = computed(() =>
	ticked.value.map((row) => ({ key: row.component, label: componentLabel(row.component), icon: row.component, done: !!row.item && row.qty > 0 })),
)
const progress = useCardProgress(cards)
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
async function findItems(row, txt) {
	if (txt.trim().length < 2) return (row.found = [])
	try {
		const found = await api.stockSearch(txt.trim(), "", 0)
		row.found = found.map((r) => ({ item_code: r.item_code, item_name: r.item_name, image: r.image, stock: r.qty }))
	} catch (e) {
		error.value = errorText(e)
	}
}
function choices(row) {
	return row.items.length && !row.other ? row.items : row.found || []
}
function offRule(row) {
	return !!row.item && !row.items.some((i) => i.item_code === row.item)
}
function rowTone(row) {
	if (!row.item || !(row.qty > 0)) return "wait"
	if (offRule(row)) return "problem"
	return "done"
}
async function request(item, qty) {
	error.value = ""
	try {
		await api.requestPurchase(store.visit.maintenance, item.item_code, qty || 1)
		requested[item.item_code] = true
		success()
	} catch (e) {
		error.value = errorText(e)
	}
}
function next() {
	if (!ticked.value.length && !(store.checklist.parts || []).length) {
		error.value = __("Select at least one component")
		return
	}
	if (progress.guard()) return
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
	<ScreenFrame :title="__('Items and parts')" v-model:error="error">
		<p v-if="!store.checklist" class="muted">{{ __("Loading") }}</p>
		<template v-else>
			<CardProgress :items="cards" @show="progress.show" />
			<LastFindings :last="store.checklist.last_findings" />
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
			<div v-for="row in ticked" :key="row.component" class="card part" :data-card="row.component">
				<h2 class="part-name"><span class="part-dot" :class="'tone-' + rowTone(row)"></span><AppIcon :name="row.component" />{{ componentLabel(row.component) }}</h2>
				<input
					v-if="!row.items.length || row.other"
					class="part-search"
					type="search"
					:placeholder="__('Search items')"
					autocomplete="off"
					@input="findItems(row, $event.target.value)"
				/>
				<div class="part-items">
					<StockChoice
						v-for="item in choices(row)"
						:key="item.item_code"
						:item="item"
						:pressed="row.item === item.item_code"
						:other="!!(row.items.length && row.other)"
						:requested="!!requested[item.item_code]"
						@pick="row.item = item.item_code"
						@request="request(item, row.qty)"
					/>
				</div>
				<BigButton v-if="row.items.length" icon="item" tone="quiet" :label="row.other ? __('Back') : __('Other item')" @press="row.other = !row.other" />
				<QtyStepper v-if="row.max_qty !== 1" v-model="row.qty" :unit="unitOf(row)" :litres="litresOf(row)" :packs="(chosen(row) || {}).packs || []" :max="row.max_qty || 0" :min="litresOf(row) ? 0.5 : 1" />
			</div>
			<OtherParts :requested="requested" @request="request($event, 1)" @error="error = $event" />
		</template>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('odometer')" />
		</template>
		<template #primary>
			<BigButton icon="next" :label="progress.nextLabel(__('Next'))" :disabled="!store.checklist" @press="next" />
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
.part-search {
	width: 100%;
	min-height: var(--button);
	margin-bottom: var(--s3);
	padding: 0 var(--s4);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface-2);
	font-size: var(--t-lg);
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
.part-item-other,
.part-item-other.pressed {
	border-color: var(--problem);
	box-shadow: inset 0 0 0 2px var(--problem);
}
.part-dot {
	width: 1rem;
	height: 1rem;
	flex: none;
	border-radius: 50%;
	background: currentColor;
}
.part-item-name {
	font-weight: 800;
}
</style>
