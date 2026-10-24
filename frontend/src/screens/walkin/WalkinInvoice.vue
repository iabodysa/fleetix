<script setup>
import { onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { errorText } from "../../api.js"
import { printDocument } from "../../native.js"
import { backHome, newWalkin, store } from "../../store/index.js"
import BigButton from "../../components/BigButton.vue"
import PlateChip from "../../components/PlateChip.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import SuccessCheck from "../../components/SuccessCheck.vue"

const PRINT_FORMAT = "Thermal Customer Invoice"
const walkin = store.walkin
const invoice = walkin.invoice
const error = ref("")
const busy = ref(false)

function money(value) {
	return Number(value || 0).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
async function print() {
	busy.value = true
	try {
		walkin.printed = await printDocument("Maintenance Invoice", invoice.maintenance_invoice, PRINT_FORMAT)
	} catch (e) {
		error.value = errorText(e)
	}
	busy.value = false
}
onMounted(() => {
	if (!walkin.printed) print()
})
</script>

<template>
	<ScreenFrame :title="__('Invoice issued')" v-model:error="error">
		<template #meta>
			<span class="muted ltr">{{ invoice.maintenance_invoice }}</span>
		</template>
		<SuccessCheck :label="__('Customer maintenance completed')" />
		<div class="card walkin-bill">
			<PlateChip :plate="invoice.plate" size="lg" />
			<p class="review-model">{{ invoice.customer_name }}</p>
			<div class="walkin-total"><span>{{ __("Total before VAT") }}</span><span class="ltr">{{ money(invoice.net_total) }}</span></div>
			<div class="walkin-total"><span>{{ __("VAT") }}</span><span class="ltr">{{ money(invoice.tax) }}</span></div>
			<div class="walkin-total walkin-grand"><b>{{ __("Total") }}</b><b class="ltr">{{ money(invoice.grand_total) }}</b></div>
			<div class="walkin-total"><span>{{ __("Payment") }}</span><span>{{ invoice.mode_of_payment }}</span></div>
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Home')" @press="backHome" />
		</template>
		<template #primary>
			<BigButton icon="printer" tone="quiet" :label="__('Print invoice')" :busy="busy" @press="print" />
			<BigButton icon="plus" :label="__('New customer')" @press="newWalkin" />
		</template>
	</ScreenFrame>
</template>

<style>
.walkin-bill {
	display: grid;
	gap: var(--s3);
	max-width: 36rem;
	margin: 0 auto;
	padding: var(--s4);
}
.walkin-bill .walkin-total {
	padding: 0;
	box-shadow: none;
}
.walkin-grand {
	font-size: var(--t-xl);
}
</style>
