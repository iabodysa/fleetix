<script setup>
import { __ } from "../i18n/index.js"
import AppIcon from "./AppIcon.vue"

defineProps({ rows: { type: Array, required: true } })
const emit = defineEmits(["answer"])
</script>

<template>
	<div class="checks">
		<div v-for="row in rows" :key="row.kind + row.item" class="card check-row" :data-card="row.kind + row.item">
			<span class="check-name">
				<AppIcon :name="row.icon || (row.kind === 'part' ? 'item' : 'review')" />
				<span>
					<b>{{ row.label }}</b>
					<span v-if="row.note" class="muted check-note">{{ row.note }}</span>
				</span>
			</span>
			<span class="check-answers">
				<button
					v-if="row.kind === 'part'"
					type="button"
					class="check-answer"
					:class="{ 'tone-done': row.condition === 'Installed' }"
					:aria-pressed="row.condition === 'Installed' ? 'true' : 'false'"
					@click="emit('answer', row, row.condition === 'Installed' ? '' : 'Installed')"
				>
					<AppIcon name="done" />{{ __("Installed") }}
				</button>
				<template v-else>
					<button type="button" class="check-answer" :class="{ 'tone-done': row.condition === 'Done' }" :aria-pressed="row.condition === 'Done' ? 'true' : 'false'" @click="emit('answer', row, 'Done')">
						<AppIcon name="done" />{{ __("Done") }}
					</button>
					<button type="button" class="check-answer" :class="{ 'tone-problem': row.condition === 'Not Done' }" :aria-pressed="row.condition === 'Not Done' ? 'true' : 'false'" @click="emit('answer', row, 'Not Done')">
						<AppIcon name="close" />{{ __("Not Done") }}
					</button>
				</template>
			</span>
		</div>
	</div>
</template>

<style>
.checks {
	display: grid;
	gap: var(--s2);
}
.check-row {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: var(--s3);
	padding: var(--s3) var(--s4);
	border-width: 2px;
}
.check-name {
	display: flex;
	flex: 1;
	align-items: center;
	gap: var(--s3);
	min-width: 12rem;
}
.check-note {
	display: block;
	font-size: var(--t-sm);
}
.check-answers {
	display: flex;
	gap: var(--s2);
}
.check-answer {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	gap: var(--s2);
	min-width: 9.5rem;
	min-height: var(--tap);
	padding: 0 var(--s4);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface);
	font-weight: 800;
}
.check-answer.tone-done {
	border-color: var(--done);
}
.check-answer.tone-problem {
	border-color: var(--problem);
}
</style>
