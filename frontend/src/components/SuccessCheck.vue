<script setup>
import { onMounted } from "vue"
import { success } from "../composables/useFeedback.js"

defineProps({ label: { type: String, required: true } })
onMounted(success)
</script>

<template>
	<div class="success-check" role="status">
		<svg class="success-check-mark" viewBox="0 0 96 96" aria-hidden="true">
			<circle cx="48" cy="48" r="44" />
			<path d="M28 50 L42 64 L70 34" />
		</svg>
		<p class="success-check-label">{{ label }}</p>
	</div>
</template>

<style>
.success-check {
	display: flex;
	align-items: center;
	gap: var(--s4);
}
.success-check-mark {
	flex: none;
	width: 5.5rem;
	height: 5.5rem;
}
.success-check-mark circle {
	fill: var(--done);
}
.success-check-mark path {
	fill: none;
	stroke: var(--on-done);
	stroke-width: 9;
	stroke-linecap: round;
	stroke-linejoin: round;
	stroke-dasharray: 70;
	stroke-dashoffset: 70;
	animation: success-check-draw 200ms 80ms var(--ease) forwards;
}
.success-check-label {
	font-size: var(--t-xl);
	font-weight: 800;
	line-height: 1.2;
}
@keyframes success-check-draw {
	to {
		stroke-dashoffset: 0;
	}
}
@media (prefers-reduced-motion: reduce) {
	.success-check-mark path {
		animation: none;
		stroke-dashoffset: 0;
	}
}
</style>
