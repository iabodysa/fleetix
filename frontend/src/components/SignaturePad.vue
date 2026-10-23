<script setup>
import { onMounted, ref } from "vue"
import { __ } from "../i18n/index.js"
import { offerUndo } from "../composables/useUndo.js"
import AppIcon from "./AppIcon.vue"

const props = defineProps({ label: { type: String, required: true }, value: { type: String, default: null } })
const emit = defineEmits(["change"])
const canvas = ref(null)
let drawing = false
let usesPointer = false

function pen() {
	const ctx = canvas.value.getContext("2d")
	ctx.lineWidth = 4
	ctx.lineCap = "round"
	ctx.strokeStyle = "#0b1520"
	return ctx
}
function point(x, y) {
	const box = canvas.value.getBoundingClientRect()
	return [((x - box.left) * canvas.value.width) / box.width, ((y - box.top) * canvas.value.height) / box.height]
}
function begin(x, y) {
	const ctx = pen()
	ctx.beginPath()
	ctx.moveTo.apply(ctx, point(x, y))
	drawing = true
}
function draw(x, y) {
	if (!drawing) return
	const ctx = pen()
	ctx.lineTo.apply(ctx, point(x, y))
	ctx.stroke()
}
function start(event) {
	usesPointer = true
	begin(event.clientX, event.clientY)
}
function move(event) {
	draw(event.clientX, event.clientY)
}
function startTouch(event) {
	if (usesPointer) return
	begin(event.touches[0].clientX, event.touches[0].clientY)
}
function moveTouch(event) {
	if (usesPointer) return
	draw(event.touches[0].clientX, event.touches[0].clientY)
}
function end() {
	if (!drawing) return
	drawing = false
	emit("change", canvas.value.toDataURL("image/png"))
}
function paint(dataUrl) {
	const image = new Image()
	image.onload = () => canvas.value && canvas.value.getContext("2d").drawImage(image, 0, 0)
	image.src = dataUrl
}
function wipe() {
	canvas.value.getContext("2d").clearRect(0, 0, canvas.value.width, canvas.value.height)
}
function clear() {
	const before = props.value
	wipe()
	emit("change", null)
	if (!before) return
	offerUndo(__("Signature cleared"), () => {
		paint(before)
		emit("change", before)
	})
}
onMounted(() => props.value && paint(props.value))
</script>

<template>
	<div class="sign">
		<div class="sign-head">
			<span class="sign-label"><AppIcon name="signature" />{{ label }}</span>
			<button class="app-header-button" type="button" :aria-label="__('Clear')" @click="clear"><AppIcon name="close" /></button>
		</div>
		<canvas
			ref="canvas"
			class="sign-canvas"
			:class="{ signed: value }"
			width="520"
			height="200"
			@pointerdown="start"
			@pointermove="move"
			@pointerup="end"
			@pointerleave="end"
			@touchstart.prevent="startTouch"
			@touchmove.prevent="moveTouch"
			@touchend.prevent="end"
		></canvas>
	</div>
</template>

<style>
.sign {
	display: flex;
	flex-direction: column;
	gap: var(--s2);
	min-width: 0;
}
.sign-head {
	display: flex;
	align-items: center;
	justify-content: space-between;
}
.sign-label {
	display: inline-flex;
	align-items: center;
	gap: var(--s2);
	font-weight: 800;
}
.sign-canvas {
	width: 100%;
	aspect-ratio: 520 / 200;
	border: 2px dashed var(--line);
	border-radius: var(--r-md);
	background: var(--plate);
	touch-action: none;
}
.sign-canvas.signed {
	border-style: solid;
	border-color: var(--done);
}
</style>
