import { computed } from "vue"
import { useCardProgress } from "./useCardProgress.js"

export function useFinalCheck(checks, findings) {
	const cards = computed(() => checks.map((row) => ({ key: row.kind + row.item, label: row.label, icon: row.kind === "part" ? row.icon || "item" : "review", done: !!row.condition })))
	const progress = useCardProgress(cards)
	const open = computed(() => progress.missing.value.length)
	const parts = computed(() => checks.map((row) => ({ key: row.item, label: row.label })))

	function answer(row, condition) {
		row.condition = condition
		const auto = findings.findIndex((f) => f.part === row.item && f.reason === "Not Done")
		if (condition === "Not Done" && auto === -1) findings.push({ part: row.item, reason: "Not Done", note: "" })
		if (condition !== "Not Done" && auto !== -1) findings.splice(auto, 1)
	}
	function answers() {
		return checks.map((row) => ({ item: row.item, condition: row.condition }))
	}
	return { cards, progress, open, parts, answer, answers }
}
