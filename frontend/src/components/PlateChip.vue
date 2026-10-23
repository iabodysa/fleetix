<script setup>
import { computed } from "vue"
import { parsePlate } from "./plate.js"

const props = defineProps({ plate: { type: String, default: "" }, size: { type: String, default: "md" } })
const parts = computed(() => parsePlate(props.plate))
</script>

<template>
	<div class="plate" :class="'plate-' + size" dir="ltr">
		<div class="plate-block">
			<div class="plate-row plate-ar">
				<span v-for="(d, i) in parts.digits" :key="'da' + i">{{ d.arabic }}</span>
			</div>
			<div class="plate-row">
				<span v-for="(d, i) in parts.digits" :key="'dl' + i">{{ d.latin }}</span>
			</div>
		</div>
		<div class="plate-block">
			<div class="plate-row plate-ar">
				<span v-for="(l, i) in parts.letters" :key="'la' + i">{{ l.arabic }}</span>
			</div>
			<div class="plate-row">
				<span v-for="(l, i) in parts.letters" :key="'ll' + i">{{ l.latin }}</span>
			</div>
		</div>
		<div class="plate-strip">KSA</div>
	</div>
</template>

<style>
.plate {
	display: inline-flex;
	align-items: stretch;
	border: 2px solid var(--plate-ink);
	border-radius: var(--r-sm);
	background: var(--plate);
	color: var(--plate-ink);
	font-weight: 800;
	line-height: 1.05;
	overflow: hidden;
}
.plate-block {
	display: flex;
	flex-direction: column;
	justify-content: center;
	padding: 0.15em 0.45em;
	border-inline-end: 2px solid var(--plate-ink);
}
.plate-row {
	display: flex;
	justify-content: center;
	gap: 0.2em;
}
.plate-ar {
	border-bottom: 1px solid var(--plate-ink);
}
.plate-strip {
	display: flex;
	align-items: center;
	padding: 0 0.35em;
	background: var(--brand);
	color: var(--on-brand);
	font-size: 0.6em;
	writing-mode: vertical-rl;
}
.plate-sm {
	font-size: var(--t-sm);
}
.plate-md {
	font-size: var(--t-md);
}
.plate-lg {
	font-size: var(--t-xl);
}
.plate-xl {
	font-size: clamp(var(--t-xl), 9vw, var(--t-display));
}
</style>
