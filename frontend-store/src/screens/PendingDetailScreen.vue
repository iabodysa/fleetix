<script setup>
import { ref } from "vue"
import { api, errorText } from "../api.js"
import { __ } from "../i18n.js"
import { go, store } from "../store.js"
import BigButton from "../components/BigButton.vue"

const issue = store.issue
const busy = ref(false)
const error = ref("")

async function approve() {
	busy.value = true
	error.value = ""
	try {
		await api.approve(issue.name)
		store.notice = __("Issued")
		store.issue = null
		go("pending")
	} catch (e) {
		error.value = errorText(e)
		busy.value = false
	}
}
</script>

<template>
	<div class="page">
		<div v-if="issue" class="screen">
			<div class="card values">
				<template v-if="issue.plate"><span>{{ __("Plate") }}</span><b dir="ltr">{{ issue.plate }}</b></template>
				<span>{{ __("Maintenance") }}</span><b dir="ltr">{{ issue.maintenance }}</b>
			</div>
			<div class="list">
				<div v-for="(row, index) in issue.items" :key="index" class="card part">
					<img v-if="row.image" :src="row.image" alt="" />
					<span class="grow">
						<strong>{{ row.item_name }}</strong>
						<span class="values">
							<span>{{ __("Qty") }}</span><b>{{ row.qty }}</b>
							<span>{{ __("Available") }}</span><b>{{ row.available }}</b>
						</span>
					</span>
				</div>
			</div>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
		</div>
		<div v-if="issue" class="dock">
			<BigButton icon="check" :label="__('Approve')" :busy="busy" @press="approve" />
		</div>
	</div>
</template>
