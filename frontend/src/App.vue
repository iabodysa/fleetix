<template>
	<div class="app">
		<LoginScreen v-if="!boot.is_worker" />
		<template v-else>
			<header class="head">
				<div class="head-start">
					<PlateChip v-if="store.visit" :plate="store.visit.plate" size="sm" />
					<img v-else class="brand" src="/assets/fleetix/images/fleetix-logo.svg" alt="" />
				</div>
				<ol class="progress">
					<li
						v-for="(label, index) in stepLabels"
						:key="label"
						:class="{ done: index < stepIndex, current: index === stepIndex }"
					>
						<span class="progress-bar"></span>
						<span class="progress-label">{{ label }}</span>
					</li>
				</ol>
				<div class="head-end">
					<span class="dot" :class="online ? 'dot-ok' : 'dot-bad'" :title="online ? __('Online') : __('Offline')"></span>
					<span v-if="printerReady" class="dot dot-ok" :title="__('Printer')"></span>
					<button v-if="store.step !== 'queue'" class="btn btn-soft btn-head" type="button" @click="openDrawer">
						{{ __("Vehicles") }} <b>{{ queue.data.length }}</b>
					</button>
					<button v-if="store.step !== 'queue'" class="btn btn-soft btn-head" type="button" @click="backToQueue">
						{{ __("Close") }}
					</button>
					<button v-else class="btn btn-soft btn-head" type="button" @click="menu = !menu">{{ boot.full_name }}</button>
					<div v-if="menu" class="menu">
						<button v-if="shell" type="button" @click="openSettings">{{ __("Settings") }}</button>
						<button type="button" @click="logout">{{ __("Log out") }}</button>
					</div>
				</div>
			</header>
			<main class="body">
				<QueueScreen v-if="store.step === 'queue'" />
				<OdometerScreen v-else-if="store.step === 'odometer'" />
				<ComponentsScreen v-else-if="store.step === 'components'" />
				<PhotosScreen v-else-if="store.step === 'photos'" />
				<AwaitScreen v-else-if="store.step === 'await'" />
				<ReviewScreen v-else-if="store.step === 'review'" />
				<DoneScreen v-else-if="store.step === 'done'" />
			</main>
			<div v-if="store.drawer" class="drawer-veil" @click="store.drawer = false"></div>
			<aside class="drawer" :class="{ open: store.drawer }">
				<div class="drawer-head">
					<h2>{{ __("Vehicles") }}</h2>
					<button class="btn btn-soft" type="button" @click="store.drawer = false">{{ __("Close") }}</button>
				</div>
				<QueueList compact />
			</aside>
		</template>
	</div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { __ } from "./translate.js"
import { api } from "./api.js"
import { hasPrinter, hasShell, onShellBack, openSettings, showStepOnCustomerDisplay } from "./native.js"
import { STEPS, backToQueue, queue, stepBack, store } from "./store.js"
import PlateChip from "./components/PlateChip.vue"
import QueueList from "./components/QueueList.vue"
import LoginScreen from "./screens/LoginScreen.vue"
import QueueScreen from "./screens/QueueScreen.vue"
import OdometerScreen from "./screens/OdometerScreen.vue"
import ComponentsScreen from "./screens/ComponentsScreen.vue"
import PhotosScreen from "./screens/PhotosScreen.vue"
import AwaitScreen from "./screens/AwaitScreen.vue"
import ReviewScreen from "./screens/ReviewScreen.vue"
import DoneScreen from "./screens/DoneScreen.vue"

const boot = window.frappe.boot
const menu = ref(false)
const online = ref(navigator.onLine)
const printerReady = hasPrinter()
const shell = hasShell()
const stepLabels = [__("Vehicle"), __("Odometer"), __("Items and parts"), __("Photos"), __("Approval"), __("Review")]
const stepIndex = computed(() => (store.step === "done" ? STEPS.length : STEPS.indexOf(store.step)))

function shellBack() {
	if (menu.value) {
		menu.value = false
		return true
	}
	return stepBack()
}
watch(
	() => [store.step, store.visit && store.visit.plate],
	([step, plate]) => {
		if (step === "done") return
		showStepOnCustomerDisplay(step === "queue" ? "" : plate, stepLabels[STEPS.indexOf(step)])
	},
)
onShellBack(shellBack)

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
onMounted(() => {
	window.addEventListener("online", setOnline)
	window.addEventListener("offline", setOnline)
	if (boot.is_worker) queue.fetch()
})
onBeforeUnmount(() => {
	window.removeEventListener("online", setOnline)
	window.removeEventListener("offline", setOnline)
})
</script>
