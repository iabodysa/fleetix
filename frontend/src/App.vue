<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { __ } from "./i18n/index.js"
import { api } from "./api.js"
import { hasPrinter, hasShell, onShellBack, openSettings } from "./native.js"
import { useLanguage } from "./composables/useLanguage.js"
import { publishToCustomer } from "./composables/useCustomerDisplay.js"
import { STEPS, backToQueue, queue, restoreDraft, stepBack, store } from "./store/index.js"
import AppHeader from "./components/AppHeader.vue"
import AppIcon from "./components/AppIcon.vue"
import PrintTest from "./components/PrintTest.vue"
import QueueList from "./components/QueueList.vue"
import StepBar from "./components/StepBar.vue"
import UndoToast from "./components/UndoToast.vue"
import AwaitScreen from "./screens/await/AwaitScreen.vue"
import CustomerScreen from "./screens/customer/CustomerScreen.vue"
import DamageScreen from "./screens/damage/DamageScreen.vue"
import DoneScreen from "./screens/done/DoneScreen.vue"
import LanguageScreen from "./screens/language/LanguageScreen.vue"
import LoginScreen from "./screens/login/LoginScreen.vue"
import OdometerScreen from "./screens/odometer/OdometerScreen.vue"
import PartsScreen from "./screens/parts/PartsScreen.vue"
import PhotosScreen from "./screens/photos/PhotosScreen.vue"
import QueueScreen from "./screens/queue/QueueScreen.vue"
import ReviewScreen from "./screens/review/ReviewScreen.vue"
import SignaturesScreen from "./screens/signatures/SignaturesScreen.vue"

const SCREENS = {
	queue: QueueScreen,
	odometer: OdometerScreen,
	parts: PartsScreen,
	damage: DamageScreen,
	photos: PhotosScreen,
	signatures: SignaturesScreen,
	await: AwaitScreen,
	review: ReviewScreen,
	done: DoneScreen,
}
const STEP_LABELS = [__("Vehicle"), __("Odometer"), __("Parts"), __("Damage"), __("Photos"), __("Signatures"), __("Approval"), __("Review")]

const boot = window.frappe.boot
const customerView = new URLSearchParams(window.location.search).get("view") === "customer"
const language = useLanguage()
language.applyDocument()
const redirecting = !customerView && language.followDevice()
const picking = ref(!customerView && !language.chosen())
const menu = ref(false)
const printTest = ref(false)
const online = ref(navigator.onLine)
const printer = hasPrinter()
const shell = hasShell()
const stepIndex = computed(() => (store.step === "done" ? STEPS.length - 1 : STEPS.indexOf(store.step)))
const inVisit = computed(() => store.step !== "queue")

function shellBack() {
	if (picking.value && language.chosen()) {
		picking.value = false
		return true
	}
	if (menu.value) {
		menu.value = false
		return true
	}
	return stepBack()
}
function setOnline() {
	online.value = navigator.onLine
}
function openDrawer() {
	queue.fetch()
	store.drawer = true
}
async function logout() {
	await api.logout()
	window.location.reload()
}

watch(
	() => [store.step, store.visit && store.visit.plate],
	([step, plate]) => {
		if (step === "done") return publishToCustomer({ plate, status: __("Completed"), tone: "done" })
		const status = step === "photos" || step === "signatures" ? __("Photos and signatures") : STEP_LABELS[STEPS.indexOf(step)]
		publishToCustomer({ plate: step === "queue" ? "" : plate, status, tone: step === "await" ? "wait" : "quiet" })
	},
)
onShellBack(shellBack)
onMounted(() => {
	window.addEventListener("online", setOnline)
	window.addEventListener("offline", setOnline)
	if (boot.is_worker && !redirecting) restoreDraft()
})
watch(
	() => boot.is_worker,
	(isWorker) => {
		if (isWorker) restoreDraft()
	},
)
onBeforeUnmount(() => {
	window.removeEventListener("online", setOnline)
	window.removeEventListener("offline", setOnline)
})
</script>

<template>
	<CustomerScreen v-if="customerView" />
	<div v-else class="app">
		<LanguageScreen v-if="picking" :can-close="!!language.chosen()" @close="picking = false" />
		<LoginScreen v-else-if="!boot.is_worker" @language="picking = true" />
		<template v-else>
			<AppHeader
				:plate="store.visit ? store.visit.plate : ''"
				:vehicles="queue.data.length"
				:in-visit="inVisit"
				:online="online"
				:printer="printer"
				:language="language.current.name"
				:user="boot.full_name"
				@vehicles="openDrawer"
				@close="backToQueue"
				@language="picking = true"
				@menu="menu = !menu"
			/>
			<div v-if="menu" class="card app-menu">
				<p class="app-menu-name">{{ boot.full_name }}</p>
				<button class="app-header-button" type="button" @click="(printTest = true), (menu = false)">{{ __("Print test") }}</button>
				<button v-if="shell" class="app-header-button" type="button" @click="openSettings">{{ __("Settings") }}</button>
				<button class="app-header-button" type="button" @click="logout">{{ __("Log out") }}</button>
			</div>
			<PrintTest v-if="printTest" @close="printTest = false" />
			<StepBar v-if="inVisit" :steps="STEP_LABELS" :current="stepIndex" />
			<main class="app-body">
				<Transition :name="'slide-' + store.flow" mode="out-in">
					<component :is="SCREENS[store.step]" :key="store.step" />
				</Transition>
			</main>
			<div v-if="store.drawer" class="drawer-veil" @click="store.drawer = false"></div>
			<aside class="drawer" :class="{ open: store.drawer }">
				<div class="drawer-head">
					<h2>{{ __("Vehicles") }}</h2>
					<button class="app-header-button" type="button" :aria-label="__('Close')" @click="store.drawer = false"><AppIcon name="close" /></button>
				</div>
				<QueueList compact />
			</aside>
		</template>
		<UndoToast />
	</div>
</template>

<style>
.app {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
	min-height: 100%;
	max-width: 90rem;
	margin: 0 auto;
	padding: var(--s3) var(--s4) 0;
}
.app-body {
	flex: 1;
	min-height: 0;
}
.app-menu {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: var(--s2);
	padding: var(--s3);
}
.app-menu-name {
	flex: 1;
	font-weight: 800;
}
.drawer-veil {
	position: fixed;
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
	z-index: 20;
	background: rgba(5, 33, 58, 0.45);
}
.drawer {
	position: fixed;
	top: 0;
	bottom: 0;
	right: 0;
	z-index: 21;
	width: 26rem;
	max-width: 92vw;
	padding: var(--s4);
	overflow-y: auto;
	background: var(--bg);
	transform: translateX(calc(var(--flow) * 105%));
	visibility: hidden;
	transition: transform var(--slide) var(--ease), visibility var(--slide);
}
html[dir="rtl"] .drawer {
	right: auto;
	left: 0;
}
.drawer.open {
	transform: none;
	visibility: visible;
}
.drawer-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: var(--s3);
}
</style>
