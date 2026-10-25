<script setup>
import { computed, ref } from "vue"
import { __, componentLabel, formatKm, statusLabel } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { useFinalCheck } from "../../composables/useFinalCheck.js"
import { backToQueue, go, store } from "../../store/index.js"
import BigButton from "../../components/BigButton.vue"
import CardProgress from "../../components/CardProgress.vue"
import FindingsTable from "../../components/FindingsTable.vue"
import PlateChip from "../../components/PlateChip.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import ServiceChecklist from "../../components/ServiceChecklist.vue"

const vehicle = computed(() => store.checklist.vehicle)
const replaced = store.checklist.components.filter((row) => row.ticked)

function itemName(row) {
	const item = row.items.find((i) => i.item_code === row.item)
	return item ? item.item_name + " × " + row.qty : ""
}
if (!store.checklist.checks) {
	const saved = {}
	store.checklist.final_check.forEach((row) => (saved[row.item] = row.condition))
	const answer = (item, allowed) => (allowed.indexOf(saved[item]) !== -1 ? saved[item] : "")
	store.checklist.checks = replaced
		.map((row) => ({ kind: "part", item: row.component, label: componentLabel(row.component) || row.component, note: itemName(row), icon: row.component, condition: answer(row.component, ["Installed"]) }))
		.concat(store.checklist.service_checklist.map((row) => ({ kind: "service", item: row.item, label: row.label, condition: answer(row.item, ["Done", "Not Done"]) })))
}
const checks = store.checklist.checks
const findings = store.checklist.findings
const check = useFinalCheck(checks, findings)
const busy = ref(false)
const error = ref("")

const DONE = { part: "Installed", service: "Done" }
function allDone() {
	checks.filter((row) => !row.condition).forEach((row) => check.answer(row, DONE[row.kind]))
}
async function finish() {
	if (check.progress.guard()) return
	busy.value = true
	try {
		store.result = await api.finish(store.visit.maintenance, check.answers(), findings)
		go("done")
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
</script>

<template>
	<ScreenFrame :title="__('Final check')" v-model:error="error">
		<template #meta>
			<span class="pill" :class="check.open.value ? 'tone-wait' : 'tone-done'">{{ check.open.value ? __("{0} left", [check.open.value]) : statusLabel(store.checklist.status) }}</span>
		</template>
		<div class="review">
			<div class="card review-vehicle">
				<PlateChip :plate="vehicle.plate" size="lg" />
				<div>
					<p class="review-model">{{ vehicle.model }}</p>
					<p class="muted">{{ formatKm(store.checklist.odometer) }}</p>
				</div>
			</div>
			<CardProgress :items="check.cards.value" @show="check.progress.show" />
			<BigButton v-if="check.open.value" icon="done" tone="done" :label="__('All done')" block @press="allDone" />
			<ServiceChecklist :rows="checks" @answer="check.answer" />
			<FindingsTable :findings="findings" :parts="check.parts.value" />
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="backToQueue" />
		</template>
		<template #primary>
			<BigButton icon="done" tone="done" :label="busy ? __('Finishing') : check.progress.nextLabel(__('Finish maintenance'))" :busy="busy" @press="finish" />
		</template>
	</ScreenFrame>
</template>

<style>
.review {
	display: grid;
	gap: var(--s3);
}
.review-vehicle {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: var(--s4);
	padding: var(--s4);
}
.review-model {
	font-size: var(--t-lg);
	font-weight: 800;
}
</style>
