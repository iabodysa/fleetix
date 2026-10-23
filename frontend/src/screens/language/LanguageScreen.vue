<script setup>
import AppIcon from "../../components/AppIcon.vue"
import { useLanguage } from "../../composables/useLanguage.js"

defineProps({ canClose: Boolean })
defineEmits(["close"])
const { languages, current, choose } = useLanguage()
</script>

<template>
	<section class="language-screen">
		<header class="language-head">
			<span class="language-globe"><AppIcon name="language" size="xl" /></span>
			<button v-if="canClose" class="app-header-button" type="button" :aria-label="__('Close')" @click="$emit('close')">
				<AppIcon name="close" />
			</button>
		</header>
		<div class="language-grid">
			<button
				v-for="language in languages"
				:key="language.code"
				class="language-tile"
				:class="{ pressed: language.code === current.code }"
				type="button"
				:lang="language.code"
				:dir="language.dir"
				:aria-pressed="language.code === current.code ? 'true' : 'false'"
				@click="choose(language.code)"
			>
				<span class="language-name">{{ language.name }}</span>
				<span class="language-code ltr">{{ language.code.toUpperCase() }}</span>
			</button>
		</div>
	</section>
</template>

<style>
.language-screen {
	display: flex;
	flex-direction: column;
	gap: var(--s5);
	width: 100%;
	max-width: 56rem;
	margin: 0 auto;
	padding: var(--s5) 0;
}
.language-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
}
.language-globe {
	display: inline-flex;
	padding: var(--s3);
	border-radius: var(--r-lg);
	background: var(--primary);
	color: var(--on-primary);
}
.language-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
	gap: var(--s3);
}
.language-tile {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: var(--s3);
	min-height: 5.5rem;
	padding: 0 var(--s5);
	border: 2px solid var(--line);
	border-radius: var(--r-lg);
	background: var(--surface);
	box-shadow: var(--shadow);
	text-align: start;
}
.language-tile.pressed {
	border-color: var(--primary);
	box-shadow: inset 0 0 0 2px var(--primary);
}
.language-name {
	font-size: var(--t-xl);
	font-weight: 800;
}
.language-code {
	color: var(--ink-2);
	font-weight: 700;
}
</style>
