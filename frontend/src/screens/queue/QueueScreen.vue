<script setup>
import { ref } from "vue"
import { __ } from "../../i18n/index.js"
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

function scanned(key) {
	const row = (queue.data || []).find((r) => [r.plate, r.vehicle, r.maintenance].some((value) => scanKey(value) === key))
	if (row && stepForStatus(row)) {
		error.value = ""
		success()
		openVisit(row)
		return
	}
	error.value = __("No open visit for this vehicle")
	problem()
}
</script>

<template>
	<ScreenFrame :title="filter ? __('Vehicles') : __('Vehicles due')" v-model:error="error">
		<template #meta>
			<BigButton icon="refresh" tone="quiet" :label="__('Refresh')" :busy="queue.loading" @press="queue.fetch()" />
		</template>
		<VehicleResults v-if="filter" :filter="filter" />
		<QueueList v-else />
		<template #aside>
			<div class="queue-find">
				<BarcodeInput @scan="scanned" />
				<PlateKeypad v-model="filter" />
			</div>
		</template>
	</ScreenFrame>
</template>

<style>
.queue-find {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
}
</style>
