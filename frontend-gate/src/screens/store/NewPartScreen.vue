<script setup>
import { ref, watch } from "vue"
import { api, errorText } from "../../api.js"
import { __ } from "../../i18n.js"
import { desk, pickItem } from "../../storekeeper.js"
import BigButton from "../../components/BigButton.vue"
import "./store.css"

const SPARE_PARTS = "Spare Parts"
const name = ref("")
const model = ref("")
const group = ref("")
const code = ref(desk.unknown ? desk.unknown.code : "")
const busy = ref(false)
const error = ref("")

watch(
	() => desk.groups,
	(list) => {
		if (!group.value && list.indexOf(SPARE_PARTS) !== -1) group.value = SPARE_PARTS
	},
	{ immediate: true },
)
async function save() {
	busy.value = true
	error.value = ""
	try {
		const itemCode = await api.newPart({ name_ar: name.value, vehicle_model: model.value, item_group: group.value, code: code.value })
		await pickItem(itemCode)
	} catch (e) {
		error.value = errorText(e)
		busy.value = false
	}
}
</script>

<template>
	<div class="page">
		<form class="screen" @submit.prevent="save">
			<h1 class="screen-title">{{ __("New part") }}</h1>
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<label class="store-field">
				<span>{{ __("Part name") }}</span>
				<input v-model="name" class="store-input" autocomplete="off" required />
			</label>
			<label v-if="desk.models.length" class="store-field">
				<span>{{ __("Vehicle model") }}</span>
				<select v-model="model" class="store-input">
					<option value=""></option>
					<option v-for="option in desk.models" :key="option" :value="option">{{ option }}</option>
				</select>
			</label>
			<label class="store-field">
				<span>{{ __("Item Group") }}</span>
				<select v-model="group" class="store-input" required>
					<option v-for="option in desk.groups" :key="option" :value="option">{{ __(option) }}</option>
				</select>
			</label>
			<label class="store-field">
				<span>{{ __("Code") }}</span>
				<input v-model="code" class="store-input" dir="ltr" autocomplete="off" />
			</label>
			<button type="submit" hidden></button>
		</form>
		<div class="dock">
			<BigButton icon="check" tone="ok" :label="__('Save')" :busy="busy" :disabled="!name || !group" @press="save" />
		</div>
	</div>
</template>
