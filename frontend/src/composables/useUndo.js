import { reactive } from "vue"

const UNDO_MS = 6000

export const undoState = reactive({ message: "", revert: null })
let timer = null

export function clearUndo() {
	clearTimeout(timer)
	undoState.message = ""
	undoState.revert = null
}

export function offerUndo(message, revert) {
	clearTimeout(timer)
	undoState.message = message
	undoState.revert = revert
	timer = setTimeout(clearUndo, UNDO_MS)
}

export function runUndo() {
	const revert = undoState.revert
	clearUndo()
	if (revert) revert()
}
