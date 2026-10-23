<script setup>
const props = defineProps({
	marked: { type: Array, default: () => [] },
	selected: { type: String, default: "" },
	labels: { type: Object, required: true },
})
defineEmits(["pick"])

const ZONES = [
	{ area: "Front", fill: "M40 20 H160 V100 H40 Z", hit: "M0 0 H200 V100 H0 Z", label: [100, 62] },
	{ area: "Rear", fill: "M40 280 H160 V350 H40 Z", hit: "M0 280 H200 V370 H0 Z", label: [100, 318] },
	{ area: "Left Side", fill: "M40 100 H72 V280 H40 Z", hit: "M0 100 H72 V280 H0 Z", label: [56, 190] },
	{ area: "Right Side", fill: "M128 100 H160 V280 H128 Z", hit: "M128 100 H200 V280 H128 Z", label: [144, 190] },
	{ area: "Roof", fill: "M72 100 H128 V280 H72 Z", hit: "M72 100 H128 V280 H72 Z", label: [100, 190] },
]

function state(area) {
	if (props.selected === area) return "selected"
	return props.marked.indexOf(area) !== -1 ? "marked" : "clear"
}
</script>

<template>
	<svg class="car-diagram" viewBox="0 0 200 370" role="group" :aria-label="labels.title">
		<defs>
			<clipPath id="car-diagram-body">
				<path d="M100 18 C134 18 158 26 160 60 V318 C160 344 140 352 100 352 C60 352 40 344 40 318 V60 C42 26 66 18 100 18 Z" />
			</clipPath>
		</defs>
		<rect class="car-wheel" x="28" y="74" width="14" height="40" rx="6" />
		<rect class="car-wheel" x="158" y="74" width="14" height="40" rx="6" />
		<rect class="car-wheel" x="28" y="262" width="14" height="40" rx="6" />
		<rect class="car-wheel" x="158" y="262" width="14" height="40" rx="6" />
		<g clip-path="url(#car-diagram-body)">
			<path v-for="zone in ZONES" :key="'f' + zone.area" class="car-zone" :class="'car-zone-' + state(zone.area)" :d="zone.fill" />
		</g>
		<path class="car-outline" d="M100 18 C134 18 158 26 160 60 V318 C160 344 140 352 100 352 C60 352 40 344 40 318 V60 C42 26 66 18 100 18 Z" />
		<path class="car-glass" d="M60 104 Q100 90 140 104 L132 136 Q100 128 68 136 Z" />
		<path class="car-glass" d="M66 262 Q100 270 134 262 L140 282 Q100 294 60 282 Z" />
		<path class="car-line" d="M40 100 H160 M40 280 H160 M72 136 V262 M128 136 V262" />
		<g v-for="zone in ZONES" :key="'h' + zone.area" class="car-hit" role="button" :aria-label="labels[zone.area]" :aria-pressed="state(zone.area) !== 'clear' ? 'true' : 'false'" tabindex="0" @click="$emit('pick', zone.area)" @keydown.enter.prevent="$emit('pick', zone.area)">
			<path :d="zone.hit" />
			<circle v-if="state(zone.area) !== 'clear'" class="car-pin" :class="'car-pin-' + state(zone.area)" :cx="zone.label[0]" :cy="zone.label[1]" r="13" />
		</g>
	</svg>
</template>

<style>
.car-diagram {
	display: block;
	width: 100%;
	max-width: 16rem;
	height: auto;
	margin-inline: auto;
	direction: ltr;
}
.car-wheel {
	fill: var(--ink-2);
}
.car-zone {
	transition: fill 120ms var(--ease);
}
.car-zone-clear {
	fill: var(--surface);
}
.car-zone-marked {
	fill: var(--problem-bg);
}
.car-zone-selected {
	fill: var(--wait-bg);
}
.car-outline {
	fill: none;
	stroke: var(--ink);
	stroke-width: 3;
}
.car-glass {
	fill: var(--surface-2);
	stroke: var(--ink-2);
	stroke-width: 2;
}
.car-line {
	fill: none;
	stroke: var(--line);
	stroke-width: 2;
	stroke-dasharray: 4 4;
}
.car-hit {
	cursor: pointer;
}
.car-hit path {
	fill: transparent;
}
.car-hit:focus {
	outline: none;
}
.car-hit:focus-visible path {
	stroke: var(--focus);
	stroke-width: 3;
}
.car-pin-marked {
	fill: var(--problem);
}
.car-pin-selected {
	fill: var(--wait);
}
</style>
