<script setup>
import AppIcon from "./AppIcon.vue"

defineEmits(["key", "clear", "erase"])
const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
</script>

<template>
	<div class="number-pad ltr">
		<button v-for="key in keys" :key="key" class="number-key" type="button" @click="$emit('key', key)">{{ key }}</button>
		<button class="number-key number-key-soft" type="button" :aria-label="__('Clear')" @click="$emit('clear')">
			<AppIcon name="close" size="lg" />
		</button>
		<button class="number-key" type="button" @click="$emit('key', '0')">0</button>
		<button class="number-key number-key-soft" type="button" :aria-label="__('Delete')" @click="$emit('erase')">
			<AppIcon name="erase" size="lg" />
		</button>
	</div>
</template>

<style>
.number-pad {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: var(--s2);
}
.number-key {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: var(--button);
	border: 1px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface);
	color: var(--ink);
	font-size: var(--t-xl);
	font-weight: 800;
	font-variant-numeric: tabular-nums;
	box-shadow: var(--shadow);
}
.number-key:active {
	background: var(--surface-2);
	transform: scale(0.97);
}
.number-key-soft {
	background: var(--surface-2);
	color: var(--ink-2);
}
</style>
