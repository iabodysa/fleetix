<script setup>
import { __ } from "../../i18n/index.js"
import { go, newWalkin, queue } from "../../store/index.js"
import { openApprovals, openReceive } from "../../store/storekeeper.js"
import IconTile from "../../components/IconTile.vue"

const storeKeeper = window.frappe.boot.is_store

function fleet() {
	queue.fetch()
	go("queue")
}
</script>

<template>
	<section class="home">
		<IconTile icon="fleet" :label="__('Etihad fleet maintenance')" :note="queue.data.length ? __('{0} vehicles waiting', [queue.data.length]) : ''" @press="fleet" />
		<IconTile icon="customer" :label="__('Customer maintenance')" @press="newWalkin" />
		<div v-if="storeKeeper" class="home-store">
			<IconTile icon="approvals" :label="__('Approvals')" @press="openApprovals" />
			<IconTile icon="item" :label="__('Spare parts')" @press="go('stock')" />
			<IconTile icon="receive" :label="__('Receive')" @press="openReceive" />
		</div>
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
.home-store {
	display: grid;
	grid-column: 1 / -1;
	grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
	gap: var(--s4);
}
.home .home-store .icon-tile {
	min-height: 9rem;
}
.home .icon-tile-label {
	font-size: var(--t-xl);
}
</style>
