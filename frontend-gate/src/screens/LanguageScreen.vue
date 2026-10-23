<script setup>
import { chooseLanguage } from "../i18n.js"
import LanguagePicker from "../components/LanguagePicker.vue"
</script>

<template>
	<div class="page">
		<div class="screen center">
			<img class="logo" src="/assets/fleetix/images/fleetix-logo.svg" alt="Fleetix" />
			<LanguagePicker @pick="chooseLanguage" />
		</div>
	</div>
</template>

<style scoped>
.center {
	justify-content: center;
	min-height: 100dvh;
	max-width: 440px;
}
.logo {
	height: 56px;
	margin: 0 auto 8px;
}
</style>
