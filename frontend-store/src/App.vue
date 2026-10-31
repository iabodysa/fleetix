<script setup>
import { ref } from "vue"
import { api } from "./api.js"
import { __, chooseLanguage, storedLanguage } from "./i18n.js"
import { reloadOnNewVersion } from "../../frontend/src/freshness.js"
import { go, store, stepBack } from "./store.js"
import AppIcon from "./components/AppIcon.vue"
import BigButton from "./components/BigButton.vue"
import LanguagePicker from "./components/LanguagePicker.vue"
import LanguageScreen from "./screens/LanguageScreen.vue"
import LoginScreen from "./screens/LoginScreen.vue"
import MatchScreen from "./screens/MatchScreen.vue"
import NewPartScreen from "./screens/NewPartScreen.vue"
import PendingDetailScreen from "./screens/PendingDetailScreen.vue"
import PendingScreen from "./screens/PendingScreen.vue"
import ReceiveScreen from "./screens/ReceiveScreen.vue"

const SCREENS = { pending: PendingScreen, detail: PendingDetailScreen, receive: ReceiveScreen, match: MatchScreen, newpart: NewPartScreen }
const TABS = [
	{ step: "pending", label: __("Pending issues"), steps: ["pending", "detail"] },
	{ step: "receive", label: __("Receive stock"), steps: ["receive", "match", "newpart"] },
]
const boot = window.frappe.boot
const sheet = ref(null)
const firstRun = !storedLanguage()

async function pickLanguage(code) {
	if (boot.user !== "Guest") await api.setLanguage(code).catch(() => null)
	chooseLanguage(code)
}
async function logout() {
	await api.logout().catch(() => null)
	window.location.reload()
}
reloadOnNewVersion(() => store.step === "pending" && !store.receipt.item)
</script>

<template>
	<LanguageScreen v-if="firstRun" />
	<LoginScreen v-else-if="!boot.is_store" @language="sheet = 'language'" />
	<div v-else class="app">
		<header class="head">
			<button v-if="store.step === 'detail' || store.step === 'match' || store.step === 'newpart'" type="button" class="icon-btn" :aria-label="__('Back')" @click="stepBack">
				<AppIcon name="back" flip />
			</button>
			<img v-else class="brand" src="/assets/fleetix/images/fleetix-logo.svg" alt="Fleetix" />
			<span class="grow"></span>
			<button type="button" class="icon-btn" :aria-label="__('Menu')" @click="sheet = 'menu'">
				<span class="who">{{ boot.full_name }}</span>
			</button>
		</header>
		<nav class="tabs">
			<button v-for="tab in TABS" :key="tab.step" type="button" class="tab" :class="{ on: tab.steps.indexOf(store.step) !== -1 }" @click="go(tab.step)">
				{{ tab.label }}
			</button>
		</nav>
		<main class="body">
			<Transition :name="store.forward ? 'slide-fwd' : 'slide-back'" mode="out-in">
				<component :is="SCREENS[store.step]" :key="store.step" />
			</Transition>
		</main>
	</div>
	<div v-if="sheet" class="veil" @click.self="sheet = null">
		<div class="sheet" role="dialog">
			<LanguagePicker v-if="sheet === 'language'" @pick="pickLanguage" />
			<template v-else>
				<BigButton icon="globe" tone="soft" :label="__('Language')" @press="sheet = 'language'" />
				<BigButton icon="back" tone="soft" :label="__('Log out')" @press="logout" />
			</template>
			<BigButton icon="back" tone="soft" :label="__('Close')" @press="sheet = null" />
		</div>
	</div>
</template>

<style>
#app {
	min-height: 100vh;
	min-height: 100dvh;
	display: flex;
	flex-direction: column;
}
.app {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 10px;
	min-height: 100vh;
	min-height: 100dvh;
}
.head {
	display: flex;
	align-items: center;
	gap: 10px;
	padding: 10px 16px;
	padding-top: calc(10px + env(safe-area-inset-top));
	max-width: 720px;
	width: 100%;
	margin: 0 auto;
}
.brand {
	height: 32px;
}
.grow {
	flex: 1;
}
.icon-btn {
	min-height: 48px;
	min-width: 48px;
	border: 1px solid var(--line);
	border-radius: 12px;
	background: var(--surface);
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0 12px;
}
.who {
	max-width: 160px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	font-weight: 600;
}
.tabs {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 8px;
	padding: 0 16px;
	max-width: 720px;
	width: 100%;
	margin: 0 auto;
}
.tab {
	min-height: 52px;
	border: 1px solid var(--line);
	border-radius: 12px;
	background: var(--surface);
	font-weight: 700;
}
.tab.on {
	border: 3px solid var(--accent);
}
.body {
	flex: 1;
	display: flex;
	flex-direction: column;
	overflow-x: hidden;
}
.page {
	flex: 1;
	display: flex;
	flex-direction: column;
}
.veil {
	position: fixed;
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
	z-index: 20;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: flex-end;
	justify-content: center;
}
.sheet {
	width: 100%;
	max-width: 560px;
	background: var(--bg);
	border-radius: 20px 20px 0 0;
	padding: 16px 16px calc(16px + env(safe-area-inset-bottom));
	display: grid;
	gap: 10px;
}
</style>
