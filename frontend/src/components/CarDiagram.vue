<script setup>
const props = defineProps({
	views: { type: Array, default: () => [] },
	marks: { type: Array, default: () => [] },
	labels: { type: Object, required: true },
})
const emit = defineEmits(["mark", "unmark"])
const ORDER = [
	["right", "front"],
	["left", "rear"],
]

function view(name) {
	return props.views.find((row) => row.view === name)
}
function rows() {
	return ORDER.map((names) => names.map(view).filter(Boolean)).filter((row) => row.length)
}
function place(row, event) {
	const box = event.currentTarget.getBoundingClientRect()
	const x = (event.clientX - box.left) / box.width
	const y = (event.clientY - box.top) / box.height
	if (x < 0 || x > 1 || y < 0 || y > 1) return
	emit("mark", { view: row.view, x: Math.round(x * 10000) / 10000, y: Math.round(y * 10000) / 10000 })
}
function marksOn(name) {
	return props.marks.map((mark, index) => ({ mark, no: index + 1 })).filter((row) => row.mark.view === name)
}
</script>

<template>
	<div class="car-diagram" role="group" :aria-label="labels.title">
		<div v-for="(row, index) in rows()" :key="index" class="car-row">
			<figure v-for="item in row" :key="item.view" class="car-view" :style="{ flex: item.aspect + ' 1 0px' }">
				<div class="car-canvas" :style="{ paddingBottom: 100 / item.aspect + '%' }" @click="place(item, $event)">
					<div class="car-svg" v-html="item.svg"></div>
					<button
						v-for="entry in marksOn(item.view)"
						:key="entry.no"
						class="car-x"
						type="button"
						:aria-label="labels.remove"
						:style="{ left: entry.mark.x * 100 + '%', top: entry.mark.y * 100 + '%' }"
						@click.stop="emit('unmark', entry.mark)"
					>
						<svg class="car-x-glyph" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5L19 19M19 5L5 19" /></svg>
						<span class="car-x-no">{{ entry.no }}</span>
					</button>
				</div>
				<figcaption class="car-caption">{{ labels[item.view] }}</figcaption>
			</figure>
		</div>
	</div>
</template>

<style>
.car-diagram {
	direction: ltr;
	width: 100%;
	max-width: 32rem;
	margin: 0 auto;
}
.car-row {
	display: flex;
	justify-content: center;
}
.car-row + .car-row {
	margin-top: var(--s3);
}
.car-view {
	flex: 1 1 0;
	min-width: 0;
	margin: 0;
	padding: var(--s2);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: #ffffff;
}
.car-view + .car-view {
	margin-left: var(--s3);
}
.car-canvas {
	position: relative;
	height: 0;
	cursor: crosshair;
	touch-action: manipulation;
}
.car-svg {
	position: absolute;
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
	pointer-events: none;
}
.car-svg svg {
	display: block;
	width: 100%;
	height: 100%;
}
.car-x {
	position: absolute;
	width: 2.75rem;
	height: 2.75rem;
	margin: -1.375rem 0 0 -1.375rem;
	padding: 0;
	border: 0;
	background: none;
	color: var(--problem);
}
.car-x-glyph {
	display: block;
	width: 100%;
	height: 100%;
	padding: 0.5rem;
	fill: none;
	stroke: currentColor;
	stroke-width: 4;
	stroke-linecap: round;
}
.car-x-no {
	position: absolute;
	top: -0.25rem;
	right: -0.25rem;
	min-width: 1.25rem;
	height: 1.25rem;
	border-radius: 0.625rem;
	background: var(--problem);
	color: #ffffff;
	font-size: 0.75rem;
	font-weight: 800;
	line-height: 1.25rem;
	text-align: center;
}
.car-caption {
	margin-top: var(--s1);
	color: var(--ink-2);
	font-weight: 700;
	text-align: center;
}
</style>
