<script setup>
import { ref } from "vue"
import { __ } from "../i18n/index.js"
import { api, errorText } from "../api.js"
import { offerUndo } from "../composables/useUndo.js"
import { store } from "../store/index.js"
import AppIcon from "./AppIcon.vue"
import BigButton from "./BigButton.vue"
import QtyStepper from "./QtyStepper.vue"
import StockChoice from "./StockChoice.vue"

defineProps({ requested: { type: Object, default: () => ({}) } })
const emit = defineEmits(["request", "error"])
const found = ref([])
let asked = 0

function lines() {
	if (!store.checklist.parts) store.checklist.parts = []
	return store.checklist.parts
}
async function search(txt) {
	const no = ++asked
	if (txt.trim().length < 2) return (found.value = [])
	try {
		const rows = await api.stockSearch(txt.trim(), "", 0)
		if (no === asked) found.value = rows.map((row) => ({ item_code: row.item_code, item_name: row.item_name, image: row.image, stock: row.qty }))
	} catch (e) {
		emit("error", errorText(e))
	}
}
function add(item) {
	const line = lines().find((row) => row.item_code === item.item_code)
	if (line) line.qty = Math.min(line.qty + 1, item.stock)
	else lines().push(Object.assign({}, item, { qty: 1 }))
}
function remove(index) {
	const [line] = lines().splice(index, 1)
	offerUndo(__("{0} removed", [line.item_name]), () => lines().splice(index, 0, line))
}
</script>

<template>
	<section class="card part">
		<h2 class="part-name"><AppIcon name="parts" />{{ __("Other parts") }}</h2>
		<div v-for="(line, index) in store.checklist.parts || []" :key="line.item_code" class="other-line">
			<img v-if="line.image" class="other-line-thumb" :src="line.image" :alt="line.item_name" loading="lazy" />
			<span class="part-item-name">{{ line.item_name }}</span>
			<QtyStepper v-model="line.qty" :unit="__('piece')" :min="1" :max="line.stock > 0 ? line.stock : 0" />
			<BigButton icon="close" tone="quiet" :label="__('Remove')" @press="remove(index)" />
		</div>
		<input class="part-search" type="search" :placeholder="__('Search items')" autocomplete="off" @input="search($event.target.value)" />
		<div class="part-items">
			<StockChoice v-for="item in found" :key="item.item_code" :item="item" :requested="!!requested[item.item_code]" @pick="add(item)" @request="$emit('request', item)" />
		</div>
	</section>
</template>

<style>
.other-line {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: var(--s3);
	padding: var(--s3) 0;
	border-bottom: 1px solid var(--line);
}
.other-line-thumb {
	width: 4rem;
	height: 4rem;
	border-radius: var(--r-md);
	background: var(--surface-2);
	object-fit: contain;
}
</style>
