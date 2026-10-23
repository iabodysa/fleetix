<script setup>
defineProps({ label: { type: String, required: true } })
</script>

<template>
	<div class="empty-state">
		<svg class="empty-state-art" viewBox="0 0 200 110" aria-hidden="true">
			<path class="empty-ground" d="M10 92 H190" />
			<path class="empty-body" d="M30 78 V62 Q30 56 36 55 L58 52 L76 34 Q80 30 88 30 H128 Q136 30 140 35 L156 52 L168 55 Q174 57 174 64 V78 Z" />
			<path class="empty-glass" d="M82 50 L90 38 H108 V50 Z M114 50 V38 H130 L142 50 Z" />
			<circle class="empty-wheel" cx="62" cy="80" r="12" />
			<circle class="empty-wheel" cx="146" cy="80" r="12" />
			<circle class="empty-badge" cx="166" cy="24" r="14" />
			<path class="empty-tick" d="M159 24 L164 29 L173 19" />
		</svg>
		<p class="empty-state-label">{{ label }}</p>
		<slot />
	</div>
</template>

<style>
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: var(--s3);
	padding: var(--s6) var(--s4);
	text-align: center;
}
.empty-state-art {
	width: min(16rem, 70%);
	height: auto;
}
.empty-ground {
	stroke: var(--line);
	stroke-width: 3;
	stroke-linecap: round;
}
.empty-body {
	fill: var(--surface);
	stroke: var(--ink-2);
	stroke-width: 3;
	stroke-linejoin: round;
}
.empty-glass {
	fill: var(--surface-2);
	stroke: var(--ink-2);
	stroke-width: 2;
}
.empty-wheel {
	fill: var(--ink-2);
	stroke: var(--surface);
	stroke-width: 4;
}
.empty-badge {
	fill: var(--done);
}
.empty-tick {
	fill: none;
	stroke: var(--on-done);
	stroke-width: 3.5;
	stroke-linecap: round;
	stroke-linejoin: round;
}
.empty-state-label {
	font-size: var(--t-lg);
	font-weight: 700;
	color: var(--ink-2);
}
</style>
