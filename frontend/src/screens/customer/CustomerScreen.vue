<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { CUSTOMER_KEY, readCustomerView } from "../../composables/useCustomerDisplay.js"
import PlateChip from "../../components/PlateChip.vue"

const view = ref(readCustomerView())

function refresh(event) {
	if (event.key === CUSTOMER_KEY) view.value = readCustomerView()
}
onMounted(() => window.addEventListener("storage", refresh))
onBeforeUnmount(() => window.removeEventListener("storage", refresh))
</script>

<template>
	<section class="customer">
		<img class="customer-brand" src="/assets/fleetix/images/fleetix-logo.svg" alt="Fleetix" />
		<template v-if="view && view.plate">
			<PlateChip :plate="view.plate" size="xl" />
			<p class="customer-status" :class="'tone-' + (view.tone || 'wait')">{{ view.status }}</p>
			<p v-if="view.amount" class="customer-amount ltr">{{ view.amount }}</p>
		</template>
		<p v-else class="customer-welcome">{{ __("Welcome") }}</p>
	</section>
</template>

<style>
.customer {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: var(--s6);
	min-height: 100%;
	padding: var(--s6);
	background: var(--brand);
	color: var(--on-brand);
	text-align: center;
}
.customer-brand {
	height: 3.5rem;
}
.customer-status {
	padding: var(--s3) var(--s6);
	border-radius: var(--r-pill);
	font-size: var(--t-xxl);
	font-weight: 800;
}
.customer-amount {
	font-size: var(--t-display);
	font-weight: 800;
	color: var(--gold);
	font-variant-numeric: tabular-nums;
}
.customer-welcome {
	font-size: var(--t-display);
	font-weight: 800;
}
</style>
