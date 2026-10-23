<script setup>
import { runUndo, undoState } from "../composables/useUndo.js"
import AppIcon from "./AppIcon.vue"
</script>

<template>
	<Transition name="undo">
		<div v-if="undoState.message" class="undo-toast" role="status">
			<span class="undo-text">{{ undoState.message }}</span>
			<button class="undo-button" type="button" @click="runUndo">
				<AppIcon name="undo" />
				<span>{{ __("Undo") }}</span>
			</button>
		</div>
	</Transition>
</template>

<style>
.undo-toast {
	position: fixed;
	left: var(--s4);
	right: var(--s4);
	bottom: calc(var(--button) + var(--s6));
	z-index: 30;
	display: flex;
	align-items: center;
	gap: var(--s3);
	max-width: 36rem;
	margin-left: auto;
	margin-right: auto;
	padding: var(--s2) var(--s2) var(--s2) var(--s4);
	border-radius: var(--r-md);
	background: var(--ink);
	color: var(--bg);
	box-shadow: var(--shadow);
}
.undo-text {
	flex: 1;
	min-width: 0;
	font-weight: 700;
}
.undo-button {
	display: inline-flex;
	align-items: center;
	gap: var(--s2);
	min-height: var(--tap);
	padding: 0 var(--s4);
	border: 0;
	border-radius: var(--r-sm);
	background: var(--gold);
	color: var(--on-gold);
	font-weight: 800;
}
.undo-enter-active,
.undo-leave-active {
	transition: transform var(--slide) var(--ease), opacity var(--slide) var(--ease);
}
.undo-enter-from,
.undo-leave-to {
	transform: translateY(1rem);
	opacity: 0;
}
html[dir="rtl"] .undo-toast {
	padding: var(--s2) var(--s4) var(--s2) var(--s2);
}
</style>
