<template>
	<div class="login">
		<form class="card login-card" @submit.prevent="submit">
			<img class="login-logo" src="/assets/fleetix/images/fleetix-logo.svg" alt="" />
			<h1>{{ __("Fleetix Maintenance") }}</h1>
			<p v-if="boot.user !== 'Guest'" class="error">{{ __("This account cannot use the maintenance app") }}</p>
			<label class="field">
				<span class="label">{{ __("User") }}</span>
				<input
					v-model="usr"
					class="input"
					name="usr"
					type="text"
					inputmode="email"
					autocomplete="username"
					autocapitalize="off"
					autocorrect="off"
					spellcheck="false"
					dir="ltr"
					required
				/>
			</label>
			<label class="field">
				<span class="label">{{ __("Password") }}</span>
				<input
					ref="pwdInput"
					v-model="pwd"
					class="input"
					name="pwd"
					type="password"
					autocomplete="current-password"
					dir="ltr"
					required
				/>
			</label>
			<p v-if="error" class="error">{{ error }}</p>
			<button class="btn btn-primary btn-block" type="submit" :disabled="busy">{{ __("Log in") }}</button>
		</form>
	</div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { api, errorText } from "../api.js"
import { __ } from "../translate.js"

const boot = window.frappe.boot
const USER_KEY = "fleetix_maintenance_user"
const usr = ref(readUser())
const pwdInput = ref(null)
const pwd = ref("")
const error = ref("")
const busy = ref(false)

async function submit() {
	busy.value = true
	error.value = ""
	try {
		if (boot.user !== "Guest") await api.logout()
		await api.login(usr.value, pwd.value)
		saveUser(usr.value)
		const session = await api.boot().catch(() => null)
		if (!session || session.boot.user === "Guest") {
			error.value = __("This device did not keep the sign-in. Update Android System WebView and try again.")
			busy.value = false
			return
		}
		window.csrf_token = session.csrf_token
		Object.assign(boot, session.boot)
		busy.value = false
	} catch (e) {
		error.value = errorText(e)
		busy.value = false
	}
}

function readUser() {
	try {
		return window.localStorage.getItem(USER_KEY) || ""
	} catch (e) {
		return ""
	}
}

function saveUser(value) {
	try {
		window.localStorage.setItem(USER_KEY, value)
	} catch (e) {}
}

onMounted(() => {
	if (usr.value && pwdInput.value) pwdInput.value.focus()
})
</script>
