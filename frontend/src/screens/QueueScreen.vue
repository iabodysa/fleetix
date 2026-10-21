<template>
	<section class="screen screen-split">
		<div class="pane">
			<div class="pane-head">
				<h1>{{ __("Vehicles due") }}</h1>
				<button class="btn btn-soft" type="button" @click="queue.fetch()">{{ __("Refresh") }}</button>
			</div>
			<QueueList :filter="filter" />
		</div>
		<aside class="side">
			<span class="label">{{ __("Plate number") }}</span>
			<div class="search-readout" dir="ltr">{{ filter || "-" }}</div>
			<KeyPad @key="filter = (filter + $event).slice(0, 4)" @clear="filter = ''" @back="filter = filter.slice(0, -1)" />
		</aside>
	</section>
</template>

<script setup>
import { ref } from "vue"
import { queue } from "../store.js"
import KeyPad from "../components/KeyPad.vue"
import QueueList from "../components/QueueList.vue"

const filter = ref("")
</script>
