<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue"
import { __ } from "../../i18n/index.js"
import { api, errorText } from "../../api.js"
import { go, store } from "../../store/index.js"
import AppIcon from "../../components/AppIcon.vue"
import BigButton from "../../components/BigButton.vue"
import ScreenFrame from "../../components/ScreenFrame.vue"

const POLL_MS = 5000
const error = ref("")
const link = ref(null)
let timer = null

async function poll() {
	try {
		store.photos = await api.photos(store.visit.maintenance)
	} catch (e) {
		error.value = errorText(e)
	}
}
function next() {
	if (!store.photos.length) {
		error.value = __("Add at least one photo from the phone")
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
	<ScreenFrame :title="__('Photos')" :error="error">
		<div class="photos">
			<div class="card photos-qr">
				<img v-if="link" class="photos-qr-code" :src="link.qr" alt="" />
				<p class="photos-qr-text"><AppIcon name="photos" size="lg" />{{ __("Scan with your phone to add photos") }}</p>
			</div>
			<div class="photos-landed">
				<p class="photos-count">
					<span class="pill" :class="store.photos.length ? 'tone-done' : 'tone-wait'">{{ __("Photos added") }} <span class="ltr">{{ store.photos.length }}</span></span>
				</p>
				<div class="photos-strip">
					<img v-for="photo in store.photos" :key="photo.name" class="photos-thumb" :src="photo.file_url" alt="" />
				</div>
			</div>
		</div>
		<template #back>
			<BigButton icon="back" tone="quiet" :label="__('Back')" @press="go('damage')" />
		</template>
		<template #primary>
			<BigButton icon="next" :label="__('Next')" @press="next" />
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
.photos-strip {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(7rem, 1fr));
	gap: var(--s2);
}
.photos-thumb {
	width: 100%;
	aspect-ratio: 1;
	object-fit: cover;
	border-radius: var(--r-md);
}
@media (max-width: 760px) {
	.photos {
		grid-template-columns: minmax(0, 1fr);
	}
}
</style>
