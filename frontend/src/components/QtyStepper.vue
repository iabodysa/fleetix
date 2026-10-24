<script setup>
import { computed } from "vue"
import { __ } from "../i18n/index.js"
import AppIcon from "./AppIcon.vue"

const props = defineProps({
	modelValue: { type: Number, required: true },
	unit: { type: String, required: true },
	litres: Boolean,
	packs: { type: Array, default: () => [] },
	max: { type: Number, default: 0 },
	min: { type: Number, default: 0 },
})
const emit = defineEmits(["update:modelValue"])
const steps = computed(() => (props.litres ? [0.5, 1] : [1]))
const pack = computed(() => {
	const size = props.litres && props.packs.find((row) => row.factor <= props.modelValue)
	if (!size) return ""
	const count = Math.floor(props.modelValue / size.factor)
	const rest = Math.round((props.modelValue - count * size.factor) * 100) / 100
	const head = "= " + count + " " + size.uom + " " + size.factor + " " + props.unit
	return rest ? head + " + " + rest + " " + props.unit : head
})

function fits(step) {
	return !props.max || props.modelValue + step <= props.max
}
function add(step) {
	if (fits(step)) emit("update:modelValue", Math.round((props.modelValue + step) * 100) / 100)
}
function less() {
	emit("update:modelValue", Math.max(props.min, Math.round((props.modelValue - steps.value[0]) * 100) / 100))
}
</script>

<template>
	<div class="qty" :class="{ 'qty-litres': litres }">
		<button class="qty-button" type="button" :aria-label="__('Less')" :disabled="modelValue <= min" @click="less">
			<AppIcon name="minus" /><span class="ltr">{{ steps[0] }}</span> {{ unit }}
		</button>
		<span class="qty-value">
			<AppIcon v-if="litres" name="litre" size="lg" />
			<b class="ltr">{{ modelValue }}</b>
			<span>{{ unit }}</span>
		</span>
		<button v-for="step in steps" :key="step" class="qty-button" type="button" :aria-label="__('More')" :disabled="!fits(step)" @click="add(step)">
			<AppIcon name="plus" /><span class="ltr">{{ step }}</span> {{ unit }}
		</button>
		<span v-if="pack" class="qty-pack muted">{{ pack }}</span>
	</div>
</template>

<style>
.qty {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: var(--s2);
}
.qty-button {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	gap: var(--s1);
	min-width: 6rem;
	min-height: var(--tap);
	padding: 0 var(--s3);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface-2);
	font-weight: 800;
}
.qty-button:disabled {
	opacity: 0.4;
}
.qty-value {
	display: inline-flex;
	align-items: center;
	gap: var(--s2);
	min-width: 7rem;
	justify-content: center;
	font-size: var(--t-xl);
	font-weight: 800;
}
.qty-pack {
	flex-basis: 100%;
	font-weight: 700;
}
</style>
