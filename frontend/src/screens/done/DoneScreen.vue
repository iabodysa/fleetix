<script setup>
import { onMounted, ref } from "vue"
import { __, componentLabel, statusLabel } from "../../i18n/index.js"
import { errorText } from "../../api.js"
import { dueText, hasPrinter, printDocument, printReceipt, receiptCanvas, showOnCustomerDisplay } from "../../native.js"
import { backToQueue, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import SuccessCheck from "../../components/SuccessCheck.vue"

const result = store.result
const receipt = receiptCanvas(result).toDataURL("image/png")
const error = ref("")
const busy = ref(false)
const TONE = { overdue: "problem", soon: "wait", ok: "done" }
const STATE_TEXT = { overdue: __("Overdue"), soon: __("Due soon"), ok: __("Good") }

async function print() {
	busy.value = true
	try {
		store.printed = await printReceipt(result)
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
async function printForm(format) {
	busy.value = true
	try {
		await printDocument("Maintenance", result.maintenance, format)
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
onMounted(async () => {
	try {
		store.display = await showOnCustomerDisplay(result.plate, statusLabel(result.status), result.next_due)
	} catch (e) {
		error.value = errorText(e)
	}
	if (!store.printed) await print()
})
</script>

<template>
	<ScreenFrame :title="__('Next service')" :error="error">
		<template #meta>
			<span class="muted ltr">{{ result.maintenance }}</span>
		</template>
		<SuccessCheck :label="__('Maintenance completed')" />
		<div class="done">
			<div class="done-due">
				<div v-for="row in result.next_due" :key="row.component" class="card done-row">
					<AppIcon :name="row.component" size="lg" />
					<span class="done-name">{{ componentLabel(row.component) }}</span>
					<span class="done-when">{{ dueText(row) }}</span>
					<span v-if="row.replaced" class="pill tone-done">{{ __("Replaced today") }}</span>
					<span v-else class="pill" :class="'tone-' + TONE[row.state]">{{ STATE_TEXT[row.state] }}</span>
				</div>
				<div class="done-devices">
					<span class="pill" :class="store.printed ? 'tone-done' : 'tone-quiet'"><AppIcon name="printer" />{{ store.printed ? __("Receipt printed") : __("Printer not connected") }}</span>
					<span class="pill" :class="store.display ? 'tone-done' : 'tone-quiet'"><AppIcon name="screen" />{{ store.display ? __("On customer screen") : __("Customer screen not connected") }}</span>
				</div>
				<div v-if="hasPrinter()" class="done-devices">
					<BigButton icon="printer" tone="quiet" :label="__('Maintenance Invoice')" :busy="busy" @press="printForm('Thermal Maintenance Invoice')" />
					<BigButton icon="printer" tone="quiet" :label="__('Gate Exit Pass')" :busy="busy" @press="printForm('Thermal Gate Exit Pass')" />
				</div>
			</div>
			<img class="done-receipt" :src="receipt" alt="" />
		</div>
		<template #back>
			<BigButton icon="printer" tone="quiet" :label="__('Print again')" :busy="busy" @press="print" />
		</template>
		<template #primary>
			<BigButton icon="next" :label="__('Next vehicle')" @press="backToQueue" />
		</template>
	</ScreenFrame>
</template>

<style>
.done {
	display: grid;
	grid-template-columns: minmax(0, 1fr) minmax(12rem, 18rem);
	gap: var(--s5);
	align-items: start;
	margin-top: var(--s5);
}
.done-due {
	display: grid;
	gap: var(--s2);
	min-width: 0;
}
.done-row {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: var(--s3);
	padding: var(--s3) var(--s4);
}
.done-name {
	flex: 1;
	font-weight: 800;
}
.done-when {
	font-weight: 700;
}
.done-devices {
	display: flex;
	flex-wrap: wrap;
	gap: var(--s2);
}
.done-receipt {
	width: 100%;
	border: 1px solid var(--line);
	border-radius: var(--r-md);
}
@media (max-width: 760px) {
	.done {
		grid-template-columns: minmax(0, 1fr);
	}
	.done-receipt {
		display: none;
	}
}
</style>
