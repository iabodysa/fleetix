<script setup>
import AppIcon from "./AppIcon.vue"

defineProps({
	icon: { type: String, default: "" },
	label: { type: String, required: true },
	tone: { type: String, default: "primary" },
	busy: Boolean,
	disabled: Boolean,
	block: Boolean,
	type: { type: String, default: "button" },
})
defineEmits(["press"])
</script>

<template>
	<button
		class="big-button"
		:class="['big-button-' + tone, { 'big-button-block': block, 'big-button-busy': busy }]"
		:type="type"
		:disabled="disabled || busy"
		:aria-label="label"
		:aria-busy="busy ? 'true' : 'false'"
		@click="$emit('press')"
	>
		<AppIcon v-if="icon" :name="icon" size="lg" />
		<span class="big-button-label">{{ label }}</span>
	</button>
</template>

<style>
.big-button {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	gap: var(--s3);
	min-height: var(--button);
	min-width: 10rem;
	padding: 0 var(--s5);
	border: 0;
	border-radius: var(--r-md);
	font-size: var(--t-lg);
	font-weight: 800;
	line-height: 1.15;
	transition: transform 120ms var(--ease), background-color 120ms var(--ease);
}
.big-button:active:not(:disabled) {
	transform: scale(0.98);
}
.big-button:disabled {
	opacity: 0.45;
}
.big-button-block {
	width: 100%;
}
.big-button-primary {
	background: var(--primary);
	color: var(--on-primary);
}
.big-button-primary:active:not(:disabled) {
	background: var(--primary-press);
}
.big-button-done {
	background: var(--done);
	color: var(--on-done);
}
.big-button-quiet {
	background: var(--surface);
	color: var(--ink);
	border: 2px solid var(--line);
	min-width: var(--button);
	font-size: var(--t-md);
}
.big-button-busy .app-icon {
	animation: big-button-spin 900ms linear infinite;
}
.big-button-label {
	overflow-wrap: anywhere;
}
@keyframes big-button-spin {
	to {
		transform: rotate(360deg);
	}
}
</style>
