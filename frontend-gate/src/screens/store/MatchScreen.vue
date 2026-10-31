<script setup>
import { ref } from "vue"
import { api, errorText } from "../../api.js"
import { __ } from "../../i18n.js"
import { desk, pickItem, show } from "../../storekeeper.js"
import BigButton from "../../components/BigButton.vue"
import PartRow from "../../components/PartRow.vue"
import "./store.css"

const unknown = desk.unknown || { code: "", suggestions: [] }
const suggestions = ref(unknown.suggestions || [])
const name = ref("")
const model = ref("")
const error = ref("")

async function search() {
	try {
		suggestions.value = await api.suggestItems(name.value || unknown.code, model.value)
	} catch (e) {
		error.value = errorText(e)
	}
}
async function pick(itemCode) {
	try {
		await pickItem(itemCode)
	} catch (e) {
		error.value = errorText(e)
	}
}
</script>

<template>
	<div class="page">
		<div class="screen">
			<h1 class="screen-title">{{ __("Unknown barcode") }}</h1>
			<PartRow :name="__('Code')" :code="unknown.code" />
			<p v-if="error" class="banner banner-bad" role="alert">{{ error }}</p>
			<label class="store-field">
				<span>{{ __("Part name") }}</span>
				<input v-model="name" class="store-input" type="search" autocomplete="off" @change="search" />
			</label>
			<label v-if="desk.models.length" class="store-field">
				<span>{{ __("Vehicle model") }}</span>
				<select v-model="model" class="store-input" @change="search">
					<option value=""></option>
					<option v-for="option in desk.models" :key="option" :value="option">{{ option }}</option>
				</select>
			</label>
			<p v-if="suggestions.length" class="store-field">{{ __("Suggested parts") }}</p>
			<div class="store-list">
				<PartRow v-for="item in suggestions" :key="item.item_code" :name="item.item_name" :code="item.item_code" :image="item.image || ''" pressable @press="pick(item.item_code)" />
			</div>
		</div>
		<div class="dock">
			<BigButton icon="plus" :label="__('New part')" @press="show('newPart')" />
		</div>
	</div>
</template>
