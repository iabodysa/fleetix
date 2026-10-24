<script setup>
import { computed, ref } from "vue"
import { __, formatKm } from "../../i18n/index.js"
import { offerUndo } from "../../composables/useUndo.js"
import { backToQueue, go, store } from "../../store/index.js"
import BigButton from "../../components/BigButton.vue"
import NumberPad from "../../components/NumberPad.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const BIG_JUMP_KM = 20000
const last = computed(() => store.visit.last_odometer || 0)
const reading = computed(() => Number(store.odometer || 0))
const diff = computed(() => reading.value - last.value)
const cells = computed(() => ("0000000" + (store.odometer || "")).slice(-7).split(""))
const lead = computed(() => 7 - (store.odometer || "").length)
const error = ref("")

function press(key) {
	if (store.odometer.length < 7) store.odometer = (store.odometer + key).replace(/^0+/, "")
	error.value = ""
}
function clear() {
	const before = store.odometer
	if (!before) return
	store.odometer = ""
	offerUndo(__("Reading cleared"), () => (store.odometer = before))
}
function next() {
	if (!reading.value) {
		error.value = __("Enter the odometer reading")
		return
	}
	if (diff.value < 0) {
		error.value = __("Odometer reading is below the last reading {0}", [formatKm(last.value)])
		return
	}
	go("parts")
	if (diff.value > BIG_JUMP_KM) offerUndo(__("Difference is above 20,000 km"), () => go("odometer"))
}
</script>

<template>
	<ScreenFrame :title="__('Odometer reading')" v-model:error="error">
		<div class="odometer">
			<div class="drum ltr">
				<span v-for="(digit, index) in cells" :key="index" class="drum-cell" :class="{ lead: digit === '0' && index < lead }">{{ digit }}</span>
				<span class="drum-unit">{{ __("km") }}</span>
			</div>
			<dl class="facts">
				<div>
					<dt>{{ __("Last reading") }}</dt>
					<dd>{{ formatKm(last) }}</dd>
				</div>
				<div>
					<dt>{{ __("Difference") }}</dt>
					<dd class="ltr" :class="{ 'odometer-jump': diff > BIG_JUMP_KM }">{{ reading ? (diff >= 0 ? "+" : "") + diff.toLocaleString("en-US") : "-" }}</dd>
				</div>
			</dl>
		</div>
		<template #aside>
			<NumberPad @key="press" @clear="clear" @erase="store.odometer = store.odometer.slice(0, -1)" />
		</template>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="backToQueue" />
		</template>
		<template #primary>
			<BigButton icon="next" :label="diff > BIG_JUMP_KM ? __('Confirm reading') : __('Next')" @press="next" />
		</template>
	</ScreenFrame>
</template>

<style>
.odometer {
	display: flex;
	flex-direction: column;
	gap: var(--s5);
}
.drum {
	display: flex;
	align-items: center;
	gap: var(--s1);
	width: fit-content;
	max-width: 100%;
	padding: var(--s3);
	border-radius: var(--r-lg);
	background: var(--drum);
	color: var(--drum-ink);
}
.drum-cell {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: 2.6rem;
	height: 4rem;
	border-radius: var(--r-sm);
	background: rgba(255, 255, 255, 0.08);
	font-size: var(--t-xxl);
	font-weight: 800;
	font-variant-numeric: tabular-nums;
}
.drum-cell.lead {
	opacity: 0.3;
}
.drum-unit {
	padding-left: var(--s2);
	font-weight: 700;
}
html[dir="rtl"] .drum-unit {
	padding-left: 0;
	padding-right: var(--s2);
}
.odometer-jump {
	color: var(--wait);
}
@media (max-width: 480px) {
	.drum-cell {
		width: 2.1rem;
		height: 3.25rem;
		font-size: var(--t-xl);
	}
}
</style>
