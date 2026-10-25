<script setup>
import { __ } from "../i18n.js"
import GateIcon from "./GateIcon.vue"

defineProps({ label: { type: String, required: true }, photo: { type: Object, default: null } })
const emit = defineEmits(["pick", "retry"])
const STATES = { saving: __("Saving"), saved: __("Saved"), uploading: __("Uploading"), uploaded: __("Uploaded"), failed: __("Upload failed") }

function picked(event) {
	const file = event.target.files && event.target.files[0]
	event.target.value = ""
	if (file) emit("pick", file)
}
</script>

<template>
	<div class="cell">
		<label class="slot" :class="[{ taken: photo }, photo && 'is-' + photo.state]">
			<img v-if="photo && photo.url" :src="photo.url" alt="" />
			<span v-else class="empty"><GateIcon name="camera" /></span>
			<span class="name">
				<GateIcon v-if="photo && photo.state === 'uploaded'" name="check" />
				{{ label }}
			</span>
			<span v-if="photo" class="state" aria-live="polite">{{ STATES[photo.state] }}</span>
			<input type="file" accept="image/*" capture="environment" @change="picked" />
		</label>
		<button v-if="photo && photo.state === 'failed'" type="button" class="retry" @click="emit('retry')">
			<GateIcon name="retry" />{{ __("Try again") }}
		</button>
	</div>
</template>

<style scoped>
.cell {
	display: flex;
	flex-direction: column;
	gap: 6px;
}
.slot {
	position: relative;
	display: flex;
	flex-direction: column;
	border: 2px dashed var(--line);
	border-radius: var(--radius);
	overflow: hidden;
	min-height: 132px;
	background: var(--surface);
	cursor: pointer;
}
.slot:focus-within {
	outline: 3px solid var(--focus);
}
.taken {
	border-style: solid;
	border-color: var(--ok);
}
img {
	width: 100%;
	height: 96px;
	object-fit: cover;
}
.empty {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	color: var(--ink-2);
	min-height: 88px;
}
.name {
	display: flex;
	align-items: center;
	gap: 6px;
	padding: 8px 10px;
	font-weight: 700;
	min-height: 40px;
}
.taken .name {
	color: var(--ok-ink);
	background: var(--ok-bg);
}
.state {
	padding: 0 10px 8px;
	font-weight: 600;
	font-size: 14px;
	color: var(--ink-2);
}
.taken .state {
	background: var(--ok-bg);
}
.is-failed {
	border-color: var(--bad);
}
.is-failed .name,
.is-failed .state {
	color: var(--bad-ink);
	background: transparent;
}
.is-saving,
.is-saved,
.is-uploading {
	border-color: var(--warn);
}
.is-saving .name,
.is-saved .name,
.is-uploading .name,
.is-saving .state,
.is-saved .state,
.is-uploading .state {
	color: var(--warn-ink);
	background: transparent;
}
.retry {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 6px;
	min-height: 48px;
	border: 2px solid var(--bad);
	border-radius: var(--radius);
	background: var(--surface);
	color: var(--bad-ink);
	font-weight: 700;
}
.retry :deep(.icon),
.name :deep(.icon) {
	width: 18px;
	height: 18px;
}
input {
	position: absolute;
	opacity: 0;
	width: 1px;
	height: 1px;
}
</style>
