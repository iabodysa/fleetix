<template>
	<svg class="check" viewBox="0 0 96 96" aria-hidden="true">
		<circle cx="48" cy="48" r="44" />
		<path d="M28 50l14 14 26-30" />
	</svg>
</template>

<style scoped>
.check {
	width: 112px;
	height: 112px;
	margin: 0 auto;
	display: block;
}
circle {
	fill: var(--ok);
	transform-origin: center;
	animation: pop calc(var(--move) * 1.6) var(--ease) both;
}
path {
	fill: none;
	stroke: var(--on-ok);
	stroke-width: 8;
	stroke-linecap: round;
	stroke-linejoin: round;
	stroke-dasharray: 70;
	stroke-dashoffset: 70;
	animation: draw calc(var(--move) * 2) var(--ease) calc(var(--move) * 1.2) forwards;
}
@keyframes pop {
	from {
		transform: scale(0.6);
		opacity: 0;
	}
}
@keyframes draw {
	to {
		stroke-dashoffset: 0;
	}
}
@media (prefers-reduced-motion: reduce) {
	circle {
		animation: none;
	}
	path {
		animation: none;
		stroke-dashoffset: 0;
	}
}
</style>
