<script setup>
import { ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { go } from "../../store/index.js"
import { desk } from "../../store/storekeeper.js"
import BigButton from "../../components/BigButton.vue"
import PartRow from "../../components/PartRow.vue"
import PlateChip from "../../components/PlateChip.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
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
	try {
		await api.approveIssue(issue.name)
		desk.notice = __("Issued")
		desk.issue = null
		go("approvals")
	} catch (e) {
		error.value = errorText(e)
		busy.value = false
	}
}
</script>

<template>
	<ScreenFrame :title="__('Approvals')" v-model:error="error">
		<template #meta>
			<PlateChip v-if="issue && issue.plate" :plate="issue.plate" size="sm" />
		</template>
		<div v-if="issue" class="store-stack">
			<dl class="facts">
				<div>
					<dt>{{ __("Maintenance") }}</dt>
					<dd class="ltr">{{ issue.maintenance }}</dd>
				</div>
			</dl>
			<div class="store-list">
				<PartRow v-for="(row, index) in issue.items" :key="index" :name="row.item_name" :code="row.item_code" :image="row.image || ''" :facts="facts(row)" />
			</div>
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('approvals')" />
		</template>
		<template #primary>
			<BigButton v-if="issue" icon="done" :label="__('Approve')" :busy="busy" @press="approve" />
		</template>
	</ScreenFrame>
</template>
