<script setup>
import { ref } from "vue"
import { api, errorText } from "../../api.js"
import { __ } from "../../i18n.js"
import { desk, show } from "../../storekeeper.js"
import BigButton from "../../components/BigButton.vue"
import PartRow from "../../components/PartRow.vue"
import PlateChip from "../../components/PlateChip.vue"
import "./store.css"

const issue = desk.issue
const busy = ref(false)
const error = ref("")

function facts(row) {
	return [
		{ label: __("Qty"), value: row.qty },
		{ label: __("Available"), value: row.available },
	]
}
async function approve() {
	busy.value = true
	error.value = ""
	try {
		await api.approveIssue(issue.name)
		desk.notice = __("Issued")
		desk.issue = null
		show("approvals")
	} catch (e) {
		error.value = errorText(e)
		busy.value = false
	}
}
</script>

<template>
	<div class="page">
		<div v-if="issue" class="screen">
			<h1 class="screen-title">{{ __("Approvals") }}</h1>
			<PlateChip v-if="issue.plate" :plate="issue.plate" size="sm" />
			<PartRow :name="__('Maintenance')" :code="issue.maintenance" />
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<div class="store-list">
				<PartRow v-for="(row, index) in issue.items" :key="index" :name="row.item_name" :code="row.item_code" :image="row.image || ''" :facts="facts(row)" />
			</div>
		</div>
		<div v-if="issue" class="dock">
			<BigButton icon="check" tone="ok" :label="__('Approve')" :busy="busy" @press="approve" />
		</div>
	</div>
</template>
