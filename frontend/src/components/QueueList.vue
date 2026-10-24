<script setup>
import { computed, ref } from "vue"
import { api, errorText } from "../api.js"
import { problem, success } from "../composables/useFeedback.js"
import { __, componentLabel, formatKm, reasonLabel, statusLabel } from "../i18n/index.js"
import { printDocument } from "../native.js"
import { openVisit, queue, stepForStatus, store } from "../store/index.js"
import AppIcon from "./AppIcon.vue"
import BigButton from "./BigButton.vue"
import EmptyState from "./EmptyState.vue"
import ErrorCard from "./ErrorCard.vue"
import PlateChip from "./PlateChip.vue"

defineProps({ compact: Boolean })
const rows = computed(() => queue.data || [])

const EXIT_ACTION = "Complete"
const EXIT_PASS = "Thermal Gate Exit Pass"
const acting = ref("")
const failed = ref("")

async function act(row) {
	const action = row.actions[0]
	acting.value = row.maintenance
	failed.value = ""
	try {
		await api.act(row.maintenance, action)
		success()
		if (action === EXIT_ACTION) {
			store.exited = row
			await printExit(row)
		}
		await queue.fetch()
	} catch (e) {
		failed.value = errorText(e)
		problem()
	}
	acting.value = ""
}
async function printExit(row) {
	acting.value = row.maintenance
	try {
		if (!(await printDocument("Maintenance", row.maintenance, EXIT_PASS))) failed.value = __("Printer not connected")
	} catch (e) {
		failed.value = errorText(e)
		problem()
	}
	acting.value = ""
}
function nextAction(row) {
	return !stepForStatus(row) && row.actions && row.actions.length ? row.actions[0] : ""
}
const ACTION_LABELS = { [EXIT_ACTION]: __("Approve exit") }
function actionLabel(action) {
	return ACTION_LABELS[action] || __(action)
}
function stageText(row) {
	if (row.status === "Due Alert") return __("Waiting for driver")
	if (row.status === "Full Inspection" && row.inspection) return __("Waiting for approval")
	return statusLabel(row.status)
}
function stageTone(row) {
	if (!stepForStatus(row)) return "quiet"
	if (row.status === "Full Inspection" && row.inspection) return "wait"
	if (["Approved", "Service", "Final Check"].indexOf(row.status) !== -1) return "done"
	return "wait"
}
function late(row) {
	return row.worst.km ? __("Late by {0}", [formatKm(row.worst.km)]) : __("Late by {0} days", [row.worst.days])
}
</script>

<template>
	<div class="queue" :class="{ 'queue-compact': compact }">
		<div v-if="store.exited && !compact" class="card visit">
			<span class="visit-top">
				<PlateChip :plate="store.exited.plate" size="md" />
				<span class="pill tone-done">{{ __("Exit approved") }}</span>
			</span>
			<span class="visit-model">{{ store.exited.model }}</span>
			<BigButton icon="printer" tone="quiet" :label="__('Gate Exit Pass')" :busy="acting === store.exited.maintenance" block @press="printExit(store.exited)" />
		</div>
		<p v-if="queue.loading && !rows.length" class="queue-loading">{{ __("Loading") }}</p>
		<EmptyState v-else-if="!rows.length" :label="__('No vehicles waiting')" />
		<component
			:is="stepForStatus(row) ? 'button' : 'div'"
			v-for="row in rows"
			:key="row.maintenance"
			class="card visit"
			:class="{ active: store.visit && store.visit.maintenance === row.maintenance, 'visit-open': stepForStatus(row) }"
			:type="stepForStatus(row) ? 'button' : null"
			@click="stepForStatus(row) && openVisit(row)"
		>
			<span class="visit-top">
				<PlateChip :plate="row.plate" size="md" />
				<span class="pill" :class="'tone-' + stageTone(row)">{{ stageText(row) }}</span>
			</span>
			<span class="visit-model">{{ row.model }}</span>
			<span v-if="row.due.length" class="visit-due">
				<span v-for="component in row.due" :key="component" class="pill tone-problem">
					<AppIcon :name="component" />
					{{ componentLabel(component) }}
				</span>
			</span>
			<span v-if="row.worst" class="visit-late">{{ late(row) }}</span>
			<span v-if="row.findings && row.findings.length" class="visit-findings">
				<span v-for="(finding, index) in row.findings" :key="index" class="visit-finding">
					<b>{{ __(finding.part) }}</b>
					<span v-if="finding.reason" class="pill" :class="finding.reason === 'Not Done' ? 'tone-problem' : 'tone-wait'">{{ reasonLabel(finding.reason) }}</span>
					<span v-if="finding.note" class="muted">{{ finding.note }}</span>
				</span>
			</span>
			<BigButton v-if="nextAction(row) && !compact" :label="actionLabel(nextAction(row))" :busy="acting === row.maintenance" block @press="act(row)" />
		</component>
		<ErrorCard :error="failed" @dismiss="failed = ''" />
	</div>
</template>

<style>
.queue {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(17rem, 1fr));
	gap: var(--s3);
}
.visit-findings {
	display: grid;
	gap: var(--s1);
}
.visit-finding {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: var(--s2);
	font-size: var(--t-sm);
}
.queue-compact {
	grid-template-columns: minmax(0, 1fr);
}
.queue .empty-state {
	grid-column: 1 / -1;
}
.queue-loading {
	padding: var(--s5);
	color: var(--ink-2);
	font-weight: 700;
}
.visit {
	display: flex;
	flex-direction: column;
	align-items: stretch;
	gap: var(--s2);
	min-height: 8rem;
	padding: var(--s4);
	text-align: start;
	border-width: 2px;
}
.visit-open:active {
	transform: scale(0.99);
}
.visit.active {
	border-color: var(--primary);
}
.visit-top {
	display: flex;
	align-items: center;
	justify-content: space-between;
	flex-wrap: wrap;
	gap: var(--s2);
}
.visit-model {
	font-size: var(--t-lg);
	font-weight: 800;
}
.visit-due {
	display: flex;
	flex-wrap: wrap;
	gap: var(--s2);
}
.visit-late {
	color: var(--problem);
	font-weight: 700;
}
</style>
