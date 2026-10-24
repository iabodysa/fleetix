<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const POLL_MS = 5000
const error = ref("")
const link = ref(null)
const checking = ref(false)
let timer = null
const filled = computed(() => store.photos.filter((slot) => slot.photos.length).length)

async function poll() {
	try {
		store.photos = await api.photos(store.visit.maintenance)
	} catch (e) {
		error.value = errorText(e)
	}
}
async function next() {
	checking.value = true
	try {
		store.photos = await api.photos(store.visit.maintenance)
	} catch (e) {
		error.value = errorText(e)
		return
	} finally {
		checking.value = false
	}
	const missing = store.photos.filter((slot) => !slot.photos.length)
	if (missing.length) {
		error.value = { text: __("Take the photo: {0}", [missing[0].label]), detail: missing.map((slot) => slot.label).join(", ") }
		return
	}
	go("signatures")
}
onMounted(async () => {
	poll()
	timer = setInterval(poll, POLL_MS)
	try {
		link.value = await api.photoLink(store.visit.maintenance)
	} catch (e) {
		error.value = errorText(e)
	}
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
	<ScreenFrame :title="__('Photos')" v-model:error="error">
		<div class="photos">
			<div class="card photos-qr">
				<img v-if="link" class="photos-qr-code" :src="link.qr" alt="" />
				<p class="photos-qr-text"><AppIcon name="photos" size="lg" />{{ __("Scan with your phone to add photos") }}</p>
			</div>
			<div class="photos-landed">
				<p class="photos-count">
					<span class="pill" :class="filled === store.photos.length ? 'tone-done' : 'tone-wait'">{{ __("Photos added") }} <span class="ltr">{{ filled }} / {{ store.photos.length }}</span></span>
				</p>
				<div class="photos-slots">
					<div v-for="slot in store.photos" :key="slot.slot" class="card photos-slot" :class="{ 'photos-slot-done': slot.photos.length }">
						<img v-if="slot.photos.length" class="photos-thumb" :src="slot.photos[slot.photos.length - 1]" alt="" />
						<span v-else class="photos-empty"><AppIcon :name="slot.damage ? 'damage' : 'photos'" size="lg" /></span>
						<span class="photos-label">{{ slot.label }}</span>
					</div>
				</div>
			</div>
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('damage')" />
		</template>
		<template #primary>
			<BigButton icon="next" :label="__('Next')" :busy="checking" @press="next" />
		</template>
	</ScreenFrame>
</template>

<style>
.photos {
	display: grid;
	grid-template-columns: minmax(14rem, 20rem) minmax(0, 1fr);
	gap: var(--s5);
	align-items: start;
}
.photos-qr {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: var(--s3);
	padding: var(--s4);
}
.photos-qr-code {
	width: 100%;
	max-width: 15rem;
	aspect-ratio: 1;
	background: var(--plate);
	border-radius: var(--r-sm);
}
.photos-qr-text {
	display: flex;
	align-items: center;
	gap: var(--s2);
	font-weight: 700;
}
.photos-landed {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
	min-width: 0;
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
	border: 2px dashed var(--line);
	text-align: center;
}
.photos-slot-done {
	border: 2px solid var(--done);
}
.photos-empty {
	display: flex;
	align-items: center;
	justify-content: center;
	width: 100%;
	height: 5rem;
	color: var(--ink-2);
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
@media (max-width: 760px) {
	.photos {
		grid-template-columns: minmax(0, 1fr);
	}
}
</style>
