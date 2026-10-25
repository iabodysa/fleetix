<script setup>
import { computed, ref, watch } from "vue"
import { api, errorText } from "../api.js"
import { problem } from "../composables/useFeedback.js"
import { __, formatKm, isolate, statusLabel } from "../i18n/index.js"
import { hasPrinter, printDocument } from "../native.js"
import AppIcon from "./AppIcon.vue"
import BigButton from "./BigButton.vue"
import ErrorCard from "./ErrorCard.vue"

const props = defineProps({ vehicle: { type: String, required: true } })
defineEmits(["close"])

const PRINT_LABELS = {
	"Thermal Vehicle Card": () => __("Vehicle Card"),
	"Thermal Vehicle Label": () => __("Vehicle Label"),
	"Thermal Gate Entry Pass": () => __("Gate Entry Pass"),
	"Thermal Gate Exit Pass": () => __("Gate Exit Pass"),
	"Thermal Damage Sheet": () => __("Damage Sheet"),
}
const SOURCE_LABELS = {
	Maintenance: () => __("Maintenance"),
	"Vehicle Inspection": () => __("Vehicle Inspection"),
	"Vehicle Handover": () => __("Vehicle Handover"),
}
const profile = ref(null)
const error = ref("")
const printing = ref("")
const opened = ref("")
const zoomed = ref("")

function visitType(type) {
	return { Periodic: __("Periodic"), Emergency: __("Emergency") }[type] || type
}
function pairs(rows) {
	return rows.filter((row) => row[1] !== null && row[1] !== undefined && row[1] !== "" && row[1] !== 0)
}
const identity = computed(() => {
	const car = profile.value.vehicle
	return pairs([
		[__("Plate"), car.license_plate],
		[__("Manufacturer"), car.make],
		[__("Model"), car.model],
		[__("Year"), car.model_year],
		[__("Vehicle Type"), car.vehicle_type],
		[__("Color"), car.color],
		[__("Status"), car.status && __(car.status)],
		[__("Project"), car.current_project],
		[__("Istimara No"), car.istimara_no],
		[__("Registration Expiry"), car.registration_expiry && isolate(car.registration_expiry)],
		[__("Chassis No"), car.chassis_no],
	])
})
const last = computed(() => {
	const visit = profile.value.last_maintenance
	return visit ? pairs([[__("Date"), isolate(visit.date)], [__("Type"), visitType(visit.type)], [__("Odometer"), visit.odometer && formatKm(visit.odometer)], [__("Visit"), visit.name]]) : []
})
const reading = computed(() => {
	const odometer = profile.value.odometer
	const source = SOURCE_LABELS[odometer.doctype]
	return pairs([[__("Odometer"), odometer.value && formatKm(odometer.value)], [__("Date"), odometer.date && isolate(odometer.date)], [__("Source"), source && source() + " " + odometer.name]])
})
const driver = computed(() => {
	const assignment = profile.value.assignment || {}
	return pairs([
		[__("Driver"), profile.value.driver],
		[__("Authorized by"), assignment.approved_by],
		[__("Authorization"), assignment.name],
		[__("Assigned to"), assignment.driver !== profile.value.driver ? assignment.driver : null],
		[__("From"), assignment.from_date && isolate(assignment.from_date)],
		[__("To"), assignment.to_date && isolate(assignment.to_date)],
	])
})
const prints = computed(() => (hasPrinter() ? profile.value.prints : []))

async function load() {
	profile.value = null
	try {
		profile.value = await api.vehicleProfile(props.vehicle)
	} catch (e) {
		error.value = errorText(e)
	}
}
async function print(row) {
	printing.value = row.format
	try {
		if (!(await printDocument(row.doctype, row.name, row.format))) error.value = __("Printer not connected")
	} catch (e) {
		error.value = errorText(e)
		problem()
	}
	printing.value = ""
}
watch(() => props.vehicle, load, { immediate: true })
</script>

