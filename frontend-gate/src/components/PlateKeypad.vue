<script setup>
import { computed, ref } from "vue"
import { PLATE_LETTERS, plateDigit, plateLetter } from "../plate.js"
import { __ } from "../i18n.js"
import GateIcon from "./GateIcon.vue"

const props = defineProps({
	modelValue: { type: String, default: "" },
	mode: { type: String, default: "plate" },
	maxDigits: { type: Number, default: 4 },
	maxLetters: { type: Number, default: 3 },
})
const emit = defineEmits(["update:modelValue"])
const DIGITS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
const pad = ref("digits")

const digits = computed(() => (props.modelValue.match(/[0-9]/g) || []).join(""))
const letters = computed(() => (props.modelValue.match(/[A-Z]/g) || []).join(""))
const showLetters = computed(() => props.mode === "plate" && pad.value === "letters")
const digitLabel = (digit) => (props.mode === "plate" ? plateDigit(digit) : digit)

function compose(nextDigits, nextLetters) {
	emit("update:modelValue", props.mode === "plate" ? (nextDigits + " " + nextLetters).trim() : nextDigits)
}
function addDigit(digit) {
	if (digits.value.length >= props.maxDigits) return
	const next = digits.value + digit
	compose(next, letters.value)
	if (props.mode === "plate" && next.length === props.maxDigits) pad.value = "letters"
}
function addLetter(letter) {
	if (letters.value.length >= props.maxLetters) return
	compose(digits.value, letters.value + letter)
}
function erase() {
	if (showLetters.value && letters.value) compose(digits.value, letters.value.slice(0, -1))
	else if (letters.value && !digits.value) compose(digits.value, letters.value.slice(0, -1))
	else compose(digits.value.slice(0, -1), letters.value)
}
</script>

<template>
	<div class="keypad">
		<div v-if="mode === 'plate'" class="switch" role="tablist">
			<button type="button" role="tab" :aria-selected="pad === 'digits'" :class="{ on: pad === 'digits' }" @click="pad = 'digits'">
				{{ ["1", "2", "3"].map(plateDigit).join("") }}
			</button>
			<button type="button" role="tab" :aria-selected="pad === 'letters'" :class="{ on: pad === 'letters' }" @click="pad = 'letters'">
				{{ __("Letters") }}
			</button>
		</div>
		<div v-if="showLetters" class="grid letters" dir="ltr">
			<button v-for="[latin] in PLATE_LETTERS" :key="latin" type="button" class="key" @click="addLetter(latin)">
				{{ plateLetter(latin) }}
			</button>
			<button type="button" class="key key-soft" :aria-label="__('Erase')" @click="erase"><GateIcon name="erase" /></button>
		</div>
		<div v-else class="grid digits" dir="ltr">
			<button v-for="digit in DIGITS" :key="digit" type="button" class="key" @click="addDigit(digit)">{{ digitLabel(digit) }}</button>
			<span></span>
			<button type="button" class="key" @click="addDigit('0')">{{ digitLabel("0") }}</button>
			<button type="button" class="key key-soft" :aria-label="__('Erase')" @click="erase"><GateIcon name="erase" /></button>
		</div>
	</div>
</template>

<style scoped>
.keypad {
	display: flex;
	flex-direction: column;
	gap: 10px;
}
.switch {
	display: grid;
	grid-template-columns: 1fr 1fr;
	background: var(--surface-2);
	border-radius: var(--radius);
	padding: 4px;
	gap: 4px;
}
.switch button {
	min-height: 48px;
	border: 0;
	border-radius: 10px;
	background: transparent;
	font-weight: 700;
	color: var(--ink-2);
}
.switch .on {
	background: var(--surface);
	color: var(--ink);
	box-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
}
.grid {
	display: grid;
	gap: 8px;
}
.digits {
	grid-template-columns: repeat(3, 1fr);
}
.letters {
	grid-template-columns: repeat(6, 1fr);
}
.key {
	min-height: 64px;
	border: 1px solid var(--line);
	border-radius: 12px;
	background: var(--surface);
	font-size: 26px;
	font-weight: 700;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	line-height: 1.1;
	transition: transform 100ms var(--ease);
}
.key:active {
	transform: scale(0.96);
	background: var(--surface-2);
}
.letters .key {
	font-size: 24px;
	min-height: 60px;
}
.key-soft {
	background: var(--surface-2);
}
</style>
