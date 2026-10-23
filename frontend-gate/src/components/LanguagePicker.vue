<script setup>
import { LANGUAGES, currentLanguage } from "../i18n.js"

defineEmits(["pick"])
const now = currentLanguage()
</script>

<template>
	<div class="langs">
		<button
			v-for="language in LANGUAGES"
			:key="language.code"
			type="button"
			class="lang"
			:class="{ on: language.code === now }"
			:lang="language.code"
			:dir="language.code === 'ar' || language.code === 'ur' ? 'rtl' : 'ltr'"
			@click="$emit('pick', language.code)"
		>
			{{ language.name }}
		</button>
	</div>
</template>

<style scoped>
.langs {
	display: grid;
	gap: 10px;
}
.lang {
	min-height: 64px;
	border: 1px solid var(--line);
	border-radius: var(--radius);
	background: var(--surface);
	font-size: 22px;
	font-weight: 700;
}
.on {
	border: 3px solid var(--accent);
}
</style>
