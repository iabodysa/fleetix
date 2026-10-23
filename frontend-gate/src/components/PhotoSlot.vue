<script setup>
import GateIcon from "./GateIcon.vue"

defineProps({ label: { type: String, required: true }, photo: { type: Object, default: null } })
const emit = defineEmits(["pick"])

function picked(event) {
	const file = event.target.files && event.target.files[0]
	event.target.value = ""
	if (file) emit("pick", file)
}
</script>

<template>
	<label class="slot" :class="{ taken: photo }">
		<img v-if="photo" :src="photo.url" alt="" />
		<span v-else class="empty"><GateIcon name="camera" /></span>
		<span class="name">
			<GateIcon v-if="photo" name="check" />
			{{ label }}
		</span>
		<input type="file" accept="image/*" capture="environment" @change="picked" />
	</label>
</template>

<style scoped>
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
