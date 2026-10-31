<script setup>
defineProps({
	name: { type: String, required: true },
	code: { type: String, default: "" },
	image: { type: String, default: "" },
	facts: { type: Array, default: () => [] },
	pressable: { type: Boolean, default: false },
})
defineEmits(["press"])
</script>

<template>
	<component :is="pressable ? 'button' : 'div'" class="card part" :type="pressable ? 'button' : undefined" @click="pressable && $emit('press')">
		<img v-if="image" class="thumb" :src="image" :alt="name" loading="lazy" />
		<span class="text">
			<span class="name">{{ name }}</span>
			<span v-if="code" class="code" dir="ltr">{{ code }}</span>
			<dl v-if="facts.length" class="facts">
				<div v-for="fact in facts" :key="fact.label">
					<dt>{{ fact.label }}</dt>
					<dd :dir="fact.ltr ? 'ltr' : undefined">{{ fact.value }}</dd>
				</div>
			</dl>
		</span>
	</component>
</template>

<style scoped>
.part {
	display: flex;
	align-items: flex-start;
	gap: 12px;
	width: 100%;
	padding: 12px;
	text-align: start;
}
.thumb {
	flex: none;
	width: 72px;
	height: 72px;
	border-radius: 10px;
	object-fit: cover;
	background: var(--surface-2);
}
.text {
	display: flex;
	flex-direction: column;
	gap: 4px;
	min-width: 0;
}
.name {
	font-weight: 700;
}
.code {
	color: var(--ink-2);
	text-align: start;
}
.facts {
	display: flex;
	flex-wrap: wrap;
	gap: 4px 16px;
	margin: 0;
}
.facts div {
	display: flex;
	gap: 6px;
}
dt {
	color: var(--ink-2);
}
dd {
	margin: 0;
	font-weight: 700;
}
</style>
