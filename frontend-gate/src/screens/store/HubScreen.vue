<script setup>
import { __ } from "../../i18n.js"
import { openStore } from "../../storekeeper.js"
import BigButton from "../../components/BigButton.vue"
</script>

<template>
	<div class="page">
		<div class="screen">
			<h1 class="screen-title">{{ __("Store") }}</h1>
			<BigButton icon="check" tone="soft" :label="__('Approvals')" @press="openStore('approvals')" />
			<BigButton icon="box" tone="soft" :label="__('Spare parts')" @press="openStore('parts')" />
			<BigButton icon="plus" tone="soft" :label="__('Receive')" @press="openStore('receive')" />
		</div>
	</div>
</template>
