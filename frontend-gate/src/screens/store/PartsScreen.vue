<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from "vue"
import { api, errorText } from "../../api.js"
import { __ } from "../../i18n.js"
import BigButton from "../../components/BigButton.vue"
import PartRow from "../../components/PartRow.vue"
import "./store.css"

const PAGE = 20
const SEARCH_MS = 250
const query = ref("")
const rows = ref([])
const loading = ref(false)
const more = ref(false)
const error = ref("")
let timer = null
let asked = 0

function facts(row) {
	const out = [{ label: __("Qty"), value: row.qty }]
	if (row.warehouse) out.push({ label: __("Warehouse"), value: row.warehouse })
	return out
}
async function search(start) {
	const ticket = ++asked
	loading.value = true
	try {
		const found = await api.stockSearch(query.value.trim(), start)
		if (ticket !== asked) return
		rows.value = start ? rows.value.concat(found) : found
		more.value = found.length === PAGE
		error.value = ""
	} catch (e) {
		if (ticket === asked) error.value = errorText(e)
	} finally {
		if (ticket === asked) loading.value = false
	}
}
watch(query, () => {
	clearTimeout(timer)
	timer = setTimeout(() => search(0), SEARCH_MS)
})
onMounted(() => search(0))
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
	<div class="page">
		<div class="screen">
			<h1 class="screen-title">{{ __("Spare parts") }}</h1>
			<label class="store-field">
				<span>{{ __("Search") }}</span>
				<input v-model="query" class="store-input" type="search" autocomplete="off" enterkeyhint="search" />
			</label>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<p v-if="loading && !rows.length" class="store-hint">{{ __("Loading") }}</p>
			<p v-else-if="!rows.length" class="store-hint">{{ __("No parts found") }}</p>
			<div class="store-list">
				<PartRow v-for="row in rows" :key="row.item_code" :name="row.item_name" :code="row.item_code" :image="row.image || ''" :facts="facts(row)" />
			</div>
			<BigButton v-if="more" icon="plus" tone="soft" :label="__('Load more')" :busy="loading" @press="search(rows.length)" />
		</div>
	</div>
</template>
