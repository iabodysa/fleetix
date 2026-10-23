<script setup>
import { computed } from "vue"
import FeatherIcon from "frappe-ui/src/components/FeatherIcon.vue"
import { ICONS, MIRRORED } from "../icons/index.js"

const props = defineProps({ name: { type: String, required: true }, size: { type: String, default: "md" } })
const feather = computed(() => ICONS[props.name] || "circle")
const mirrored = computed(() => MIRRORED.indexOf(props.name) !== -1)
</script>

<template>
	<FeatherIcon :name="feather" :stroke-width="2.25" class="app-icon" :class="['app-icon-' + size, { 'app-icon-mirror': mirrored }]" aria-hidden="true" />
</template>

<style>
.app-icon {
	flex: none;
	width: var(--icon);
	height: var(--icon);
}
.app-icon-lg {
	width: var(--icon-lg);
	height: var(--icon-lg);
}
.app-icon-xl {
	width: 3rem;
	height: 3rem;
}
html[dir="rtl"] .app-icon-mirror {
	transform: scaleX(-1);
}
</style>
