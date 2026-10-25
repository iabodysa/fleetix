<script setup>
import AppIcon from "../../components/AppIcon.vue"

defineProps({ busy: Boolean })
</script>

<template>
	<section class="badge-screen">
		<div class="card badge-card" :class="{ 'badge-busy': busy }">
			<span class="badge-mark"><AppIcon name="scan" size="lg" /></span>
			<h2 class="badge-title">{{ __("Scan your badge") }}</h2>
		</div>
	</section>
</template>

<style>
.badge-screen {
	display: flex;
	flex: 1;
	align-items: center;
	justify-content: center;
	min-height: 60vh;
}
.badge-card {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: var(--s4);
	width: min(32rem, 100%);
	padding: var(--s6) var(--s4);
	border: 2px dashed var(--done);
	text-align: center;
}
.badge-mark {
	display: inline-flex;
	color: var(--done);
	transform: scale(2);
	margin: var(--s4);
	animation: barcode-input-pulse 1.6s ease-in-out infinite;
}
.badge-busy .badge-mark {
	animation: none;
	opacity: 0.5;
}
.badge-title {
	font-size: var(--t-lg);
	font-weight: 800;
}
</style>
