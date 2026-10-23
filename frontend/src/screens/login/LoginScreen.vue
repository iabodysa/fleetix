<script setup>
import { ref } from "vue"
import { api, errorText } from "../../api.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"

defineEmits(["language"])
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
	<div class="login">
		<form class="card login-card" @submit.prevent="submit">
			<div class="login-top">
				<img class="login-logo" src="/assets/fleetix/images/fleetix-logo.svg" alt="Fleetix" />
				<button class="app-header-button" type="button" :aria-label="__('Language')" @click="$emit('language')">
					<AppIcon name="language" />
				</button>
			</div>
			<h1>{{ __("Fleetix Maintenance") }}</h1>
			<p v-if="boot.user !== 'Guest'" class="screen-error">{{ __("This account cannot use the maintenance app") }}</p>
			<label class="login-field">
				<span class="login-label"><AppIcon name="user" />{{ __("User") }}</span>
				<input v-model="usr" class="login-input" name="usr" autocomplete="username" dir="ltr" required />
			</label>
			<label class="login-field">
				<span class="login-label"><AppIcon name="login" />{{ __("Password") }}</span>
				<input v-model="pwd" class="login-input" name="pwd" type="password" autocomplete="current-password" dir="ltr" required />
			</label>
			<p v-if="error" class="screen-error" role="alert">{{ error }}</p>
			<BigButton icon="login" :label="__('Log in')" :busy="busy" type="submit" block />
		</form>
	</div>
</template>

<style>
.login {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 100%;
	padding: var(--s4) 0;
}
.login-card {
	display: flex;
	flex-direction: column;
	gap: var(--s4);
	width: min(30rem, 100%);
	padding: var(--s5);
}
.login-top {
	display: flex;
	align-items: center;
	justify-content: space-between;
}
.login-logo {
	height: 3rem;
}
.login-field {
	display: flex;
	flex-direction: column;
	gap: var(--s2);
}
.login-label {
	display: inline-flex;
	align-items: center;
	gap: var(--s2);
	font-weight: 700;
}
.login-input {
	min-height: var(--button);
	padding: 0 var(--s4);
	border: 2px solid var(--line);
	border-radius: var(--r-md);
	background: var(--surface-2);
	font-size: var(--t-lg);
}
</style>
