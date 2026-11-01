<script setup>
import { computed } from "vue"
import { __ } from "../i18n/index.js"
import BigButton from "./BigButton.vue"

const props = defineProps({
	item: { type: Object, required: true },
	pressed: Boolean,
	requested: Boolean,
	other: Boolean,
})
defineEmits(["pick", "request"])
const empty = computed(() => props.item.stock !== undefined && !(props.item.stock > 0))
</script>

<template>
	<div class="stock-choice">
		<button
			class="part-item"
			:class="{ pressed, 'part-item-other': other, 'part-item-empty': empty }"
			type="button"
			:disabled="empty"
			:aria-pressed="pressed ? 'true' : 'false'"
			@click="$emit('pick')"
		>
			<img v-if="item.image" class="stock-choice-thumb" :src="item.image" :alt="item.item_name" loading="lazy" />
			<span class="part-item-name">{{ item.item_name }}</span>
			<span v-if="item.stock !== undefined" class="muted">{{ __("Stock") }} <span class="ltr">{{ item.stock }}</span> {{ item.stock_uom }}</span>
		</button>
		<BigButton v-if="empty" icon="send" tone="quiet" :label="requested ? __('Purchase requested') : __('Purchase request')" :disabled="requested" @press="$emit('request')" />
	</div>
</template>

<style>
.stock-choice {
	display: grid;
	gap: var(--s2);
	align-content: start;
}
.stock-choice-thumb {
	width: 100%;
	height: 6rem;
	border-radius: var(--r-md);
	background: var(--surface-2);
	object-fit: contain;
}
.part-item-empty {
	opacity: 0.45;
	filter: grayscale(1);
}
</style>
