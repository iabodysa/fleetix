<script setup>
import { computed, ref } from "vue"
import { offerUndo } from "../composables/useUndo.js"
import { __ } from "../i18n/index.js"
import AppIcon from "./AppIcon.vue"
import NumberPad from "./NumberPad.vue"
import { PLATE_LETTERS } from "./plate.js"

const props = defineProps({
	modelValue: { type: String, default: "" },
	maxDigits: { type: Number, default: 4 },
	maxLetters: { type: Number, default: 3 },
})
const emit = defineEmits(["update:modelValue"])
const pad = ref("digits")
const digits = computed(() => props.modelValue.replace(/[^0-9]/g, ""))
const letters = computed(() => props.modelValue.replace(/[^A-Z]/g, ""))
const digitCells = computed(() => Array.from({ length: props.maxDigits }, (_, index) => digits.value[index] || ""))
const letterCells = computed(() => Array.from({ length: props.maxLetters }, (_, index) => letters.value[index] || ""))

function put(nextDigits, nextLetters) {
	emit("update:modelValue", nextDigits + nextLetters)
}
function addDigit(digit) {
	if (digits.value.length >= props.maxDigits) return
	put(digits.value + digit, letters.value)
}
function addLetter(letter) {
	if (letters.value.length < props.maxLetters) put(digits.value, letters.value + letter)
}
function erase() {
	if (letters.value) return put(digits.value, letters.value.slice(0, -1))
	pad.value = "digits"
	put(digits.value.slice(0, -1), "")
}
function clear() {
	const before = props.modelValue
	if (!before) return
	pad.value = "digits"
	put("", "")
	offerUndo(__("Plate number cleared"), () => emit("update:modelValue", before))
}
</script>

<template>
	<div class="plate-keypad">
		<div class="plate-keypad-readout ltr" :aria-label="__('Plate number')">
			<span v-for="(digit, index) in digitCells" :key="'d' + index" class="plate-keypad-cell" :class="{ empty: !digit }">{{ digit || "·" }}</span>
			<span class="plate-keypad-split"></span>
			<span v-for="(letter, index) in letterCells" :key="'l' + index" class="plate-keypad-cell" :class="{ empty: !letter }">{{ letter || "·" }}</span>
			<button class="plate-keypad-clear" type="button" :aria-label="__('Clear')" :disabled="!modelValue" @click="clear">
				<AppIcon name="close" />
			</button>
		</div>
		<div v-if="pad === 'letters'" class="letter-pad ltr">
			<button v-for="[latin, arabic] in PLATE_LETTERS" :key="latin" class="number-key letter-key" type="button" @click="addLetter(latin)">
				<span class="letter-key-ar">{{ arabic }}</span>
				<span>{{ latin }}</span>
			</button>
			<button class="number-key number-key-soft letter-key-switch" type="button" :aria-label="__('Numbers')" @click="pad = 'digits'">123</button>
			<button class="number-key number-key-soft" type="button" :aria-label="__('Delete')" @click="erase">
				<AppIcon name="erase" size="lg" />
			</button>
		</div>
		<NumberPad v-else @key="addDigit" @erase="erase">
			<template #lead>
				<button class="number-key number-key-soft letter-key-switch" type="button" :aria-label="__('Letters')" @click="pad = 'letters'">ABC</button>
			</template>
		</NumberPad>
	</div>
</template>

<style>
.plate-keypad {
	display: flex;
	flex-direction: column;
	gap: var(--s3);
}
.plate-keypad-readout {
	display: flex;
	align-items: center;
	justify-content: center;
	gap: var(--s1);
	padding: var(--s2) var(--s2) var(--s2) var(--s3);
	border: 3px solid var(--plate-ink);
	border-radius: var(--r-md);
	background: var(--plate);
	color: var(--plate-ink);
}
.plate-keypad-cell {
	width: 2.1rem;
	font-size: var(--t-xxl);
	font-weight: 800;
	line-height: 1;
	text-align: center;
	font-variant-numeric: tabular-nums;
}
.plate-keypad-cell.empty {
	color: var(--plate-muted);
}
.plate-keypad-split {
	align-self: stretch;
	width: 2px;
	margin: 0 var(--s2);
	background: var(--plate-ink);
}
.plate-keypad-clear {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: var(--tap);
	height: var(--tap);
	margin-left: auto;
	border: 0;
	border-radius: var(--r-md);
	background: var(--surface-2);
	color: var(--ink-2);
}
.plate-keypad-clear:disabled {
	visibility: hidden;
}
.letter-pad {
	display: grid;
	grid-template-columns: repeat(5, 1fr);
	gap: var(--s2);
}
.letter-key {
	flex-direction: column;
	line-height: 1;
}
.letter-key-ar {
	font-size: var(--t-md);
	color: var(--ink-2);
}
.letter-key-switch {
	font-size: var(--t-lg);
}
</style>
