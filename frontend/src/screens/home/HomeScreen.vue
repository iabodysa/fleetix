<script setup>
import { __ } from "../../i18n/index.js"
import { go, newWalkin, queue } from "../../store/index.js"
import IconTile from "../../components/IconTile.vue"

function fleet() {
	queue.fetch()
	go("queue")
}
</script>

<template>
	<section class="home">
		<IconTile icon="fleet" :label="__('Etihad fleet maintenance')" :note="queue.data.length ? __('{0} vehicles waiting', [queue.data.length]) : ''" @press="fleet" />
		<IconTile icon="customer" :label="__('Customer maintenance')" @press="newWalkin" />
	</section>
</template>

<style>
.home {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
	gap: var(--s5);
	align-content: center;
	min-height: 60vh;
	padding: var(--s5) 0;
}
.home .icon-tile {
	min-height: 16rem;
}
.home .icon-tile-label {
	font-size: var(--t-xl);
}
</style>
