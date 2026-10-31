<script setup>
import { computed, onMounted, ref } from "vue"
import { api } from "./api.js"
import { __, chooseLanguage, storedLanguage } from "./i18n.js"
import { hasShell, onShellBack, openSettings } from "./native.js"
import { reloadOnNewVersion } from "../../frontend/src/freshness.js"
import { STEPS, restoreDraft, stepBack, store } from "./store.js"
import { desk, openStore, storeBack } from "./storekeeper.js"
import BigButton from "./components/BigButton.vue"
import GateIcon from "./components/GateIcon.vue"
import LanguagePicker from "./components/LanguagePicker.vue"
import PlateChip from "./components/PlateChip.vue"
import StepBar from "./components/StepBar.vue"
import DoneScreen from "./screens/DoneScreen.vue"
import LanguageScreen from "./screens/LanguageScreen.vue"
import LoginScreen from "./screens/LoginScreen.vue"
import OdometerScreen from "./screens/OdometerScreen.vue"
import PhotosScreen from "./screens/PhotosScreen.vue"
import PlateScreen from "./screens/PlateScreen.vue"
import RouteScreen from "./screens/RouteScreen.vue"
import ApprovalScreen from "./screens/store/ApprovalScreen.vue"
import ApprovalsScreen from "./screens/store/ApprovalsScreen.vue"
import HubScreen from "./screens/store/HubScreen.vue"
import MatchScreen from "./screens/store/MatchScreen.vue"
import NewPartScreen from "./screens/store/NewPartScreen.vue"
import PartsScreen from "./screens/store/PartsScreen.vue"
import ReceiveScreen from "./screens/store/ReceiveScreen.vue"

const SCREENS = { plate: PlateScreen, odometer: OdometerScreen, photos: PhotosScreen, route: RouteScreen, done: DoneScreen }
const STORE_SCREENS = {
	hub: HubScreen,
	approvals: ApprovalsScreen,
	approval: ApprovalScreen,
	parts: PartsScreen,
	receive: ReceiveScreen,
	match: MatchScreen,
	newPart: NewPartScreen,
}
const boot = window.frappe.boot
const shell = hasShell()
const sheet = ref(null)
const firstRun = !storedLanguage()
const stepLabels = [__("Car"), __("Odometer"), __("Photos"), __("Next stop")]
const stepIndex = computed(() => (store.step === "done" ? STEPS.length : STEPS.indexOf(store.step)))
const transition = computed(() => (store.forward ? "slide-fwd" : "slide-back"))
const screen = computed(() => (desk.view ? STORE_SCREENS[desk.view] : SCREENS[store.step]))
const canBack = computed(() => (desk.view ? desk.view !== "hub" || boot.is_worker : store.step !== "plate" && store.step !== "done"))
const storeEntry = computed(() => boot.is_store && boot.is_worker && !desk.view && store.step === "plate")

async function pickLanguage(code) {
	if (boot.user !== "Guest") await api.setLanguage(code).catch(() => null)
	chooseLanguage(code)
}
async function logout() {
	await api.logout().catch(() => null)
	window.location.reload()
}
function shellBack() {
	if (sheet.value) {
		sheet.value = null
		return true
	}
	return desk.view ? storeBack() : stepBack()
}
function back() {
	if (desk.view) storeBack()
	else stepBack()
}
onShellBack(shellBack)
onMounted(() => {
	if (boot.is_worker) restoreDraft()
	else openStore("hub")
	reloadOnNewVersion(() => (desk.view ? desk.view === "hub" : store.step === "plate" && !store.vehicle))
})
</script>

<template>
	<LanguageScreen v-if="firstRun" />
	<LoginScreen v-else-if="!boot.is_worker && !boot.is_store" @language="sheet = 'language'" />
	<div v-else class="app">
		<header class="head">
			<button v-if="canBack" type="button" class="icon-btn" :aria-label="__('Back')" @click="back">
				<GateIcon name="back" flip />
			</button>
			<PlateChip v-if="!desk.view && store.vehicle && store.step !== 'plate'" :plate="store.vehicle.plate" size="sm" />
			<img v-else class="brand" src="/assets/fleetix/images/fleetix-logo.svg" alt="Fleetix" />
			<span class="grow"></span>
			<button v-if="storeEntry" type="button" class="icon-btn" @click="openStore('hub')">
				<GateIcon name="box" />
				<span class="who">{{ __("Store") }}</span>
			</button>
			<button type="button" class="icon-btn" :aria-label="__('Menu')" @click="sheet = 'menu'">
				<span class="who">{{ boot.full_name }}</span>
			</button>
		</header>
		<StepBar v-if="!desk.view && store.step !== 'done'" :steps="stepLabels" :current="stepIndex" />
		<main class="body">
			<Transition :name="transition" mode="out-in">
				<component :is="screen" :key="desk.view || store.step" />
			</Transition>
		</main>
	</div>
	<div v-if="sheet" class="veil" @click.self="sheet = null">
		<div class="sheet" role="dialog">
			<LanguagePicker v-if="sheet === 'language'" @pick="pickLanguage" />
			<template v-else>
				<BigButton icon="globe" tone="soft" :label="__('Language')" @press="sheet = 'language'" />
				<BigButton v-if="shell" icon="wrench" tone="soft" :label="__('Settings')" @press="openSettings" />
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
