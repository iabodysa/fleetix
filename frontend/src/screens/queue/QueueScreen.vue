<script setup>
import { ref } from "vue"
import { api, errorText } from "../../api.js"
import { problem, success } from "../../composables/useFeedback.js"
import { scanKey } from "../../composables/useBarcode.js"
import { openVisit, queue, stepForStatus } from "../../store/index.js"
import BarcodeInput from "../../components/BarcodeInput.vue"
import BigButton from "../../components/BigButton.vue"
import PlateKeypad from "../../components/PlateKeypad.vue"
import QueueList from "../../components/QueueList.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import VehicleResults from "../../components/VehicleResults.vue"

const filter = ref("")
const error = ref("")

async function scanned(key) {
	const row = (queue.data || []).find((r) => [r.plate, r.vehicle, r.maintenance].some((value) => scanKey(value) === key))
	error.value = ""
	try {
		const visit = row && stepForStatus(row) ? row : await api.openScanned(key)
		success()
		await openVisit(visit)
	} catch (e) {
		error.value = errorText(e)
		problem()
	}
}
</script>

<template>
	<ScreenFrame :title="filter ? __('Vehicles') : __('Vehicles due')" v-model:error="error">
		<template #meta>
			<BigButton icon="refresh" tone="quiet" :label="__('Refresh')" :busy="queue.loading" @press="queue.fetch()" />
		</template>
		<VehicleResults v-if="filter" :filter="filter" />
		<template v-else>
			<QueueList />
			<h2 class="queue-heading">{{ __("All vehicles") }}</h2>
			<VehicleResults filter="" />
		</template>
		<template #aside>
			<div class="queue-find">
				<BarcodeInput @scan="scanned" />
				<PlateKeypad v-model="filter" />
			</div>
		</template>
	</ScreenFrame>
</template>

<style>
.queue-heading {
	margin: var(--s5) 0 var(--s3);
	font-size: var(--t-lg);
	font-weight: 800;
}
.queue-find {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
}
</style>
