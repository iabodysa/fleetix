<template>
	<div class="queue" :class="{ 'queue-compact': compact }">
		<p v-if="queue.loading && !rows.length" class="empty">{{ __("Loading") }}</p>
		<p v-else-if="!rows.length" class="empty">{{ __("No vehicles waiting") }}</p>
		<button
			v-for="row in rows"
			:key="row.maintenance"
			class="card visit"
			:class="{ active: store.visit && store.visit.maintenance === row.maintenance }"
			type="button"
			:disabled="!stepForStatus(row)"
			@click="openVisit(row)"
		>
			<div class="visit-top">
				<PlateChip :plate="row.plate" size="sm" />
				<span class="pill" :class="'pill-' + stageTone(row)">{{ stageText(row) }}</span>
			</div>
			<div class="visit-model">{{ row.model }}</div>
			<div class="chips">
				<span v-for="component in row.due" :key="component" class="chip chip-bad">{{ componentLabel(component) }}</span>
			</div>
			<div v-if="row.worst" class="visit-worst">
				{{ row.worst.km ? __("Late by {0}", [formatKm(row.worst.km)]) : __("Late by {0} days", [row.worst.days]) }}
			</div>
		</button>
	</div>
</template>

<script setup>
import { computed } from "vue"
import { __, componentLabel, formatKm, statusLabel } from "../translate.js"
import { openVisit, queue, stepForStatus, store } from "../store.js"
import PlateChip from "./PlateChip.vue"

const props = defineProps({ compact: Boolean, filter: { type: String, default: "" } })
const rows = computed(() =>
	(queue.data || []).filter((row) => !props.filter || String(row.plate).indexOf(props.filter) !== -1)
)

function stageText(row) {
	if (row.status === "Due Alert") return __("Waiting for driver")
	if (row.status === "Full Inspection" && row.inspection) return __("Waiting for approval")
	return statusLabel(row.status)
}
function stageTone(row) {
	if (!stepForStatus(row)) return "muted"
	if (row.status === "Full Inspection" && row.inspection) return "warn"
	if (["Approved", "Service", "Final Check"].indexOf(row.status) !== -1) return "ok"
	return "accent"
}
</script>
