<script setup>
import { ref } from "vue"
import { api, errorText } from "../api.js"
import BigButton from "../components/BigButton.vue"

const emit = defineEmits(["language"])
const boot = window.frappe.boot
const usr = ref("")
const pwd = ref("")
const error = ref("")
const busy = ref(false)

async function submit() {
	busy.value = true
	error.value = ""
	try {
		if (boot.user !== "Guest") await api.logout()
		await api.login(usr.value, pwd.value)
		window.location.reload()
	} catch (e) {
		error.value = errorText(e)
		busy.value = false
	}
}
</script>

<template>
	<div class="page">
		<form class="screen login" @submit.prevent="submit">
			<img class="logo" src="/assets/fleetix/images/fleetix-logo.svg" alt="Fleetix" />
			<h1 class="screen-title">{{ __("Fleetix Gate") }}</h1>
			<p v-if="boot.user !== 'Guest'" class="banner banner-bad">{{ __("This account cannot use the gate app") }}</p>
			<label class="field">
				<span>{{ __("User") }}</span>
				<input v-model="usr" name="usr" autocomplete="username" dir="ltr" required />
			</label>
			<label class="field">
				<span>{{ __("Password") }}</span>
				<input v-model="pwd" name="pwd" type="password" autocomplete="current-password" dir="ltr" required />
			</label>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<BigButton icon="next" :label="__('Log in')" :busy="busy" @press="submit" />
			<button type="submit" hidden></button>
			<BigButton icon="globe" tone="soft" :label="__('Language')" @press="emit('language')" />
		</form>
	</div>
</template>

<style scoped>
.login {
	max-width: 440px;
	min-height: 100vh;
	min-height: 100dvh;
	justify-content: center;
}
.logo {
	height: 48px;
	align-self: center;
}
.screen-title {
	text-align: center;
}
.field {
	display: flex;
	flex-direction: column;
	gap: 6px;
	font-weight: 600;
}
.field input {
	min-height: 56px;
	border: 1px solid var(--line);
	border-radius: 12px;
	background: var(--surface);
	padding: 0 14px;
	font-size: 18px;
}
</style>
