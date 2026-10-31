<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { problem, success } from "../../composables/useFeedback.js"
import { backHome, go, store } from "../../store/index.js"
import BarcodeInput from "../../components/BarcodeInput.vue"
import BigButton from "../../components/BigButton.vue"
import EmptyState from "../../components/EmptyState.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const PAGE = 20
const SEARCH_MS = 250
const rows = ref([])
const models = ref([])
const loading = ref(false)
const more = ref(false)
const error = ref("")
let timer = null
let asked = 0

const searched = computed(() => [store.stock.query.trim(), store.stock.model])

function search(start) {
	const ticket = ++asked
	loading.value = true
	api.stockSearch(store.stock.query.trim(), store.stock.model, start).then(
		(found) => {
			if (ticket !== asked) return
			rows.value = start ? rows.value.concat(found) : found
			more.value = found.length === PAGE
			loading.value = false
		},
		(e) => {
			if (ticket !== asked) return
			error.value = errorText(e)
			loading.value = false
		},
	)
}
function open(itemCode) {
	store.stock.item = itemCode
	go("stockItem")
}
async function scanned(key, raw) {
	try {
		const found = await api.stockScan(raw || key)
		if (found && found.item_code) {
			error.value = ""
			success()
			open(found.item_code)
			return
		}
		error.value = __("No parts found")
	} catch (e) {
		error.value = errorText(e)
	}
	problem()
}
watch(searched, () => {
	clearTimeout(timer)
	timer = setTimeout(() => search(0), SEARCH_MS)
})
onMounted(() => {
	search(0)
	api.stockModels().then((found) => (models.value = found || []), (e) => (error.value = errorText(e)))
})
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
	<ScreenFrame :title="__('Stock')" v-model:error="error">
		<div class="stock-list">
			<p v-if="loading && !rows.length" class="queue-loading">{{ __("Loading") }}</p>
			<EmptyState v-else-if="!rows.length" :label="__('No parts found')" />
			<button v-for="row in rows" :key="row.item_code" class="card stock-row" type="button" @click="open(row.item_code)">
				<img v-if="row.image" class="stock-thumb" :src="row.image" :alt="row.item_name" loading="lazy" />
				<span class="stock-row-text">
					<span class="stock-row-name">{{ row.item_name }}</span>
					<span class="muted ltr">{{ row.item_code }}</span>
					<dl class="facts stock-row-facts">
						<div>
							<dt>{{ __("Qty") }}</dt>
							<dd>{{ row.qty }}</dd>
						</div>
						<div v-if="row.warehouse">
							<dt>{{ __("Warehouse") }}</dt>
							<dd>{{ row.warehouse }}</dd>
						</div>
					</dl>
				</span>
			</button>
			<BigButton v-if="more" class="stock-more" icon="down" tone="quiet" :label="__('Load more')" :busy="loading" block @press="search(rows.length)" />
		</div>
		<template #aside>
			<div class="stock-find">
				<BarcodeInput :idle-text="__('Scan the part barcode')" :ready-text="__('Ready to scan. Point the scanner at the part barcode')" @scan="scanned" />
				<label class="stock-field">
					<span>{{ __("Search parts") }}</span>
					<input v-model="store.stock.query" class="stock-input" type="search" autocomplete="off" />
				</label>
				<div v-if="models.length" class="stock-models">
					<button class="pill stock-model" :class="{ 'tone-done': !store.stock.model }" type="button" @click="store.stock.model = ''">{{ __("All models") }}</button>
					<button
						v-for="model in models"
						:key="model"
						class="pill stock-model"
						:class="{ 'tone-done': store.stock.model === model }"
						type="button"
						@click="store.stock.model = model"
					>
						{{ model }}
					</button>
				</div>
			</div>
		</template>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="backHome" />
		</template>
	</ScreenFrame>
</template>

<style>
.stock-list {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(17rem, 1fr));
	gap: var(--s3);
}
.stock-list .empty-state,
.stock-more {
	grid-column: 1 / -1;
}
.stock-row {
	display: flex;
	align-items: flex-start;
	gap: var(--s3);
	padding: var(--s3);
	text-align: start;
}
.stock-thumb {
	flex: none;
	width: 5rem;
	height: 5rem;
	border-radius: var(--r-md);
	background: var(--surface-2);
	object-fit: cover;
}
.stock-row-text {
	display: flex;
	flex-direction: column;
	gap: var(--s1);
	min-width: 0;
}
.stock-row-name {
	font-size: var(--t-lg);
	font-weight: 800;
}
.stock-row-facts {
	gap: var(--s2) var(--s4);
}
.stock-find {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
}
.stock-field {
	display: grid;
	gap: var(--s2);
	font-weight: 800;
}
.stock-input {
	min-height: var(--tap);
	padding: 0 var(--s3);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface);
	font: inherit;
	font-size: var(--t-lg);
}
.stock-models {
	display: flex;
	flex-wrap: wrap;
	gap: var(--s2);
}
.stock-model {
	border: 2px solid var(--line);
	background: var(--surface);
	font: inherit;
	font-weight: 700;
}
.stock-model.tone-done {
	border-color: var(--done);
}
</style>
