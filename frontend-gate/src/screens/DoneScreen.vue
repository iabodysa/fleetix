<script setup>
import { computed } from "vue"
import { __ } from "../i18n.js"
import { nextCar, store } from "../store.js"
import BigButton from "../components/BigButton.vue"
import PlateChip from "../components/PlateChip.vue"
import SuccessCheck from "../components/SuccessCheck.vue"

const title = computed(() => (store.result.doctype === "Maintenance" ? __("Sent to maintenance") : __("Sent to handover")))
</script>

<template>
	<div class="page">
		<div class="screen done">
			<SuccessCheck />
			<h1 class="screen-title">{{ title }}</h1>
			<PlateChip :plate="store.vehicle.plate" size="lg" />
			<p class="ref" dir="ltr">{{ store.result.name }}</p>
		</div>
		<div class="dock">
			<BigButton icon="car" :label="__('Next car')" @press="nextCar" />
		</div>
	</div>
</template>

<style scoped>
.done {
	align-items: center;
	text-align: center;
	justify-content: center;
	flex: 1;
}
.ref {
	color: var(--ink-2);
	font-weight: 600;
}
</style>
