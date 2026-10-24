<script setup>
import { ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { useFinalCheck } from "../../composables/useFinalCheck.js"
import { go, store } from "../../store/index.js"
import BigButton from "../../components/BigButton.vue"
import CardProgress from "../../components/CardProgress.vue"
import FindingsTable from "../../components/FindingsTable.vue"
import PlateChip from "../../components/PlateChip.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import ServiceChecklist from "../../components/ServiceChecklist.vue"

const walkin = store.walkin
const check = useFinalCheck(walkin.checks, walkin.findings)
const error = ref("")
const busy = ref(false)

async function finish() {
	if (check.progress.guard()) return
	busy.value = true
	try {
		walkin.invoice = await api.finishWalkin({
			plate: walkin.plate.trim(),
			customer_name: walkin.name.trim(),
			mobile_no: walkin.mobile,
			items: JSON.stringify(walkin.items.map((row) => ({ item_code: row.item_code, qty: row.qty }))),
			final_check: JSON.stringify(check.answers()),
			findings: JSON.stringify(walkin.findings),
		})
		go("walkinInvoice")
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
</script>

<template>
	<ScreenFrame :title="__('Final check')" v-model:error="error">
		<template #meta>
			<PlateChip :plate="walkin.plate" size="md" />
			<span v-if="check.open.value" class="pill tone-wait">{{ __("{0} left", [check.open.value]) }}</span>
		</template>
		<div class="review">
			<CardProgress :items="check.cards.value" @show="check.progress.show" />
			<ServiceChecklist :rows="walkin.checks" @answer="check.answer" />
			<FindingsTable :findings="walkin.findings" :parts="check.parts.value" />
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('walkinItems')" />
		</template>
		<template #primary>
			<BigButton icon="done" tone="done" :label="busy ? __('Finishing') : check.progress.nextLabel(__('Issue invoice'))" :busy="busy" @press="finish" />
		</template>
	</ScreenFrame>
</template>
