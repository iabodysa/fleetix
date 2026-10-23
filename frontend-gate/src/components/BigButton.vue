<script setup>
import GateIcon from "./GateIcon.vue"

defineProps({
	icon: { type: String, default: "next" },
	label: { type: String, required: true },
	tone: { type: String, default: "primary" },
	disabled: { type: Boolean, default: false },
	busy: { type: Boolean, default: false },
})
defineEmits(["press"])
</script>

<template>
	<button
		class="big"
		:class="'big-' + tone"
		type="button"
		:disabled="disabled || busy"
		:aria-busy="busy"
		@click="$emit('press')"
	>
		<span v-if="busy" class="spin" aria-hidden="true"></span>
		<GateIcon v-else :name="icon" :flip="icon === 'next' || icon === 'back'" />
		<span>{{ label }}</span>
	</button>
</template>

<style scoped>
.big {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 12px;
	width: 100%;
	min-height: var(--tap);
	padding: 12px 20px;
	border: 0;
	border-radius: var(--radius);
	font-size: 20px;
	font-weight: 700;
	transition:
		transform 120ms var(--ease),
		opacity var(--move) var(--ease);
}
.big:active:not(:disabled) {
	transform: scale(0.98);
}
.big:disabled {
	opacity: 0.45;
	cursor: not-allowed;
}
.big-primary {
	background: var(--accent);
	color: var(--on-accent);
}
.big-ok {
	background: var(--ok);
	color: var(--on-ok);
}
.big-soft {
	background: var(--surface);
	color: var(--ink);
	border: 1px solid var(--line);
}
.spin {
	width: 24px;
	height: 24px;
	border: 3px solid currentColor;
	border-top-color: transparent;
	border-radius: 50%;
	animation: turn 0.8s linear infinite;
}
@keyframes turn {
	to {
		transform: rotate(360deg);
	}
}
@media (prefers-reduced-motion: reduce) {
	.spin {
		animation-duration: 2.4s;
	}
}
</style>
