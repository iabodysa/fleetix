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
		<div class="plate-block plate-letters">
			<div class="plate-row plate-ar">
				<span v-for="(l, i) in parts.letters" :key="'la' + i">{{ l.arabic }}</span>
			</div>
			<div class="plate-row">
				<span v-for="(l, i) in parts.letters" :key="'ll' + i">{{ l.latin }}</span>
			</div>
		</div>
		<div class="plate-strip">
			<span class="plate-strip-ar">السعودية</span>
			<span>KSA</span>
		</div>
	</div>
</template>

<style>
.plate {
	display: inline-flex;
	flex-shrink: 0;
	width: 6.6em;
	height: 3.3em;
	border: 0.12em solid var(--plate-ink);
	border-radius: 0.3em;
	background: var(--plate);
	color: var(--plate-ink);
	font-weight: 800;
	line-height: 1;
	overflow: hidden;
}
.plate-block {
	display: flex;
	flex-direction: column;
	width: 2.7em;
}
.plate-letters {
	border-left: 0.1em solid var(--plate-ink);
}
.plate-row {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 50%;
	font-size: 0.92em;
	font-variant-numeric: tabular-nums;
}
.plate-row span {
	padding: 0 0.05em;
}
.plate-ar {
	border-bottom: 0.06em solid var(--plate-ink);
	font-size: 0.85em;
}
.plate-letters .plate-ar {
	flex-direction: row-reverse;
}
.plate-strip {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	width: 1.2em;
	border-left: 0.1em solid var(--plate-ink);
	background: var(--brand);
	color: var(--on-brand);
	font-size: 1em;
}
.plate-strip span {
	font-size: 0.36em;
	line-height: 1.3;
}
.plate-strip .plate-strip-ar {
	font-size: 0.3em;
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
	font-size: var(--t-xxl);
	font-size: clamp(var(--t-xl), 9vw, var(--t-display));
}
</style>
