<template>
	<section class="screen">
		<div class="screen-split">
			<div class="pane">
				<div class="done-head">
					<span class="done-mark">✓</span>
					<div>
						<h1>{{ __("Maintenance completed") }}</h1>
						<div class="muted" dir="ltr">{{ result.maintenance }}</div>
					</div>
				</div>
				<h2>{{ __("Next service") }}</h2>
				<div class="tiles">
					<div v-for="row in result.next_due" :key="row.component" class="tile tile-static" :class="{ ticked: row.replaced }">
						<span class="tile-name">{{ componentLabel(row.component) }}</span>
						<span class="tile-due">{{ dueText(row) }}</span>
						<span v-if="row.replaced" class="pill pill-ok">{{ __("Replaced today") }}</span>
						<span v-else class="pill" :class="'pill-' + tone[row.state]">{{ stateText[row.state] }}</span>
					</div>
				</div>
				<div class="chips done-pills">
					<span class="chip" :class="store.printed ? 'chip-ok' : 'chip-muted'">{{ store.printed ? __("Receipt printed") : __("Printer not connected") }}</span>
					<span class="chip" :class="store.display ? 'chip-ok' : 'chip-muted'">{{ store.display ? __("On customer screen") : __("Customer screen not connected") }}</span>
				</div>
				<p class="error">{{ error }}</p>
			</div>
			<aside class="side receipt-side">
				<img class="receipt" :src="receipt" alt="" />
			</aside>
		</div>
		<footer class="foot">
			<button class="btn btn-back" type="button" @click="print">{{ __("Print again") }}</button>
			<span></span>
			<button class="btn btn-primary" type="button" @click="backToQueue">{{ __("Next vehicle") }}</button>
		</footer>
	</section>
</template>

<script setup>
import { onMounted, ref } from "vue"
import { __, componentLabel, statusLabel } from "../translate.js"
import { errorText } from "../api.js"
import { dueText, printReceipt, receiptCanvas, showOnCustomerDisplay } from "../native.js"
import { backToQueue, store } from "../store.js"

const result = store.result
const receipt = receiptCanvas(result).toDataURL("image/png")
const error = ref("")
const tone = { overdue: "bad", soon: "warn", ok: "ok" }
const stateText = { overdue: __("Overdue"), soon: __("Due soon"), ok: __("Good") }

async function print() {
	try {
		store.printed = await printReceipt(result)
	} catch (e) {
		error.value = errorText(e)
	}
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
