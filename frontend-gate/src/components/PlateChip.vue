<script setup>
import { computed } from "vue"
import { parsePlate } from "../plate.js"

const props = defineProps({ plate: { type: String, default: "" }, size: { type: String, default: "md" } })
const parts = computed(() => parsePlate(props.plate))
</script>

<template>
	<div class="plate" :class="'plate-' + size" dir="ltr">
		<div class="block">
			<div class="row ar"><span v-for="(d, i) in parts.digits" :key="'da' + i">{{ d.arabic }}</span></div>
			<div class="row"><span v-for="(d, i) in parts.digits" :key="'dl' + i">{{ d.latin }}</span></div>
		</div>
		<div class="block">
			<div class="row ar"><span v-for="(l, i) in parts.letters" :key="'la' + i">{{ l.arabic }}</span></div>
			<div class="row"><span v-for="(l, i) in parts.letters" :key="'ll' + i">{{ l.latin }}</span></div>
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
	display: flex;
	justify-content: center;
	gap: 6px;
	font-size: 20px;
	line-height: 1.2;
	min-height: 24px;
}
.ar {
	direction: rtl;
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
	font-size: 28px;
	min-height: 34px;
}
.plate-lg .block {
	min-width: 96px;
}
.plate-sm {
	min-height: 40px;
	border-width: 2px;
}
.plate-sm .row {
	font-size: 13px;
	min-height: 16px;
	gap: 3px;
}
.plate-sm .block {
	min-width: 44px;
	padding: 1px 6px;
}
.plate-sm .strip {
	font-size: 8px;
}
</style>
