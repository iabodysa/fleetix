<script setup>
defineProps({ steps: { type: Array, required: true }, current: { type: Number, required: true } })
</script>

<template>
	<ol class="steps" :aria-label="steps[current]">
		<li v-for="(label, index) in steps" :key="label" :class="{ done: index < current, now: index === current }">
			<span class="bar"></span>
			<span class="label">{{ label }}</span>
		</li>
	</ol>
</template>

<style scoped>
.steps {
	display: grid;
	grid-auto-flow: column;
	grid-auto-columns: 1fr;
	gap: 6px;
	list-style: none;
	margin: 0;
	padding: 0 16px;
	max-width: 720px;
	margin-left: auto;
	margin-right: auto;
	width: 100%;
}
li {
	display: flex;
	flex-direction: column;
	gap: 4px;
	min-width: 0;
}
.bar {
	height: 6px;
	border-radius: 3px;
	background: var(--line);
	transition: background var(--move) var(--ease);
}
.done .bar {
	background: var(--ok);
}
.now .bar {
	background: var(--accent);
}
.label {
	font-size: 13px;
	color: var(--ink-2);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
.now .label {
	color: var(--ink);
	font-weight: 700;
}
</style>
