<script setup>
import AppIcon from "./AppIcon.vue"
import PlateChip from "./PlateChip.vue"

defineProps({
	plate: { type: String, default: "" },
	vehicles: { type: Number, default: 0 },
	inVisit: Boolean,
	online: Boolean,
	printer: Boolean,
	language: { type: String, required: true },
})
defineEmits(["vehicles", "close", "language", "menu"])
</script>

<template>
	<header class="app-header">
		<div class="app-header-start">
			<PlateChip v-if="plate" :plate="plate" size="sm" />
			<img v-else class="app-header-brand" src="/assets/fleetix/images/fleetix-logo.svg" alt="Fleetix" />
		</div>
		<div class="app-header-end">
			<span class="app-header-state" :class="online ? 'tone-done' : 'tone-problem'" :title="online ? __('Online') : __('Offline')">
				<AppIcon :name="online ? 'online' : 'offline'" />
			</span>
			<span v-if="printer" class="app-header-state tone-done" :title="__('Printer')"><AppIcon name="printer" /></span>
			<button class="app-header-button" type="button" :aria-label="__('Language')" @click="$emit('language')">
				<AppIcon name="language" />
				<span>{{ language }}</span>
			</button>
			<template v-if="inVisit">
				<button class="app-header-button" type="button" @click="$emit('vehicles')">
					<AppIcon name="vehicle" />
					<b class="ltr">{{ vehicles }}</b>
				</button>
				<button class="app-header-button" type="button" :aria-label="__('Close')" @click="$emit('close')">
					<AppIcon name="close" />
				</button>
			</template>
			<button v-else class="app-header-button" type="button" :aria-label="__('Menu')" @click="$emit('menu')">
				<AppIcon name="user" />
			</button>
		</div>
	</header>
</template>

<style>
.app-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: var(--s3);
	min-height: var(--button);
}
.app-header-start,
.app-header-end {
	display: flex;
	align-items: center;
	gap: var(--s2);
	min-width: 0;
}
.app-header-brand {
	height: 2.25rem;
}
.app-header-state {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: var(--tap);
	height: var(--tap);
	border-radius: var(--r-md);
}
.app-header-button {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	gap: var(--s2);
	min-width: var(--tap);
	min-height: var(--tap);
	padding: 0 var(--s3);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface);
	font-weight: 700;
}
@media (max-width: 480px) {
	.app-header-button span {
		display: none;
	}
}
</style>
