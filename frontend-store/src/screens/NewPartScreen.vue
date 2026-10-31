<script setup>
import { ref } from "vue"
import { api, errorText } from "../api.js"
import { pickItem, store } from "../store.js"
import BigButton from "../components/BigButton.vue"

const boot = window.frappe.boot
const name = ref("")
const model = ref("")
const SPARE_PARTS = "Spare Parts"
const group = ref((boot.groups || []).indexOf(SPARE_PARTS) !== -1 ? SPARE_PARTS : "")
const code = ref(store.unknown ? store.unknown.code : "")
const busy = ref(false)
const error = ref("")

async function save() {
	busy.value = true
	error.value = ""
	try {
		const item_code = await api.newPart({ name_ar: name.value, vehicle_model: model.value, item_group: group.value, code: code.value })
		await pickItem(item_code)
	} catch (e) {
		error.value = errorText(e)
		busy.value = false
	}
}
</script>

<template>
	<div class="page">
		<form class="screen" @submit.prevent="save">
			<label class="field">
				<span>{{ __("Part name") }}</span>
				<input v-model="name" autocomplete="off" required />
			</label>
			<label v-if="boot.models && boot.models.length" class="field">
				<span>{{ __("Vehicle model") }}</span>
				<select v-model="model">
					<option value=""></option>
					<option v-for="option in boot.models" :key="option" :value="option">{{ option }}</option>
				</select>
			</label>
			<label class="field">
				<span>{{ __("Item Group") }}</span>
				<select v-model="group" required>
					<option v-for="option in boot.groups" :key="option" :value="option">{{ __(option) }}</option>
				</select>
			</label>
			<label class="field">
				<span>{{ __("Code") }}</span>
				<input v-model="code" dir="ltr" autocomplete="off" />
			</label>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<button type="submit" hidden></button>
		</form>
		<div class="dock">
			<BigButton icon="check" :label="__('Save')" :busy="busy" :disabled="!name || !group" @press="save" />
		</div>
	</div>
</template>
