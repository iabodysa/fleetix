<script setup>
import PlateChip from "./PlateChip.vue"

defineProps({ vehicle: { type: Object, required: true } })
</script>

<template>
	<section class="card vehicle">
		<PlateChip :plate="vehicle.plate" size="lg" />
		<dl>
			<template v-if="vehicle.model">
				<dt>{{ __("Car") }}</dt>
				<dd>{{ vehicle.model }}</dd>
			</template>
			<template v-if="vehicle.driver_name">
				<dt>{{ __("Driver") }}</dt>
				<dd>{{ vehicle.driver_name }}</dd>
			</template>
			<template v-if="vehicle.project_name">
				<dt>{{ __("Project") }}</dt>
				<dd>{{ vehicle.project_name }}</dd>
			</template>
		</dl>
	</section>
</template>

<style scoped>
.vehicle {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 16px;
}
dl {
	display: grid;
	grid-template-columns: auto 1fr;
	gap: 4px 12px;
	margin: 0;
	min-width: 0;
	flex: 1 1 180px;
}
dt {
	color: var(--ink-2);
}
dd {
	margin: 0;
	font-weight: 700;
	overflow-wrap: anywhere;
}
</style>
