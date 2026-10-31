<script setup>
import { ref } from "vue"
import { api, errorText } from "../api.js"
import { __ } from "../i18n.js"
import { go, pickItem, store } from "../store.js"
import BigButton from "../components/BigButton.vue"

const boot = window.frappe.boot
const unknown = store.unknown || { code: "", suggestions: [] }
const suggestions = ref(unknown.suggestions || [])
const name = ref("")
const model = ref("")
const error = ref("")

async function search() {
	error.value = ""
	try {
		suggestions.value = await api.suggest(name.value || unknown.code, model.value)
	} catch (e) {
		error.value = errorText(e)
	}
}
async function pick(item_code) {
	error.value = ""
	try {
		await pickItem(item_code)
	} catch (e) {
		error.value = errorText(e)
	}
}
</script>

<template>
	<div class="page">
		<div class="screen">
			<div class="banner banner-warn values">
				<span>{{ __("Unknown barcode") }}</span><b dir="ltr">{{ unknown.code }}</b>
			</div>
			<label class="field">
				<span>{{ __("Part name") }}</span>
				<input v-model="name" autocomplete="off" @change="search" />
			</label>
			<label v-if="boot.models && boot.models.length" class="field">
				<span>{{ __("Vehicle model") }}</span>
				<select v-model="model" @change="search">
					<option value=""></option>
					<option v-for="option in boot.models" :key="option" :value="option">{{ option }}</option>
				</select>
			</label>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<div v-if="suggestions.length" class="field">
				<span>{{ __("Suggested parts") }}</span>
				<div class="list">
					<button v-for="item in suggestions" :key="item.item_code" type="button" class="card part" @click="pick(item.item_code)">
						<img v-if="item.image" :src="item.image" alt="" />
						<span class="grow">
							<strong>{{ item.item_name }}</strong>
							<span dir="ltr">{{ item.item_code }}</span>
						</span>
					</button>
				</div>
			</div>
		</div>
		<div class="dock">
			<BigButton icon="plus" tone="soft" :label="__('New part')" @press="go('newpart')" />
		</div>
	</div>
</template>
