<script setup>
import { onMounted, ref } from "vue"
import { api, errorText } from "../api.js"
import { __ } from "../i18n.js"
import { go, store } from "../store.js"
import BigButton from "../components/BigButton.vue"

const PAGE_SIZE = 20
const issues = ref([])
const more = ref(false)
const busy = ref(false)
const error = ref("")

async function load(start) {
	busy.value = true
	error.value = ""
	try {
		const rows = await api.pending(start)
		issues.value = start ? issues.value.concat(rows) : rows
		more.value = rows.length === PAGE_SIZE
	} catch (e) {
		error.value = errorText(e)
	} finally {
		busy.value = false
	}
}
function open(issue) {
	store.issue = issue
	store.notice = ""
	go("detail")
}
onMounted(() => load(0))
</script>

<template>
	<div class="page">
		<div class="screen">
			<p v-if="store.notice" class="banner banner-ok" role="status">{{ store.notice }}</p>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<div class="list">
				<button v-for="issue in issues" :key="issue.name" type="button" class="card part" @click="open(issue)">
					<span class="grow">
						<strong v-if="issue.plate" dir="ltr">{{ issue.plate }}</strong>
						<span class="values">
							<span>{{ __("Maintenance") }}</span><b dir="ltr">{{ issue.maintenance }}</b>
							<span>{{ __("Qty") }}</span><b>{{ issue.items.length }}</b>
						</span>
					</span>
				</button>
			</div>
			<BigButton v-if="more" icon="plus" tone="soft" :label="__('Load more')" :busy="busy" @press="load(issues.length)" />
		</div>
	</div>
</template>
