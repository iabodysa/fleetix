<script setup>
import { computed, onMounted, ref } from "vue"
import { __ } from "../i18n.js"
import { hasCamera } from "../native.js"
import { shrink } from "../photos.js"
import { SIDES, go, store } from "../store.js"
import BigButton from "../components/BigButton.vue"
import GateIcon from "../components/GateIcon.vue"
import PhotoSlot from "../components/PhotoSlot.vue"

const LABELS = { front: __("Front"), back: __("Back"), left: __("Left side"), right: __("Right side") }
const camera = ref(true)
const error = ref("")
const ready = computed(() => !camera.value || SIDES.every((side) => store.photos[side]))

async function take(file, side) {
	error.value = ""
	try {
		const photo = await shrink(file)
		if (side === "damage") store.photos.damage.push(photo)
		else {
			if (store.photos[side]) URL.revokeObjectURL(store.photos[side].url)
			store.photos[side] = photo
		}
	} catch (e) {
		error.value = __("The photo could not be read. Take it again.")
	}
}
onMounted(async () => {
	camera.value = await hasCamera()
})
</script>

<template>
	<div class="page">
		<div class="screen">
			<h1 class="screen-title">{{ __("Photos") }}</h1>
			<p v-if="!camera" class="banner banner-warn nocam"><GateIcon name="nocamera" />{{ __("This device has no camera") }}</p>
			<template v-else>
				<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
				<div class="grid">
					<PhotoSlot v-for="side in SIDES" :key="side" :label="LABELS[side]" :photo="store.photos[side]" @pick="take($event, side)" />
				</div>
				<h2 class="sub">{{ __("Damage") }}</h2>
				<div class="grid">
					<PhotoSlot
						v-for="(photo, index) in store.photos.damage"
						:key="photo.url"
						:label="__('Damage') + ' ' + (index + 1)"
						:photo="photo"
						@pick="take($event, 'damage')"
					/>
					<PhotoSlot :label="__('Add damage photo')" @pick="take($event, 'damage')" />
				</div>
			</template>
		</div>
		<div class="dock">
			<BigButton icon="next" :label="camera ? __('Next') : __('Continue without photos')" :disabled="!ready" @press="go('route')" />
		</div>
	</div>
</template>

<style scoped>
.grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
	gap: 10px;
}
.sub {
	font-size: 18px;
}
.nocam {
	display: flex;
	align-items: center;
	gap: 10px;
}
</style>
