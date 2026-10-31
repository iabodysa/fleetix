<script setup>
import { onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { backHome, go } from "../../store/index.js"
import { desk } from "../../store/storekeeper.js"
import BigButton from "../../components/BigButton.vue"
import EmptyState from "../../components/EmptyState.vue"
import PartRow from "../../components/PartRow.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import "./store.css"

const PAGE = 20
const issues = ref([])
const loading = ref(false)
const more = ref(false)
const error = ref("")

async function load(start) {
	loading.value = true
	try {
		const rows = await api.pendingIssues(start)
		issues.value = start ? issues.value.concat(rows) : rows
		more.value = rows.length === PAGE
	} catch (e) {
		error.value = errorText(e)
	} finally {
		loading.value = false
	}
}
function facts(issue) {
	return [
		{ label: __("Maintenance"), value: issue.maintenance, ltr: true },
		{ label: __("Parts"), value: issue.items.length },
	]
}
function open(issue) {
	desk.issue = issue
	desk.notice = ""
	go("approval")
}
onMounted(() => load(0))
</script>

<template>
	<ScreenFrame :title="__('Approvals')" v-model:error="error">
		<template #meta>
			<span v-if="desk.notice" class="pill tone-done" role="status">{{ desk.notice }}</span>
		</template>
		<div class="store-list">
			<p v-if="loading && !issues.length" class="queue-loading">{{ __("Loading") }}</p>
			<EmptyState v-else-if="!issues.length" :label="__('No pending approvals')" />
			<PartRow v-for="issue in issues" :key="issue.name" :name="issue.plate || issue.name" :facts="facts(issue)" pressable @press="open(issue)" />
			<BigButton v-if="more" class="store-more" icon="down" tone="quiet" :label="__('Load more')" :busy="loading" block @press="load(issues.length)" />
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="backHome" />
		</template>
	</ScreenFrame>
</template>
