<script setup>
import { computed, ref, watch } from "vue"
import AppIcon from "./AppIcon.vue"

const props = defineProps({ error: { type: [String, Object], default: "" } })
const emit = defineEmits(["dismiss"])
const open = ref(false)
const text = computed(() => (props.error && typeof props.error === "object" ? props.error.text : props.error))
const detail = computed(() => (props.error && typeof props.error === "object" ? props.error.detail : ""))
const retry = computed(() => (props.error && typeof props.error === "object" && typeof props.error.retry === "function" ? props.error.retry : null))

function again() {
	const run = retry.value
	emit("dismiss")
	run()
}

watch(
	() => props.error,
	() => (open.value = false),
)
</script>

<template>
	<div v-if="text" class="error-veil" @click.self="emit('dismiss')">
		<div class="card error-card" role="alertdialog" aria-modal="true">
			<span class="error-icon"><AppIcon name="problem" size="lg" /></span>
			<p class="error-text">{{ text }}</p>
			<button v-if="detail" class="error-more" type="button" @click="open = !open">{{ open ? __("Hide details") : __("Details") }}</button>
			<p v-if="detail && open" class="error-detail">{{ detail }}</p>
			<button v-if="retry" class="error-ok" type="button" @click="again">{{ __("Try again") }}</button>
			<button class="error-ok" type="button" @click="emit('dismiss')">{{ __("OK") }}</button>
		</div>
	</div>
</template>

<style>
.error-veil {
	position: fixed;
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
	z-index: 40;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: var(--s4);
	background: rgba(5, 33, 58, 0.45);
}
.error-card {
	display: flex;
	flex-direction: column;
	align-items: center;
	width: 100%;
	max-width: 30rem;
	max-height: 90vh;
	overflow-y: auto;
	padding: var(--s5);
	border: 2px solid var(--problem);
	text-align: center;
}
.error-card > * + * {
	margin-top: var(--s3);
}
.error-icon {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: 3.5rem;
	height: 3.5rem;
	border-radius: 50%;
	background: var(--problem-bg);
	color: var(--problem);
}
.error-text {
	font-size: var(--t-lg);
	font-weight: 800;
}
.error-more {
	border: 0;
	background: none;
	color: var(--ink-2);
	font-weight: 700;
	text-decoration: underline;
}
.error-detail {
	width: 100%;
	padding: var(--s3);
	border-radius: var(--r-md);
	background: var(--surface-2);
	color: var(--ink-2);
	font-size: var(--t-sm);
	text-align: start;
	word-break: break-word;
}
.error-ok {
	width: 100%;
	min-height: var(--button);
	border: 0;
	border-radius: var(--r-md);
	background: var(--primary);
	color: var(--on-primary);
	font-size: var(--t-lg);
	font-weight: 800;
}
</style>
