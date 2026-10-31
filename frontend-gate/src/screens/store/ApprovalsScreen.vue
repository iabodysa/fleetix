<script setup>
import { onMounted, ref } from "vue"
import { api, errorText } from "../../api.js"
import { __ } from "../../i18n.js"
import { desk, show } from "../../storekeeper.js"
import BigButton from "../../components/BigButton.vue"
import PartRow from "../../components/PartRow.vue"
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
	show("approval")
}
onMounted(() => load(0))
</script>

<template>
	<div class="page">
		<div class="screen">
			<h1 class="screen-title">{{ __("Approvals") }}</h1>
			<p v-if="desk.notice" class="banner banner-ok" role="status">{{ desk.notice }}</p>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<p v-if="loading && !issues.length" class="store-hint">{{ __("Loading") }}</p>
			<p v-else-if="!issues.length" class="store-hint">{{ __("No pending approvals") }}</p>
			<div class="store-list">
				<PartRow v-for="issue in issues" :key="issue.name" :name="issue.plate || issue.name" :facts="facts(issue)" pressable @press="open(issue)" />
			</div>
			<BigButton v-if="more" icon="plus" tone="soft" :label="__('Load more')" :busy="loading" @press="load(issues.length)" />
		</div>
	</div>
</template>
