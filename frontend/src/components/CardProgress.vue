<script setup>
import AppIcon from "./AppIcon.vue"

defineProps({ items: { type: Array, required: true } })
const emit = defineEmits(["show"])
</script>

<template>
	<nav v-if="items.length > 1" class="card-progress">
		<button v-for="row in items" :key="row.key" type="button" class="card-progress-chip" :class="row.done ? 'tone-done' : 'tone-wait'" @click="emit('show', row.key)">
			<AppIcon :name="row.done ? 'done' : row.icon || 'problem'" />
			<span>{{ row.label }}</span>
		</button>
	</nav>
</template>

<style>
.card-progress {
	position: -webkit-sticky;
	position: sticky;
	top: 0;
	z-index: 5;
	display: flex;
	gap: var(--s2);
	margin: 0 calc(-1 * var(--s2));
	padding: var(--s2);
	overflow-x: auto;
	background: var(--bg);
	-webkit-overflow-scrolling: touch;
}
.card-progress-chip {
	display: inline-flex;
	flex: none;
	align-items: center;
	gap: var(--s1);
	min-height: 2.75rem;
	padding: 0 var(--s3);
	border: 2px solid var(--wait);
	border-radius: 999px;
	background: var(--wait-bg);
	color: var(--wait-ink);
	font-weight: 800;
	white-space: nowrap;
}
.card-progress-chip.tone-done {
	border-color: var(--done);
	background: var(--done-bg);
	color: var(--done-ink);
}
@keyframes card-pulse {
	0%,
	100% {
		box-shadow: 0 0 0 0 rgba(178, 106, 0, 0);
	}
	30%,
	70% {
		box-shadow: 0 0 0 6px rgba(178, 106, 0, 0.45);
	}
}
.card-pulse {
	border-color: var(--wait) !important;
	animation: card-pulse 0.8s ease-in-out 2;
}
</style>
