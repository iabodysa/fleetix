<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { api, errorText } from "../../api.js"
import { __ } from "../../i18n.js"
import BigButton from "../../components/BigButton.vue"
import PartRow from "../../components/PartRow.vue"
import PlateChip from "../../components/PlateChip.vue"
import "./store.css"

const PAGE = 20
const REFRESH_MS = 15000
const requests = ref([])
const loading = ref(false)
const more = ref(false)
const error = ref("")
let timer = null

async function load(start) {
	loading.value = true
	try {
		const rows = await api.purchaseRequests(start)
		requests.value = start ? requests.value.concat(rows) : rows
		more.value = rows.length === PAGE
	} catch (e) {
		error.value = errorText(e)
	} finally {
		loading.value = false
	}
}
onMounted(() => {
	load(0)
	timer = setInterval(() => requests.value.length <= PAGE && load(0), REFRESH_MS)
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
	<div class="page">
		<div class="screen">
			<h1 class="screen-title">{{ __("Purchase requests") }}</h1>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<p v-if="loading && !requests.length" class="store-hint">{{ __("Loading") }}</p>
			<p v-else-if="!requests.length" class="store-hint">{{ __("No purchase requests") }}</p>
			<section v-for="request in requests" :key="request.name" class="store-list">
				<PlateChip v-if="request.plate" :plate="request.plate" size="sm" />
				<PartRow v-for="(row, index) in request.items" :key="index" :name="row.item_name" :image="row.image || ''" :facts="[{ label: __('Qty'), value: row.qty }]" />
			</section>
			<BigButton v-if="more" icon="plus" tone="soft" :label="__('Load more')" :busy="loading" @press="load(requests.length)" />
		</div>
	</div>
</template>
