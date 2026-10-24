<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { __ } from "../i18n/index.js"
import { scrollByPage } from "../composables/useCardProgress.js"
import AppIcon from "./AppIcon.vue"

const CHECK_MS = 700
const SLACK = 24
const below = ref(false)
let timer = null

function check() {
	const scroller = document.scrollingElement || document.documentElement
	below.value = scroller.scrollTop + window.innerHeight < scroller.scrollHeight - SLACK
}
onMounted(() => {
	check()
	window.addEventListener("scroll", check, { passive: true })
	window.addEventListener("resize", check)
	timer = window.setInterval(check, CHECK_MS)
})
onBeforeUnmount(() => {
	window.removeEventListener("scroll", check)
	window.removeEventListener("resize", check)
	window.clearInterval(timer)
})
</script>

<template>
	<div v-if="below" class="more-below">
		<button type="button" class="more-below-arrow" :aria-label="__('More below')" @click="scrollByPage"><AppIcon name="down" size="lg" /></button>
	</div>
</template>

<style>
.more-below {
	position: absolute;
	right: 0;
	bottom: 100%;
	left: 0;
	display: flex;
	justify-content: center;
	align-items: flex-end;
	height: 4rem;
	background: linear-gradient(transparent, var(--bg));
	pointer-events: none;
}
.more-below-arrow {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: 3rem;
	height: 3rem;
	margin-bottom: var(--s1);
	border: 2px solid var(--line);
	border-radius: 999px;
	background: var(--surface);
	color: var(--ink);
	pointer-events: auto;
}
</style>
