<script setup>
import { computed, ref, watch } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { go } from "../../store/index.js"
import { desk, pickItem, storeBoot } from "../../store/storekeeper.js"
import BigButton from "../../components/BigButton.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
import "./store.css"

const SPARE_PARTS = "Spare Parts"
const groups = computed(() => storeBoot.data.groups || [])
const name = ref("")
const model = ref("")
const group = ref("")
const code = ref(desk.unknown ? desk.unknown.code : "")
const busy = ref(false)
const error = ref("")

watch(
	groups,
	(list) => {
		if (!group.value && list.indexOf(SPARE_PARTS) !== -1) group.value = SPARE_PARTS
	},
	{ immediate: true },
)
async function save() {
	busy.value = true
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
	<ScreenFrame :title="__('New part')" v-model:error="error">
		<form class="store-stack store-form" @submit.prevent="save">
			<label class="store-field">
				<span>{{ __("Part name") }}</span>
				<input v-model="name" class="store-input" autocomplete="off" required />
			</label>
			<label v-if="storeBoot.data.models.length" class="store-field">
				<span>{{ __("Vehicle model") }}</span>
				<select v-model="model" class="store-input">
					<option value=""></option>
					<option v-for="option in storeBoot.data.models" :key="option" :value="option">{{ option }}</option>
				</select>
			</label>
			<label class="store-field">
				<span>{{ __("Item Group") }}</span>
				<select v-model="group" class="store-input" required>
					<option v-for="option in groups" :key="option" :value="option">{{ __(option) }}</option>
				</select>
			</label>
			<label class="store-field">
				<span>{{ __("Code") }}</span>
				<input v-model="code" class="store-input ltr" autocomplete="off" />
			</label>
			<button type="submit" hidden></button>
		</form>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('match')" />
		</template>
		<template #primary>
			<BigButton icon="done" :label="__('Save')" :busy="busy" :disabled="!name || !group" @press="save" />
		</template>
	</ScreenFrame>
</template>
