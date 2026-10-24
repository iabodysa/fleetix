<script setup>
import { ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { useFinalCheck } from "../../composables/useFinalCheck.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import CardProgress from "../../components/CardProgress.vue"
import FindingsTable from "../../components/FindingsTable.vue"
import PlateChip from "../../components/PlateChip.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import ServiceChecklist from "../../components/ServiceChecklist.vue"

const walkin = store.walkin
const check = useFinalCheck(walkin.checks, walkin.findings)
const modes = (walkin.setup && walkin.setup.modes) || []
const error = ref("")
const busy = ref(false)

async function finish() {
	if (check.progress.guard()) return
	if (!walkin.mode) return (error.value = __("Choose how the customer pays"))
	busy.value = true
	try {
		walkin.invoice = await api.finishWalkin({
			plate: walkin.plate.trim(),
			customer_name: walkin.name.trim(),
			mobile_no: walkin.mobile,
			items: JSON.stringify(walkin.items.map((row) => ({ item_code: row.item_code, qty: row.qty }))),
			final_check: JSON.stringify(check.answers()),
			findings: JSON.stringify(walkin.findings),
			mode_of_payment: walkin.mode,
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
			<div class="card walkin-pay">
				<h2 class="findings-title">{{ __("Payment") }}</h2>
				<div class="walkin-modes">
					<button
						v-for="row in modes"
						:key="row.mode"
						type="button"
						class="walkin-mode"
						:class="{ pressed: walkin.mode === row.mode }"
						:disabled="!!row.problem"
						:aria-pressed="walkin.mode === row.mode ? 'true' : 'false'"
						@click="walkin.mode = row.mode"
					>
						<AppIcon :name="row.mode" size="lg" />
						<b>{{ row.label }}</b>
						<span v-if="row.problem" class="muted walkin-mode-problem">{{ row.problem }}</span>
					</button>
				</div>
			</div>
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('walkinItems')" />
		</template>
		<template #primary>
			<BigButton icon="done" tone="done" :label="busy ? __('Finishing') : check.progress.nextLabel(__('Issue invoice'))" :busy="busy" @press="finish" />
		</template>
	</ScreenFrame>
</template>

<style>
.walkin-pay {
	display: grid;
	gap: var(--s3);
	padding: var(--s4);
}
.walkin-modes {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
	gap: var(--s3);
}
.walkin-mode {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: var(--s2);
	min-height: 6rem;
	border: 2px solid var(--line);
	border-radius: var(--r-lg);
	background: var(--surface);
	font-size: var(--t-lg);
}
.walkin-mode.pressed {
	border-color: var(--primary);
	box-shadow: inset 0 0 0 2px var(--primary);
}
.walkin-mode:disabled {
	opacity: 0.55;
}
.walkin-mode-problem {
	font-size: var(--t-sm);
	text-align: center;
}
</style>
