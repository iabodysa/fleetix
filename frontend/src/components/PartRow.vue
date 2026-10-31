<script setup>
defineProps({
	name: { type: String, required: true },
	code: { type: String, default: "" },
	image: { type: String, default: "" },
	facts: { type: Array, default: () => [] },
	pressable: Boolean,
})
defineEmits(["press"])
</script>

<template>
	<component :is="pressable ? 'button' : 'div'" class="card part-row" :type="pressable ? 'button' : undefined" @click="pressable && $emit('press')">
		<img v-if="image" class="part-row-thumb" :src="image" :alt="name" loading="lazy" />
		<span class="part-row-text">
			<span class="part-row-name">{{ name }}</span>
			<span v-if="code" class="muted ltr">{{ code }}</span>
			<dl v-if="facts.length" class="facts part-row-facts">
				<div v-for="fact in facts" :key="fact.label">
					<dt>{{ fact.label }}</dt>
					<dd :class="{ ltr: fact.ltr }">{{ fact.value }}</dd>
				</div>
			</dl>
		</span>
	</component>
</template>

<style>
.part-row {
	display: flex;
	align-items: flex-start;
	gap: var(--s3);
	width: 100%;
	padding: var(--s3);
	text-align: start;
}
.part-row-thumb {
	flex: none;
	width: 5rem;
	height: 5rem;
	border-radius: var(--r-md);
	background: var(--surface-2);
	object-fit: cover;
}
.part-row-text {
	display: flex;
	flex-direction: column;
	gap: var(--s1);
	min-width: 0;
}
.part-row-name {
	font-size: var(--t-lg);
	font-weight: 800;
}
.part-row-facts {
	gap: var(--s2) var(--s4);
}
</style>
