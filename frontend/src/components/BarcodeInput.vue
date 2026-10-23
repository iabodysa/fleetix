<script setup>
import { scanKey, useBarcode } from "../composables/useBarcode.js"
import AppIcon from "./AppIcon.vue"

const emit = defineEmits(["scan"])
useBarcode((code) => emit("scan", scanKey(code)))
</script>

<template>
	<div class="barcode-input" role="status">
		<span class="barcode-input-mark"><AppIcon name="scan" size="lg" /></span>
		<span class="barcode-input-text">{{ __("Scan the vehicle barcode") }}</span>
	</div>
</template>

<style>
.barcode-input {
	display: flex;
	align-items: center;
	gap: var(--s3);
	padding: var(--s3) var(--s4);
	border: 2px dashed var(--line);
	border-radius: var(--r-md);
	background: var(--surface);
	font-weight: 700;
}
.barcode-input-mark {
	display: inline-flex;
	color: var(--done);
	animation: barcode-input-pulse 1.6s ease-in-out infinite;
}
@keyframes barcode-input-pulse {
	50% {
		opacity: 0.45;
	}
}
</style>
