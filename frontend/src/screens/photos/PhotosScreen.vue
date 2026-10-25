<script setup>
import { computed, onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const error = ref("")
const tiles = computed(() => store.photos.flatMap((group) => group.photos.map((url) => ({ url, label: group.slot ? group.label : "" }))))

onMounted(async () => {
	try {
		store.photos = await api.photos(store.visit.maintenance)
	} catch (e) {
		error.value = errorText(e)
	}
})
</script>

<template>
	<ScreenFrame :title="__('Photos')" v-model:error="error">
		<div class="photos">
			<p class="photos-count">
				<span class="pill" :class="tiles.length ? 'tone-done' : 'tone-wait'">{{ __("Photos added") }} <span class="ltr">{{ tiles.length }}</span></span>
			</p>
			<p v-if="!tiles.length" class="photos-none"><AppIcon name="photos" size="lg" />{{ __("No photos taken at the gate") }}</p>
			<div v-else class="photos-slots">
				<div v-for="tile in tiles" :key="tile.url" class="card photos-slot">
					<img class="photos-thumb" :src="tile.url" alt="" />
					<span v-if="tile.label" class="photos-label">{{ tile.label }}</span>
				</div>
			</div>
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('damage')" />
		</template>
		<template #primary>
			<BigButton icon="next" :label="__('Next')" @press="go('signatures')" />
		</template>
	</ScreenFrame>
</template>

<style>
.photos {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
	min-width: 0;
}
.photos-none {
	display: flex;
	align-items: center;
	gap: var(--s2);
	color: var(--ink-2);
	font-weight: 700;
}
.photos-slots {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(9rem, 1fr));
	gap: var(--s2);
}
.photos-slot {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: var(--s1);
	padding: var(--s2);
	border: 2px solid var(--done);
	text-align: center;
}
.photos-label {
	font-weight: 700;
}
.photos-thumb {
	width: 100%;
	height: 5rem;
	object-fit: cover;
	border-radius: var(--r-md);
}
</style>