<template>
	<div class="profile">
		<div class="drawer-head">
			<h2>{{ __("Vehicle") }}</h2>
			<button class="app-header-button" type="button" :aria-label="__('Close')" @click="$emit('close')"><AppIcon name="close" /></button>
		</div>
		<p v-if="!profile && !error" class="muted">{{ __("Loading") }}</p>
		<template v-if="profile">
			<img v-if="profile.front_photo" class="profile-front" :src="profile.front_photo" alt="" @click="zoomed = profile.front_photo" />
			<section v-for="group in [[__('Vehicle'), identity], [__('Last maintenance'), last], [__('Last reading'), reading], [__('Driver'), driver]]" v-show="group[1].length" :key="group[0]" class="card profile-group">
				<h3>{{ group[0] }}</h3>
				<dl class="facts">
					<div v-for="row in group[1]" :key="row[0]">
						<dt>{{ row[0] }}</dt>
						<dd>{{ row[1] }}</dd>
					</div>
				</dl>
			</section>
			<div v-if="prints.length" class="profile-prints">
				<BigButton v-for="row in prints" :key="row.format" icon="printer" tone="quiet" :label="PRINT_LABELS[row.format]()" :busy="printing === row.format" :disabled="!!printing" @press="print(row)" />
			</div>
			<section v-if="profile.visits.length" class="profile-group">
				<h3>{{ __("Previous visits") }}</h3>
				<div v-for="visit in profile.visits" :key="visit.name" class="card profile-visit">
					<button class="profile-visit-row" type="button" :disabled="!visit.photos.length" @click="opened = opened === visit.name ? '' : visit.name">
						<b class="ltr">{{ isolate(visit.date) }}</b>
						<span>{{ visitType(visit.type) }}</span>
						<span v-if="visit.odometer" class="ltr">{{ formatKm(visit.odometer) }}</span>
						<span class="pill tone-quiet">{{ statusLabel(visit.status) || __(visit.status) }}</span>
						<span v-if="visit.photos.length" class="muted"><AppIcon name="photos" /> {{ visit.photos.length }}</span>
					</button>
					<div v-if="opened === visit.name" class="profile-thumbs">
						<img v-for="photo in visit.photos" :key="photo.url" class="photos-thumb" :src="photo.url" :alt="__(photo.slot)" @click="zoomed = photo.url" />
					</div>
				</div>
			</section>
		</template>
		<ErrorCard :error="error" @dismiss="error = ''" />
		<div v-if="zoomed" class="profile-zoom" @click="zoomed = ''"><img :src="zoomed" alt="" /></div>
	</div>
</template>

<style>
.drawer.drawer-wide {
	width: 40rem;
}
.profile {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
}
.profile h3 {
	margin: 0 0 var(--s2);
	font-size: var(--t-md);
	font-weight: 800;
}
.profile-group {
	padding: var(--s3);
}
.profile-front {
	width: 100%;
	max-height: 10rem;
	object-fit: cover;
	border-radius: var(--r-lg);
}
.profile-prints {
	display: grid;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	gap: var(--s2);
}
.profile-visit {
	margin-bottom: var(--s2);
	padding: var(--s2) var(--s3);
}
.profile-visit-row {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: var(--s2) var(--s4);
	width: 100%;
	padding: 0;
	border: 0;
	background: none;
	color: inherit;
	font: inherit;
	text-align: start;
}
.profile-thumbs {
	display: grid;
	grid-template-columns: repeat(4, minmax(0, 1fr));
	gap: var(--s2);
	margin-top: var(--s2);
}
.profile-zoom {
	position: fixed;
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
	z-index: 30;
	display: flex;
	align-items: center;
	justify-content: center;
	background: rgba(0, 0, 0, 0.85);
}
.profile-zoom img {
	max-width: 100%;
	max-height: 100%;
}
</style>
