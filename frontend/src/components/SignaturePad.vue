<template>
	<div class="sign">
		<div class="sign-head">
			<span class="label">{{ label }}</span>
			<button class="btn-link" type="button" @click="clear">{{ __("Clear") }}</button>
		</div>
		<canvas
			ref="canvas"
			class="sign-canvas"
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

<script setup>
import { onMounted, ref } from "vue"

const props = defineProps({ label: String, value: String })
const emit = defineEmits(["change"])
const canvas = ref(null)
let drawing = false
let usesPointer = false

function point(x, y) {
	const box = canvas.value.getBoundingClientRect()
	return [((x - box.left) * canvas.value.width) / box.width, ((y - box.top) * canvas.value.height) / box.height]
}
function begin(x, y) {
	const ctx = canvas.value.getContext("2d")
	ctx.lineWidth = 4
	ctx.lineCap = "round"
	ctx.strokeStyle = "#0D1317"
	ctx.beginPath()
	ctx.moveTo.apply(ctx, point(x, y))
	drawing = true
}
function draw(x, y) {
	if (!drawing) return
	const ctx = canvas.value.getContext("2d")
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
onMounted(() => {
	if (!props.value) return
	const image = new Image()
	image.onload = () => canvas.value && canvas.value.getContext("2d").drawImage(image, 0, 0)
	image.src = props.value
})
function clear() {
	canvas.value.getContext("2d").clearRect(0, 0, canvas.value.width, canvas.value.height)
	emit("change", null)
}
</script>
