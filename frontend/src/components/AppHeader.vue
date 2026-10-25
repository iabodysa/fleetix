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
	user: { type: String, default: "" },
})
defineEmits(["vehicles", "close", "language", "menu", "profile"])
</script>

<template>
	<header class="app-header">
		<div class="app-header-start">
			<button v-if="plate && inVisit" class="app-header-plate" type="button" :aria-label="__('Vehicle')" @click="$emit('profile')"><PlateChip :plate="plate" size="sm" /></button>
			<PlateChip v-else-if="plate" :plate="plate" size="sm" />
			<img v-else class="app-header-brand" src="/assets/fleetix/images/fleetix-logo.svg" alt="Fleetix" />
			<span v-if="user" class="app-header-user" :title="user"><AppIcon name="user" /><span class="app-header-user-name">{{ user }}</span></span>
		</div>
		<h1 class="app-header-title">{{ __("Fleetix Maintenance") }}</h1>
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
.app-header-plate {
	padding: 0;
	border: 0;
	background: none;
}
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
	flex: 1 1 0;
	align-items: center;
	gap: var(--s2);
	min-width: 0;
}
.app-header-end {
	justify-content: flex-end;
}
.app-header-title {
	flex: 0 1 auto;
	font-size: var(--t-lg);
	text-align: center;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.app-header-user {
	display: inline-flex;
	align-items: center;
	gap: var(--s1);
	min-width: 0;
	max-width: 20rem;
	min-height: var(--tap);
	padding: 0 var(--s3);
	border-radius: var(--r-md);
	background: var(--surface-2);
	font-size: var(--t-md);
	font-weight: 800;
}
.app-header-user-name {
	min-width: 0;
	unicode-bidi: plaintext;
	overflow: hidden;
	white-space: nowrap;
	text-overflow: ellipsis;
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
	.app-header-button span,
	.app-header-title {
		display: none;
	}
}
</style>
