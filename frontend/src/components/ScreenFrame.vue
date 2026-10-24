<script setup>
import ErrorCard from "./ErrorCard.vue"

defineProps({ title: { type: String, required: true }, error: { type: [String, Object], default: "" } })
defineEmits(["update:error"])
</script>

<template>
	<section class="screen" :class="{ 'screen-split': $slots.aside }">
		<header class="screen-head">
			<h1>{{ title }}</h1>
			<slot name="meta" />
		</header>
		<div class="screen-body"><slot /></div>
		<aside v-if="$slots.aside" class="screen-aside"><slot name="aside" /></aside>
		<footer class="screen-actions">
			<slot name="back" />
			<span class="screen-gap"></span>
			<slot name="primary" />
		</footer>
		<ErrorCard :error="error" @dismiss="$emit('update:error', '')" />
	</section>
</template>

<style>
.screen {
	display: flex;
	flex-direction: column;
	min-height: 100%;
	gap: var(--s4);
}
.screen-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	flex-wrap: wrap;
	gap: var(--s3);
}
.screen-body {
	flex: 1;
	min-width: 0;
	min-height: 0;
}
.screen-split {
	display: grid;
	grid-template-columns: minmax(17rem, 24rem) minmax(0, 1fr);
	grid-template-rows: auto 1fr auto;
	grid-template-areas:
		"aside head"
		"aside body"
		"aside actions";
	gap: var(--s3) var(--s5);
	align-items: start;
}
html.no-flex-gap .screen.screen-split > :not(:last-child) {
	margin-bottom: 0;
}
.screen-split > .screen-head {
	grid-area: head;
}
.screen-split > .screen-body {
	grid-area: body;
}
.screen-split > .screen-aside {
	grid-area: aside;
}
.screen-split > .screen-actions {
	grid-area: actions;
	align-self: end;
}
.screen-actions {
	position: sticky;
	bottom: 0;
	display: flex;
	align-items: center;
	gap: var(--s3);
	padding: var(--s3) 0;
	background: linear-gradient(to top, var(--bg) 75%, transparent);
}
.screen-error {
	color: var(--problem);
	font-weight: 700;
}
.screen-gap {
	flex: 1;
	min-width: 0;
}
.screen-actions > .big-button-primary,
.screen-actions > .big-button-done {
	min-width: 14rem;
}
@media (max-width: 760px) {
	.screen-split {
		grid-template-columns: minmax(0, 1fr);
		grid-template-rows: auto auto auto auto;
		grid-template-areas:
			"head"
			"body"
			"aside"
			"actions";
	}
	.screen-actions {
		flex-wrap: wrap;
	}
	.screen-actions > .big-button-primary,
	.screen-actions > .big-button-done {
		flex: 1;
		min-width: 0;
	}
}
@media (max-width: 480px) {
	.screen-actions > .big-button-quiet {
		min-width: var(--button);
		padding: 0;
	}
	.screen-actions > .big-button-quiet .big-button-label {
		display: none;
	}
}
</style>
