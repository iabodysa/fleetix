<script setup>
import { onBeforeUnmount, ref, watch } from "vue"
import { api, errorText } from "../api.js"
import { problem, success } from "../composables/useFeedback.js"
import { __, componentLabel, formatKm } from "../i18n/index.js"
import { openVisit } from "../store/index.js"
import AppIcon from "./AppIcon.vue"
import EmptyState from "./EmptyState.vue"
import ErrorCard from "./ErrorCard.vue"
import PlateChip from "./PlateChip.vue"

const props = defineProps({ filter: { type: String, required: true } })
const TONE = { overdue: "problem", soon: "wait", ok: "done", none: "quiet" }
const SEARCH_MS = 250
const rows = ref([])
const loading = ref(false)
const opening = ref("")
const error = ref("")
let timer = null
let asked = 0

function search() {
	const ticket = ++asked
	loading.value = true
	api.findVehicles(props.filter).then(
		(found) => {
			if (ticket !== asked) return
			rows.value = found
			loading.value = false
		},
		(e) => {
			if (ticket !== asked) return
			error.value = errorText(e)
			loading.value = false
		},
	)
}
function stateText(row) {
	if (row.state === "overdue") return row.worst && row.worst.km ? __("Late by {0}", [formatKm(row.worst.km)]) : __("Overdue")
	if (row.state === "soon") return __("Due now")
	if (row.state === "ok") return __("{0} left", [formatKm(row.remaining_km)])
	return __("No maintenance data")
}
async function open(row) {
	opening.value = row.vehicle
	try {
		const visit = await api.openVehicle(row.vehicle)
		success()
		await openVisit(visit)
	} catch (e) {
		error.value = errorText(e)
		problem()
	}
	opening.value = ""
}
watch(
	() => props.filter,
	() => {
		clearTimeout(timer)
		timer = setTimeout(search, SEARCH_MS)
	},
	{ immediate: true },
)
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
	<div class="queue">
		<p v-if="loading && !rows.length" class="queue-loading">{{ __("Loading") }}</p>
		<EmptyState v-else-if="!rows.length" :label="__('No vehicle with this plate')" />
		<button
			v-for="row in rows"
			:key="row.vehicle"
			class="card visit visit-open found"
			:class="'found-' + TONE[row.state]"
			type="button"
			:disabled="!!opening"
			@click="open(row)"
		>
			<span class="visit-top">
				<PlateChip :plate="row.plate" size="md" />
				<span class="pill" :class="'tone-' + TONE[row.state]">{{ stateText(row) }}</span>
			</span>
			<span class="visit-model">{{ row.model }}</span>
			<span v-if="row.due.length" class="visit-due">
				<span v-for="component in row.due" :key="component" class="pill tone-problem">
					<AppIcon :name="component" />
					{{ componentLabel(component) }}
				</span>
			</span>
			<span v-if="row.maintenance" class="muted">{{ __("Open visit") }}</span>
			<span v-if="opening === row.vehicle" class="muted">{{ __("Opening") }}</span>
		</button>
		<ErrorCard :error="error" @dismiss="error = ''" />
	</div>
</template>

<style>
.found {
	border-left-width: 0.5rem;
}
html[dir="rtl"] .found {
	border-left-width: 2px;
	border-right-width: 0.5rem;
}
.found-problem {
	border-color: var(--problem);
}
.found-wait {
	border-color: var(--wait);
}
.found-done {
	border-color: var(--done);
}
.found-quiet {
	border-color: var(--line);
	opacity: 0.85;
}
</style>
