<script setup>
import { computed } from "vue"
import { offerUndo } from "../composables/useUndo.js"
import { __ } from "../i18n/index.js"
import NumberPad from "./NumberPad.vue"

const props = defineProps({ modelValue: { type: String, default: "" }, length: { type: Number, default: 4 } })
const emit = defineEmits(["update:modelValue"])
const cells = computed(() => Array.from({ length: props.length }, (_, index) => props.modelValue[index] || ""))

function put(value) {
	emit("update:modelValue", value)
}
function clear() {
	const before = props.modelValue
	if (!before) return
	put("")
	offerUndo(__("Plate number cleared"), () => put(before))
}
</script>

<template>
	<div class="plate-keypad">
		<div class="plate-keypad-readout ltr" :aria-label="__('Plate number')">
			<span v-for="(digit, index) in cells" :key="index" class="plate-keypad-cell" :class="{ empty: !digit }">{{ digit || "·" }}</span>
		</div>
		<NumberPad @key="put((modelValue + $event).slice(0, length))" @clear="clear" @erase="put(modelValue.slice(0, -1))" />
	</div>
</template>

<style>
.plate-keypad {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
}
.plate-keypad-readout {
	display: flex;
	justify-content: center;
	gap: var(--s2);
	padding: var(--s3);
	border: 3px solid var(--plate-ink);
	border-radius: var(--r-md);
	background: var(--plate);
	color: var(--plate-ink);
}
.plate-keypad-cell {
	width: 2.75rem;
	font-size: var(--t-xxl);
	font-weight: 800;
	line-height: 1;
	text-align: center;
	font-variant-numeric: tabular-nums;
}
.plate-keypad-cell.empty {
	color: var(--plate-muted);
}
</style>
