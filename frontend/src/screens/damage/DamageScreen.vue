<script setup>
import { computed, onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { offerUndo } from "../../composables/useUndo.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import CarDiagram from "../../components/CarDiagram.vue"
import IconTile from "../../components/IconTile.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const labels = {
	title: __("Vehicle body"),
	remove: __("Remove mark"),
	right: __("Right Side"),
	left: __("Left Side"),
	front: __("Front"),
	rear: __("Rear"),
}
const KINDS = { Scratch: __("Scratch"), Dent: __("Dent"), Broken: __("Broken"), Missing: __("Missing") }
const views = ref([])
const error = ref("")
const busy = ref(false)
const picked = ref(-1)
const current = computed(() => store.damages[picked.value])

function mark(spot) {
	store.damages = store.damages.concat([Object.assign({ kind: null }, spot)])
	picked.value = store.damages.length - 1
}
function unmark(spot) {
	const before = store.damages.slice()
	store.damages = store.damages.filter((other) => other !== spot)
	picked.value = -1
	offerUndo(__("Mark removed"), () => (store.damages = before))
}
function setKind(kind) {
	current.value.kind = current.value.kind === kind ? null : kind
}
async function next() {
	busy.value = true
	try {
		store.photos = await api.saveMarks(store.visit.maintenance, store.damages)
		go("photos")
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
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
		<template #aside>
			<div class="damage-side">
				<div class="damage-list">
					<button
						v-for="(spot, index) in store.damages"
						:key="index"
						class="pill damage-chip"
						:class="index === picked ? 'tone-wait' : 'tone-problem'"
						type="button"
						@click="picked = index"
					>
						<span class="ltr">{{ index + 1 }}</span>
						<span v-if="spot.kind">{{ KINDS[spot.kind] }}</span>
					</button>
				</div>
				<template v-if="current">
					<h2 class="damage-area"><AppIcon name="damage" /><span class="ltr">{{ picked + 1 }}</span></h2>
					<div class="tile-grid damage-kinds">
						<IconTile v-for="(label, kind) in KINDS" :key="kind" :icon="kind" :label="label" tone="problem" :pressed="current.kind === kind" @press="setKind(kind)" />
					</div>
				</template>
			</div>
		</template>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('parts')" />
		</template>
		<template #primary>
			<BigButton :icon="store.damages.length ? 'next' : 'good'" :label="store.damages.length ? __('Next') : __('No damage')" :busy="busy" @press="next" />
		</template>
	</ScreenFrame>
</template>

<style>
.damage-side {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
}
.damage-list {
	display: flex;
	flex-wrap: wrap;
	gap: var(--s2);
}
.damage-chip {
	min-height: var(--tap);
	min-width: var(--tap);
	border: 0;
	font-size: var(--t-md);
}
.damage-area {
	display: flex;
	align-items: center;
	gap: var(--s2);
	color: var(--problem);
}
.damage-kinds {
	grid-template-columns: repeat(2, minmax(0, 1fr));
}
</style>
