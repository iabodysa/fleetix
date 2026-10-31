<script setup>
import { ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { go } from "../../store/index.js"
import { desk, pickItem, storeBoot } from "../../store/storekeeper.js"
import BigButton from "../../components/BigButton.vue"
import PartRow from "../../components/PartRow.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"
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
	<ScreenFrame :title="__('Unknown barcode')" v-model:error="error">
		<template #meta>
			<span class="pill ltr">{{ unknown.code }}</span>
		</template>
		<div class="store-stack">
			<p v-if="suggestions.length" class="store-label">{{ __("Suggested parts") }}</p>
			<div class="store-list">
				<PartRow
					v-for="item in suggestions"
					:key="item.item_code"
					:name="item.item_name"
					:code="item.item_code"
					:image="item.image || ''"
					pressable
					@press="pick(item.item_code)"
				/>
			</div>
		</div>
		<template #aside>
			<div class="store-stack">
				<label class="store-field">
					<span>{{ __("Part name") }}</span>
					<input v-model="name" class="store-input" type="search" autocomplete="off" @change="search" />
				</label>
				<label v-if="storeBoot.data.models.length" class="store-field">
					<span>{{ __("Vehicle model") }}</span>
					<select v-model="model" class="store-input" @change="search">
						<option value=""></option>
						<option v-for="option in storeBoot.data.models" :key="option" :value="option">{{ option }}</option>
					</select>
				</label>
			</div>
		</template>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('receive')" />
		</template>
		<template #primary>
			<BigButton icon="plus" :label="__('New part')" @press="go('newPart')" />
		</template>
	</ScreenFrame>
</template>
