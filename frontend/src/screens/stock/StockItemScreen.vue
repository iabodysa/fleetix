<script setup>
import { onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { go, store } from "../../store/index.js"
import BigButton from "../../components/BigButton.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const item = ref(null)
const error = ref("")

onMounted(() => {
	api.stockItem(store.stock.item).then(
		(found) => (item.value = found),
		(e) => (error.value = errorText(e)),
	)
})
</script>

<template>
	<ScreenFrame :title="item ? item.item_name : store.stock.item" v-model:error="error">
		<template #meta>
			<span class="muted ltr">{{ store.stock.item }}</span>
		</template>
		<p v-if="!item && !error" class="queue-loading">{{ __("Loading") }}</p>
		<div v-if="item" class="stock-item">
			<img v-if="item.image" class="card stock-item-image" :src="item.image" :alt="item.item_name" />
			<div class="stock-item-body">
				<dl class="facts">
					<div v-if="item.item_group">
						<dt>{{ __("Item Group") }}</dt>
						<dd>{{ __(item.item_group) }}</dd>
					</div>
				</dl>
				<section v-if="item.vehicle_models.length" class="stock-item-section">
					<h2>{{ __("Vehicle Models") }}</h2>
					<div class="stock-item-pills">
						<span v-for="model in item.vehicle_models" :key="model" class="pill tone-quiet">{{ model }}</span>
					</div>
				</section>
				<table class="card stock-item-bins">
					<thead>
						<tr>
							<th>{{ __("Warehouse") }}</th>
							<th>{{ __("Qty") }}</th>
						</tr>
					</thead>
					<tbody>
						<tr v-for="row in item.bins" :key="row.warehouse">
							<td>{{ row.warehouse }}</td>
							<td class="stock-item-qty">{{ row.qty }}</td>
						</tr>
					</tbody>
				</table>
				<section v-if="item.barcodes.length" class="stock-item-section">
					<h2>{{ __("Barcodes") }}</h2>
					<div class="stock-item-pills">
						<span v-for="code in item.barcodes" :key="code" class="pill tone-quiet ltr">{{ code }}</span>
					</div>
				</section>
			</div>
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('stock')" />
		</template>
	</ScreenFrame>
</template>

<style>
.stock-item {
	display: grid;
	grid-template-columns: minmax(0, 22rem) minmax(0, 1fr);
	gap: var(--s5);
	align-items: start;
}
.stock-item-image {
	width: 100%;
	height: auto;
	padding: 0;
	object-fit: contain;
	background: var(--surface);
}
.stock-item-body {
	display: flex;
	flex-direction: column;
	gap: var(--s4);
	min-width: 0;
}
.stock-item-section h2 {
	margin: 0 0 var(--s2);
	font-size: var(--t-sm);
	color: var(--ink-2);
	font-weight: 700;
}
.stock-item-pills {
	display: flex;
	flex-wrap: wrap;
	gap: var(--s2);
}
.stock-item-bins {
	width: 100%;
	padding: 0;
	border-collapse: collapse;
	overflow: hidden;
}
.stock-item-bins th,
.stock-item-bins td {
	padding: var(--s2) var(--s3);
	text-align: start;
}
.stock-item-bins th {
	color: var(--ink-2);
	font-size: var(--t-sm);
	font-weight: 700;
}
.stock-item-bins td {
	border-top: 1px solid var(--line);
	font-size: var(--t-lg);
	font-weight: 700;
}
.stock-item-qty {
	width: 6rem;
}
@media (max-width: 760px) {
	.stock-item {
		grid-template-columns: minmax(0, 1fr);
	}
}
</style>
