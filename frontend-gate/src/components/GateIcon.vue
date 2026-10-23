<script setup>
const PATHS = {
	next: "M5 12h14M13 6l6 6-6 6",
	check: "M5 13l4 4 10-10",
	camera: "M4 8h3l2-3h6l2 3h3v11H4zM12 17a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
	scan: "M4 8V4h4M16 4h4v4M20 16v4h-4M8 20H4v-4M4 12h16",
	wrench: "M14 6a4 4 0 0 0 5 5l-8 8a2 2 0 0 1-3-3l8-8a4 4 0 0 0-2-2z",
	keys: "M4 8h14l-4-4M20 16H6l4 4",
	plus: "M12 5v14M5 12h14",
	retry: "M4 12a8 8 0 1 0 2.5-5.8M4 4v4h4",
	car: "M3 14l2-6h14l2 6v5h-3v-2H6v2H3zM6 14h2M16 14h2",
	back: "M15 6l-6 6 6 6",
	erase: "M20 6H9l-6 6 6 6h11zM12 9l6 6M18 9l-6 6",
	globe: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18",
	nocamera: "M3 3l18 18M9 5h6l2 3h3v10M4 8h3M4 8v11h13",
}
defineProps({ name: { type: String, required: true }, flip: { type: Boolean, default: false } })
</script>

<template>
	<svg class="icon" :class="{ flip }" viewBox="0 0 24 24" aria-hidden="true">
		<path :d="PATHS[name]" />
	</svg>
</template>

<style scoped>
.icon {
	width: 26px;
	height: 26px;
	fill: none;
	stroke: currentColor;
	stroke-width: 2;
	stroke-linecap: round;
	stroke-linejoin: round;
	flex: none;
}
[dir="rtl"] .flip {
	transform: scaleX(-1);
}
</style>
