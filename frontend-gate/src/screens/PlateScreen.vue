<script setup>
import { onMounted, ref } from "vue"
import { errorText } from "../api.js"
import { __ } from "../i18n.js"
import { hasCamera } from "../native.js"
import { lookUp } from "../store.js"
import BigButton from "../components/BigButton.vue"
import BarcodeInput from "../components/BarcodeInput.vue"
import PlateChip from "../components/PlateChip.vue"
import PlateKeypad from "../components/PlateKeypad.vue"

const plate = ref("")
const busy = ref(false)
const error = ref("")
const camera = ref(false)

async function find(code) {
	if (busy.value) return
	busy.value = true
	error.value = ""
	try {
		if (!(await lookUp(code))) error.value = __("No car with this plate")
	} catch (e) {
		error.value = errorText(e)
	} finally {
		busy.value = false
	}
}
onMounted(async () => {
	camera.value = await hasCamera()
})
</script>

<template>
	<div class="page">
		<div class="screen">
			<h1 class="screen-title">{{ __("Car plate") }}</h1>
			<div class="preview" :class="{ blank: !plate }">
				<PlateChip :plate="plate" size="lg" />
			</div>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<BarcodeInput :camera="camera" @scan="find" />
			<PlateKeypad v-model="plate" mode="plate" />
		</div>
		<div class="dock">
			<BigButton icon="next" :label="__('Find car')" :disabled="!/[0-9]/.test(plate)" :busy="busy" @press="find(plate)" />
		</div>
	</div>
</template>

<style scoped>
.preview {
	display: flex;
	justify-content: center;
	transition: opacity var(--move) var(--ease);
}
.blank {
	opacity: 0.5;
}
</style>
