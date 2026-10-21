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

<script setup>
import { computed } from "vue"
import { parsePlate } from "../plate.js"

const props = defineProps({ plate: String, size: { type: String, default: "md" } })
const parts = computed(() => parsePlate(props.plate))
</script>
