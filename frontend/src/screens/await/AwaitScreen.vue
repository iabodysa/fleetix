<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { formatKm, statusLabel } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { backToQueue, openVisit, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const POLL_MS = 15000
const status = ref(store.visit.status)
const error = ref("")
const busy = ref(false)
let timer = null

async function check() {
	busy.value = true
	try {
		const value = await api.status(store.visit.maintenance)
		status.value = value.status
		if (value.status !== "Full Inspection") await openVisit(Object.assign({}, store.visit, value))
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
onMounted(() => {
	timer = setInterval(check, POLL_MS)
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
	<ScreenFrame :title="__('Sent for approval')" v-model:error="error">
		<div class="await">
			<span class="await-mark tone-wait"><AppIcon name="waiting" size="xl" /></span>
			<p class="await-lead">{{ __("Waiting for the rental manager to approve") }}</p>
			<dl class="facts">
				<div>
					<dt>{{ __("Odometer") }}</dt>
					<dd>{{ formatKm(store.visit.odometer || store.odometer) }}</dd>
				</div>
				<div>
					<dt>{{ __("Status") }}</dt>
					<dd><span class="pill tone-wait">{{ statusLabel(status) }}</span></dd>
				</div>
			</dl>
		</div>
		<template #back>
			<BigButton icon="vehicle" tone="quiet" :label="__('Other vehicle')" @press="backToQueue" />
		</template>
		<template #primary>
			<BigButton icon="refresh" :label="__('Check now')" :busy="busy" @press="check" />
		</template>
	</ScreenFrame>
</template>

<style>
.await {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: var(--s4);
	padding: var(--s6) 0;
	text-align: center;
}
.await-mark {
	display: inline-flex;
	padding: var(--s5);
	border-radius: 50%;
}
.await-lead {
	font-size: var(--t-lg);
	font-weight: 700;
}
</style>
