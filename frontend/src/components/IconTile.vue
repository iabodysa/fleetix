<script setup>
import AppIcon from "./AppIcon.vue"

defineProps({
	icon: { type: String, default: "" },
	label: { type: String, required: true },
	note: { type: String, default: "" },
	tone: { type: String, default: "" },
	pressed: Boolean,
})
defineEmits(["press"])
</script>

<template>
	<button class="icon-tile" :class="[tone ? 'icon-tile-' + tone : '', { pressed }]" type="button" :aria-pressed="pressed ? 'true' : 'false'" @click="$emit('press')">
		<span class="icon-tile-mark"><AppIcon :name="pressed ? 'done' : icon" size="lg" /></span>
		<span class="icon-tile-label">{{ label }}</span>
		<span v-if="note" class="icon-tile-note">{{ note }}</span>
		<slot />
	</button>
</template>

<style>
.icon-tile {
	position: relative;
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	gap: var(--s2);
	min-height: 7.5rem;
	padding: var(--s4);
	border: 2px solid var(--line);
	border-radius: var(--r-lg);
	background: var(--surface);
	color: var(--ink);
	text-align: start;
	box-shadow: var(--shadow);
	transition: border-color 120ms var(--ease), background-color 120ms var(--ease);
}
.icon-tile-mark {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: 3rem;
	height: 3rem;
	border-radius: var(--r-md);
	background: var(--surface-2);
}
.icon-tile-label {
	font-size: var(--t-lg);
	font-weight: 800;
	line-height: 1.2;
}
.icon-tile-note {
	font-size: var(--t-sm);
	color: var(--ink-2);
}
.icon-tile-problem {
	border-color: var(--problem);
}
.icon-tile-problem .icon-tile-mark {
	background: var(--problem-bg);
	color: var(--problem-ink);
}
.icon-tile-wait .icon-tile-mark {
	background: var(--wait-bg);
	color: var(--wait-ink);
}
.icon-tile-done .icon-tile-mark {
	background: var(--done-bg);
	color: var(--done-ink);
}
.icon-tile.pressed {
	border-color: var(--primary);
	background: var(--surface-2);
	box-shadow: inset 0 0 0 2px var(--primary);
}
.icon-tile.pressed .icon-tile-mark {
	background: var(--primary);
	color: var(--on-primary);
}
.tile-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(11rem, 1fr));
	gap: var(--s3);
}
</style>
