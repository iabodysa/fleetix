<script setup>
import { computed } from "vue"

const props = defineProps({ steps: { type: Array, required: true }, current: { type: Number, required: true } })
const label = computed(() => props.steps[props.current] || "")
</script>

<template>
	<div class="step-bar" role="progressbar" :aria-valuemin="1" :aria-valuemax="steps.length" :aria-valuenow="current + 1" :aria-valuetext="label">
		<ol class="step-bar-track">
			<li v-for="(step, index) in steps" :key="step" :class="{ done: index < current, current: index === current }">
				<span class="step-bar-fill"></span>
				<span class="step-bar-name">{{ step }}</span>
			</li>
		</ol>
		<p class="step-bar-now">
			<span class="ltr">{{ current + 1 }}/{{ steps.length }}</span>
			{{ label }}
		</p>
	</div>
</template>

<style>
.step-bar-track {
	display: flex;
	gap: var(--s1);
	margin: 0;
	padding: 0;
	list-style: none;
}
.step-bar-track li {
	flex: 1;
	min-width: 0;
}
.step-bar-fill {
	display: block;
	height: 0.5rem;
	border-radius: var(--r-pill);
	background: var(--line);
	transition: background-color var(--slide) var(--ease);
}
.step-bar-track .done .step-bar-fill {
	background: var(--done);
}
.step-bar-track .current .step-bar-fill {
	background: var(--primary);
}
.step-bar-name {
	display: block;
	margin-top: var(--s1);
	font-size: var(--t-sm);
	color: var(--ink-2);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.step-bar-track .current .step-bar-name {
	color: var(--ink);
	font-weight: 800;
}
.step-bar-now {
	display: none;
	margin-top: var(--s1);
	font-size: var(--t-sm);
	font-weight: 800;
}
@media (max-width: 760px) {
	.step-bar-name {
		display: none;
	}
	.step-bar-now {
		display: block;
	}
}
</style>
