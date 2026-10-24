<script setup>
import { computed, ref } from "vue"
import { FINDING_REASONS, __, reasonLabel } from "../i18n/index.js"
import AppIcon from "./AppIcon.vue"

const props = defineProps({ findings: { type: Array, required: true }, parts: { type: Array, default: () => [] } })
const COMMON_PARTS = [
	{ key: "Engine", label: __("Engine") },
	{ key: "Brakes", label: __("Brakes") },
	{ key: "Suspension", label: __("Suspension") },
	{ key: "Air Conditioning", label: __("Air Conditioning") },
	{ key: "Electrical", label: __("Electrical") },
	{ key: "Body", label: __("Body") },
]
const choices = computed(() => {
	const seen = {}
	return props.parts.concat(COMMON_PARTS).filter((part) => !seen[part.key] && (seen[part.key] = true))
})
const part = ref("")
const reason = ref("")
const note = ref("")

function partLabel(key) {
	const found = choices.value.find((row) => row.key === key)
	return found ? found.label : __(key)
}
function add() {
	if (!part.value || (!reason.value && !note.value.trim())) return
	props.findings.push({ part: part.value, reason: reason.value, note: note.value.trim() })
	part.value = ""
	reason.value = ""
	note.value = ""
}
</script>

<template>
	<div class="card findings">
		<h2 class="findings-title"><AppIcon name="note" />{{ __("Findings") }}</h2>
		<div v-for="(row, index) in findings" :key="index" class="finding">
			<b>{{ partLabel(row.part) }}</b>
			<span v-if="row.reason" class="pill" :class="row.reason === 'Not Done' ? 'tone-problem' : 'tone-wait'">{{ reasonLabel(row.reason) }}</span>
			<span class="finding-note">{{ row.note }}</span>
			<button type="button" class="finding-remove" :aria-label="__('Remove')" @click="findings.splice(index, 1)"><AppIcon name="close" /></button>
		</div>
		<p class="muted findings-step">{{ __("Part") }}</p>
		<div class="findings-chips">
			<button v-for="row in choices" :key="row.key" type="button" class="chip" :class="{ pressed: part === row.key }" :aria-pressed="part === row.key ? 'true' : 'false'" @click="part = part === row.key ? '' : row.key">
				{{ row.label }}
			</button>
		</div>
		<template v-if="part">
			<p class="muted findings-step">{{ __("Reason") }}</p>
			<div class="findings-chips">
				<button v-for="key in FINDING_REASONS" :key="key" type="button" class="chip" :class="{ pressed: reason === key }" :aria-pressed="reason === key ? 'true' : 'false'" @click="reason = reason === key ? '' : key">
					{{ reasonLabel(key) }}
				</button>
			</div>
			<div class="findings-add">
				<input v-model="note" class="findings-input" type="text" maxlength="140" :placeholder="__('Short note')" autocomplete="off" />
				<button type="button" class="check-answer tone-done" :disabled="!reason && !note.trim()" @click="add"><AppIcon name="plus" />{{ __("Add note") }}</button>
			</div>
		</template>
	</div>
</template>

<style>
.findings {
	display: grid;
	gap: var(--s2);
	padding: var(--s4);
}
.findings-title {
	display: flex;
	align-items: center;
	gap: var(--s2);
	font-size: var(--t-lg);
}
.finding {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: var(--s2);
	padding: var(--s2) 0;
	border-bottom: 1px solid var(--line);
}
.finding-note {
	flex: 1;
	min-width: 6rem;
	color: var(--ink-2);
}
.finding-remove {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: var(--tap);
	height: var(--tap);
	border: 0;
	background: none;
}
.findings-step {
	margin-top: var(--s2);
	font-weight: 700;
}
.findings-chips {
	display: flex;
	flex-wrap: wrap;
	gap: var(--s2);
}
.chip {
	min-height: 3rem;
	padding: 0 var(--s4);
	border: 2px solid var(--line);
	border-radius: 999px;
	background: var(--surface);
	font-weight: 700;
}
.chip.pressed {
	border-color: var(--primary);
	background: var(--primary);
	color: #fff;
}
.findings-add {
	display: flex;
	flex-wrap: wrap;
	gap: var(--s2);
}
.findings-input {
	flex: 1;
	min-width: 12rem;
	min-height: var(--tap);
	padding: 0 var(--s3);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	font: inherit;
}
</style>
