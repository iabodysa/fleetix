<template>
	<div class="keypad" dir="ltr">
		<button v-for="key in keys" :key="key" class="key" type="button" @click="$emit('key', key)">{{ key }}</button>
		<button class="key key-soft" type="button" @click="$emit('clear')">{{ __("Clear") }}</button>
		<button class="key" type="button" @click="$emit('key', '0')">0</button>
		<button class="key key-soft" type="button" :aria-label="__('Delete')" @click="$emit('back')">&#9003;</button>
	</div>
</template>

<script setup>
defineEmits(["key", "clear", "back"])
const keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
</script>
