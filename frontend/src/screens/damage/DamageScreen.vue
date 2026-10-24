<script setup>
import { onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { offerUndo } from "../../composables/useUndo.js"
import { go, store } from "../../store/index.js"
import BigButton from "../../components/BigButton.vue"
import CarDiagram from "../../components/CarDiagram.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const labels = {
	title: __("Vehicle body"),
	remove: __("Remove mark"),
	right: __("Right Side"),
	left: __("Left Side"),
	front: __("Front"),
	rear: __("Rear"),
}
const views = ref([])
const error = ref("")

function mark(spot) {
	store.damages = store.damages.concat([spot])
}
function unmark(spot) {
	const before = store.damages.slice()
	store.damages = store.damages.filter((other) => other !== spot)
	offerUndo(__("Mark removed"), () => (store.damages = before))
}
onMounted(async () => {
	try {
		views.value = (await api.diagram(store.visit.maintenance)).views
	} catch (e) {
		error.value = errorText(e)
	}
})
</script>

<template>
	<ScreenFrame v-model:error="error" :title="__('Body damage')">
		<template #meta>
			<span class="pill" :class="store.damages.length ? 'tone-problem' : 'tone-done'">
				{{ store.damages.length ? __("Damage marked") : __("Tap where the damage is") }}
				<span v-if="store.damages.length" class="ltr">{{ store.damages.length }}</span>
			</span>
		</template>
		<p v-if="!views.length && !error" class="muted">{{ __("Loading") }}</p>
		<CarDiagram v-else :views="views" :marks="store.damages" :labels="labels" @mark="mark" @unmark="unmark" />
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('parts')" />
		</template>
		<template #primary>
			<BigButton :icon="store.damages.length ? 'next' : 'good'" :label="store.damages.length ? __('Next') : __('No damage')" @press="go('photos')" />
		</template>
	</ScreenFrame>
</template>
