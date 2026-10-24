<script setup>
import { computed, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import LastFindings from "../../components/LastFindings.vue"
import PlateChip from "../../components/PlateChip.vue"
import QtyStepper from "../../components/QtyStepper.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const walkin = store.walkin
const error = ref("")
const kind = ref(1)
const text = ref("")
const found = ref([])
const total = computed(() => walkin.items.reduce((sum, row) => sum + row.qty * row.rate, 0))

function money(value) {
	return Number(value || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
async function search() {
	const txt = text.value.trim()
	if (txt.length < 2) return (found.value = [])
	try {
		found.value = (await api.searchItems(txt, kind.value)).map((r) => ({ item_code: r.value, item_name: r.description || r.value }))
	} catch (e) {
		error.value = errorText(e)
	}
}
function setKind(value) {
	kind.value = value
	search()
}
async function pick(item) {
	const row = walkin.items.find((r) => r.item_code === item.item_code)
	if (row) return (row.qty += 1)
	try {
		const [rate] = await api.itemRates([item.item_code])
		if (rate) walkin.items.push(Object.assign(rate, { qty: 1 }))
	} catch (e) {
		error.value = errorText(e)
	}
}
function setQty(row, qty) {
	if (qty > 0) row.qty = qty
	else walkin.items.splice(walkin.items.indexOf(row), 1)
}
function next() {
	if (!walkin.items.length) return (error.value = __("Add at least one item"))
	const unpriced = walkin.items.find((row) => !row.rate)
	if (unpriced) return (error.value = __("No selling price for {0}. Tell the accountant.", [unpriced.item_name]))
	const saved = {}
	walkin.checks.forEach((row) => (saved[row.kind + row.item] = row.condition))
	walkin.checks = walkin.items
		.filter((row) => row.is_stock_item)
		.map((row) => ({ kind: "part", item: row.item_code, label: row.item_name, note: row.qty + " " + row.unit, condition: saved["part" + row.item_code] || "" }))
		.concat(((walkin.setup && walkin.setup.service_checklist) || []).map((row) => ({ kind: "service", item: row.item, label: row.label, condition: saved["service" + row.item] || "" })))
	go("walkinCheck")
}
</script>

<template>
	<ScreenFrame :title="__('Items and labour')" v-model:error="error">
		<template #meta>
			<PlateChip :plate="walkin.plate" size="md" />
		</template>
		<div class="walkin-items">
			<LastFindings :last="walkin.last" />
			<div v-for="row in walkin.items" :key="row.item_code" class="card walkin-line">
				<span class="walkin-line-name">
					<AppIcon :name="row.is_stock_item ? 'item' : 'labour'" />
					<b>{{ row.item_name }}</b>
					<span v-if="!row.rate" class="pill tone-problem">{{ __("No price") }}</span>
				</span>
				<QtyStepper :model-value="row.qty" :unit="row.unit" :litres="!!row.litres" :packs="row.packs || []" @update:model-value="setQty(row, $event)" />
				<span class="walkin-money ltr">{{ money(row.qty * row.rate) }}</span>
			</div>
			<div v-if="walkin.items.length" class="card walkin-total">
				<b>{{ __("Total before VAT") }}</b>
				<span class="walkin-money ltr">{{ money(total) }}</span>
			</div>
		</div>
		<template #aside>
			<div class="walkin-find">
				<div class="findings-chips">
					<button type="button" class="chip" :class="{ pressed: kind === 1 }" @click="setKind(1)">{{ __("Parts") }}</button>
					<button type="button" class="chip" :class="{ pressed: kind === 0 }" @click="setKind(0)">{{ __("Labour") }}</button>
				</div>
				<input v-model="text" class="walkin-input" type="search" :placeholder="__('Search items')" autocomplete="off" @input="search" />
				<button v-for="item in found" :key="item.item_code" type="button" class="part-item" @click="pick(item)">
					<span class="part-item-name">{{ item.item_name }}</span>
					<span class="muted ltr">{{ item.item_code }}</span>
				</button>
			</div>
		</template>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('walkin')" />
		</template>
		<template #primary>
			<BigButton icon="next" :label="__('Next')" @press="next" />
		</template>
	</ScreenFrame>
</template>

<style>
.walkin-items,
.walkin-find {
	display: grid;
	gap: var(--s3);
	align-content: start;
}
.walkin-line {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: var(--s3);
	padding: var(--s3) var(--s4);
}
.walkin-line-name {
	display: flex;
	flex: 1;
	align-items: center;
	gap: var(--s2);
	min-width: 12rem;
}
.walkin-money {
	min-width: 6rem;
	font-size: var(--t-lg);
	font-weight: 800;
	text-align: end;
}
.walkin-total {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: var(--s4);
}
</style>
