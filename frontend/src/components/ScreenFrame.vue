<script setup>
defineProps({ title: { type: String, required: true }, error: { type: String, default: "" } })
</script>

<template>
	<section class="screen">
		<header class="screen-head">
			<h1>{{ title }}</h1>
			<slot name="meta" />
		</header>
		<div class="screen-body" :class="{ 'screen-split': $slots.aside }">
			<div class="screen-main"><slot /></div>
			<aside v-if="$slots.aside" class="screen-aside"><slot name="aside" /></aside>
		</div>
		<footer class="screen-actions">
			<slot name="back" />
			<p class="screen-error" role="alert">{{ error }}</p>
			<slot name="primary" />
		</footer>
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
	min-height: 0;
}
.screen-split {
	display: grid;
	grid-template-columns: minmax(0, 1fr) minmax(16rem, 22rem);
	gap: var(--s5);
	align-items: start;
}
.screen-main {
	min-width: 0;
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
	flex: 1;
	min-width: 0;
	color: var(--problem);
	font-weight: 700;
}
.screen-actions > .big-button-primary,
.screen-actions > .big-button-done {
	min-width: 14rem;
}
@media (max-width: 760px) {
	.screen-split {
		grid-template-columns: minmax(0, 1fr);
	}
	.screen-actions {
		flex-wrap: wrap;
	}
	.screen-error {
		order: -1;
		flex-basis: 100%;
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
