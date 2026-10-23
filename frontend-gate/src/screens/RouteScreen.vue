<script setup>
import { computed, ref } from "vue"
import { errorText } from "../api.js"
import { __ } from "../i18n.js"
import { photoList, sendEntry, store } from "../store.js"
import BigButton from "../components/BigButton.vue"
import GateIcon from "../components/GateIcon.vue"

const busy = ref(false)
const error = ref("")
const HANDOVER_TYPES = { Handover: __("Handover"), Return: __("Return"), Transfer: __("Transfer") }
const STATES = { "Due Alert": __("Due Alert"), "Driver Arrived": __("Driver Arrived") }

const routes = computed(() => {
	const vehicle = store.vehicle
	const visit = vehicle.maintenance
	const inWorkshop = visit && !STATES[visit.status]
	return [
		{
			key: "maintenance",
			icon: "wrench",
			title: __("Maintenance"),
			tone: inWorkshop || (!visit && !vehicle.can_open_maintenance) ? "bad" : visit ? "ok" : "warn",
			value: inWorkshop
				? __("Already in the workshop")
				: visit
					? STATES[visit.status]
					: vehicle.can_open_maintenance
						? __("New emergency visit")
						: __("No driver or project on this car"),
			open: !inWorkshop && (!!visit || vehicle.can_open_maintenance),
		},
		{
			key: "handover",
			icon: "keys",
			title: __("Handover and return"),
			tone: vehicle.handover ? "ok" : "bad",
			value: vehicle.handover ? HANDOVER_TYPES[vehicle.handover.handover_type] : __("No handover request for this car"),
			open: !!vehicle.handover,
		},
	]
})
const label = computed(() =>
	store.route === "maintenance" ? __("Send to maintenance") : store.route === "handover" ? __("Send to handover") : __("Send"),
)
const progress = computed(() => (store.result ? __("Photo {0} of {1}", [store.sent, photoList().length]) : ""))

async function send() {
	busy.value = true
	error.value = ""
	try {
		await sendEntry()
	} catch (e) {
		error.value = errorText(e)
	} finally {
		busy.value = false
	}
}
</script>

<template>
	<div class="page">
		<div class="screen">
			<h1 class="screen-title">{{ __("Next stop") }}</h1>
			<div class="routes" role="radiogroup">
				<button
					v-for="route in routes"
					:key="route.key"
					type="button"
					role="radio"
					class="route"
					:class="['tone-' + route.tone, { picked: store.route === route.key }]"
					:aria-checked="store.route === route.key"
					:disabled="!route.open || !!store.result"
					@click="store.route = route.key"
				>
					<GateIcon :name="route.icon" />
					<span class="text">
						<b>{{ route.title }}</b>
						<span class="value">{{ route.value }}</span>
					</span>
					<span class="mark"><GateIcon v-if="store.route === route.key" name="check" /></span>
				</button>
			</div>
			<p v-if="busy && progress" class="banner banner-warn" aria-live="polite">{{ progress }}</p>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
		</div>
		<div class="dock">
			<BigButton :icon="error ? 'retry' : 'check'" tone="ok" :label="error ? __('Try again') : label" :disabled="!store.route" :busy="busy" @press="send" />
		</div>
	</div>
</template>

<style scoped>
.routes {
	display: grid;
	gap: 12px;
}
.route {
	display: flex;
	align-items: center;
	gap: 14px;
	min-height: 88px;
	padding: 14px 16px;
	border-radius: var(--radius);
	border: 2px solid var(--line);
	border-left-width: 8px;
	background: var(--surface);
	text-align: start;
	transition:
		border-color var(--move) var(--ease),
		transform 120ms var(--ease);
}
.route:active:not(:disabled) {
	transform: scale(0.99);
}
.route:disabled {
	cursor: not-allowed;
	opacity: 0.7;
}
.tone-ok {
	border-left-color: var(--ok);
}
.tone-warn {
	border-left-color: var(--warn);
}
.tone-bad {
	border-left-color: var(--bad);
}
html[dir="rtl"] .route {
	border-left-width: 2px;
	border-right-width: 8px;
}
html[dir="rtl"] .tone-ok {
	border-right-color: var(--ok);
}
html[dir="rtl"] .tone-warn {
	border-right-color: var(--warn);
}
html[dir="rtl"] .tone-bad {
	border-right-color: var(--bad);
}
html[dir="rtl"] .route.picked {
	border-color: var(--accent);
}
.picked {
	border-color: var(--accent);
	box-shadow: 0 0 0 2px var(--accent);
}
.text {
	display: flex;
	flex-direction: column;
	flex: 1;
	min-width: 0;
}
.text b {
	font-size: 20px;
}
.tone-ok .value {
	color: var(--ok-ink);
}
.tone-warn .value {
	color: var(--warn-ink);
}
.tone-bad .value {
	color: var(--bad-ink);
}
.value {
	font-weight: 600;
}
.mark {
	width: 26px;
	color: var(--accent);
}
</style>
