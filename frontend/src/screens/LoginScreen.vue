<template>
	<div class="login">
		<form class="card login-card" @submit.prevent="submit">
			<img class="login-logo" src="/assets/fleetix/images/fleetix-logo.svg" alt="" />
			<h1>{{ __("Fleetix Maintenance") }}</h1>
			<p v-if="boot.user !== 'Guest'" class="error">{{ __("This account cannot use the maintenance app") }}</p>
			<label class="field">
				<span class="label">{{ __("User") }}</span>
				<input v-model="usr" class="input" name="usr" autocomplete="username" dir="ltr" required />
			</label>
			<label class="field">
				<span class="label">{{ __("Password") }}</span>
				<input v-model="pwd" class="input" name="pwd" type="password" autocomplete="current-password" dir="ltr" required />
			</label>
			<p v-if="error" class="error">{{ error }}</p>
			<button class="btn btn-primary btn-block" type="submit" :disabled="busy">{{ __("Log in") }}</button>
		</form>
	</div>
</template>

<script setup>
import { ref } from "vue"
import { api, errorText } from "../api.js"

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
