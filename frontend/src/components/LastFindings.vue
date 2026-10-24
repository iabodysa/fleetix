<script setup>
import { __, reasonLabel } from "../i18n/index.js"
import AppIcon from "./AppIcon.vue"

defineProps({ last: { type: Object, default: null } })
</script>

<template>
	<div v-if="last && last.rows.length" class="card last-findings">
		<h2 class="findings-title"><AppIcon name="note" />{{ __("Notes from last visit") }}</h2>
		<div v-for="(row, index) in last.rows" :key="index" class="finding">
			<b>{{ __(row.part) }}</b>
			<span v-if="row.reason" class="pill" :class="row.reason === 'Not Done' ? 'tone-problem' : 'tone-wait'">{{ reasonLabel(row.reason) }}</span>
			<span class="finding-note">{{ row.note }}</span>
		</div>
	</div>
</template>

<style>
.last-findings {
	display: grid;
	gap: var(--s2);
	padding: var(--s4);
	border-color: var(--wait);
	border-width: 2px;
}
</style>
