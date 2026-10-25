<script setup>
import { computed } from "vue"
import { arabicPlate, parsePlate } from "../plate.js"

const props = defineProps({ plate: { type: String, default: "" }, size: { type: String, default: "md" } })
const parts = computed(() => parsePlate(props.plate))
const lettersDir = arabicPlate() ? "rtl" : "ltr"
</script>

<template>
	<div class="plate" :class="'plate-' + size" dir="ltr">
		<div class="block">
			<bdi class="row" dir="ltr">{{ parts.digits }}</bdi>
		</div>
		<div class="block">
			<bdi class="row" :dir="lettersDir">{{ parts.letters }}</bdi>
		</div>
		<div class="strip">KSA</div>
	</div>
</template>

<style scoped>
.plate {
	display: inline-grid;
	grid-template-columns: auto auto 22px;
	background: var(--plate);
	color: var(--plate-ink);
	border: 3px solid var(--plate-ink);
	border-radius: 8px;
	overflow: hidden;
	font-weight: 800;
	min-height: 64px;
}
.block {
	display: flex;
	flex-direction: column;
	justify-content: center;
	min-width: 72px;
	padding: 2px 10px;
}
.block + .block {
	border-left: 2px solid var(--plate-ink);
}
.row {
	display: block;
	text-align: center;
	white-space: nowrap;
	letter-spacing: 2px;
	font-size: 26px;
	line-height: 1.2;
	min-height: 32px;
}
.strip {
	writing-mode: vertical-rl;
	background: var(--plate-ink);
	color: var(--plate);
	font-size: 11px;
	display: flex;
	align-items: center;
	justify-content: center;
	letter-spacing: 2px;
}
.plate-lg .row {
	font-size: 36px;
	min-height: 44px;
}
.plate-lg .block {
	min-width: 96px;
}
.plate-sm {
	min-height: 40px;
	border-width: 2px;
}
.plate-sm .row {
	font-size: 17px;
	min-height: 22px;
	letter-spacing: 1px;
}
.plate-sm .block {
	min-width: 44px;
	padding: 1px 6px;
}
.plate-sm .strip {
	font-size: 8px;
}
</style>
