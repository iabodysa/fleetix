<script setup>
import { computed, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { offerUndo } from "../../composables/useUndo.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import CarDiagram from "../../components/CarDiagram.vue"
import IconTile from "../../components/IconTile.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const AREAS = {
	Front: __("Front"),
	Rear: __("Rear"),
	"Left Side": __("Left Side"),
	"Right Side": __("Right Side"),
	Roof: __("Roof"),
}
const KINDS = { Scratch: __("Scratch"), Dent: __("Dent"), Broken: __("Broken"), Missing: __("Missing") }
const labels = Object.assign({ title: __("Vehicle body") }, AREAS)
const selected = ref("")
const marked = computed(() => store.damages.map((row) => row.area))

function pick(area) {
	selected.value = selected.value === area ? "" : area
}
function mark(kind) {
	const area = selected.value
	store.damages = store.damages.filter((row) => row.area !== area).concat([{ area, kind }])
	selected.value = ""
}
function remove(row) {
	const before = store.damages.slice()
	store.damages = store.damages.filter((other) => other !== row)
	offerUndo(__("{0} removed", [AREAS[row.area]]), () => (store.damages = before))
}
</script>

<template>
	<ScreenFrame :title="__('Body damage')">
		<div class="damage">
			<CarDiagram :marked="marked" :selected="selected" :labels="labels" @pick="pick" />
			<div class="damage-side">
				<template v-if="selected">
					<h2 class="damage-area"><AppIcon name="damage" />{{ AREAS[selected] }}</h2>
					<div class="tile-grid damage-kinds">
						<IconTile v-for="(label, kind) in KINDS" :key="kind" :icon="kind" :label="label" tone="problem" @press="mark(kind)" />
					</div>
				</template>
				<template v-else>
					<p class="damage-hint">{{ store.damages.length ? __("Damage marked") : __("Tap the damaged part") }}</p>
					<div class="damage-list">
						<button v-for="row in store.damages" :key="row.area" class="pill tone-problem damage-chip" type="button" @click="remove(row)">
							{{ AREAS[row.area] }} · {{ KINDS[row.kind] }}
							<AppIcon name="close" />
						</button>
					</div>
				</template>
			</div>
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('parts')" />
		</template>
		<template #primary>
			<BigButton :icon="store.damages.length ? 'next' : 'good'" :label="store.damages.length ? __('Next') : __('No damage')" @press="go('photos')" />
		</template>
	</ScreenFrame>
</template>

<style>
.damage {
	display: grid;
	grid-template-columns: minmax(12rem, 18rem) minmax(0, 1fr);
	gap: var(--s5);
	align-items: start;
}
.damage-side {
	display: flex;
	flex-direction: column;
	gap: var(--s4);
	min-width: 0;
}
.damage-area {
	display: flex;
	align-items: center;
	gap: var(--s2);
	color: var(--problem);
}
.damage-kinds {
	grid-template-columns: repeat(auto-fill, minmax(9.5rem, 1fr));
}
.damage-hint {
	font-size: var(--t-lg);
	font-weight: 700;
}
.damage-list {
	display: flex;
	flex-wrap: wrap;
	gap: var(--s2);
}
.damage-chip {
	min-height: var(--tap);
	border: 0;
	font-size: var(--t-md);
}
@media (max-width: 760px) {
	.damage {
		grid-template-columns: minmax(0, 1fr);
	}
	.car-diagram {
		max-width: 11rem;
	}
}
</style>
