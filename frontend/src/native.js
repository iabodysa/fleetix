import { __, componentLabel, formatKm, isolate } from "./i18n/index.js"

function plugin(name) {
	const capacitor = window.Capacitor
	if (!capacitor || !capacitor.isNativePlatform || !capacitor.isNativePlatform()) return null
	return (capacitor.Plugins && capacitor.Plugins[name]) || null
}

const PRINTER_ERRORS = {
	OutOfPaper: __("Out of paper"),
	CoverIsOpen: __("Printer cover is open"),
	Overheated: __("Printer is overheated"),
	PrinterNotDetected: __("Printer not found"),
}

export function hasPrinter() {
	return !!plugin("SunmiPrinter")
}

export function hasCustomerDisplay() {
	return !!plugin("CustomerDisplay")
}

export function hasShell() {
	return !!plugin("Shell")
}

export function onShellBack(handler) {
	window.fleetixShell = { back: handler }
}

export function showStepOnCustomerDisplay(plate, step) {
	const display = plugin("CustomerDisplay")
	if (!display) return
	const call = plate ? display.step({ plate, step }) : display.idle()
	call.catch(() => null)
}

export function dueText(row) {
	if (row.due_km) return formatKm(row.due_km)
	if (row.due_date) return isolate(row.due_date)
	return "-"
}

export async function showOnCustomerDisplay(plate, status, nextDue) {
	const display = plugin("CustomerDisplay")
	if (!display) return false
	await display.show({
		plate,
		status,
		title: __("Next service"),
		rows: (nextDue || []).map((row) => ({ label: componentLabel(row.component), value: dueText(row) })),
	})
	return true
}

export function receiptCanvas(result) {
	const width = 576
	const lines = [
		{ text: __("Fleetix Maintenance"), size: 40, bold: true },
		{ text: result.maintenance, size: 26 },
		{ text: result.plate + "  " + (result.model || ""), size: 30, bold: true },
		{ text: __("Odometer") + ": " + formatKm(result.odometer), size: 26 },
		{ text: __("Date") + ": " + isolate(result.visit_date), size: 26 },
		{ rule: true },
		{ text: __("Next service"), size: 30, bold: true },
	]
	result.next_due.forEach((row) => {
		lines.push({ text: (row.replaced ? "* " : "") + componentLabel(row.component) + ": " + dueText(row), size: 26, bold: row.replaced })
	})
	lines.push({ rule: true }, { text: "* " + __("Replaced today"), size: 22 })
	const canvas = document.createElement("canvas")
	canvas.width = width
	canvas.height = lines.reduce((sum, line) => sum + (line.rule ? 24 : line.size + 18), 40)
	const ctx = canvas.getContext("2d")
	ctx.fillStyle = "#FFFFFF"
	ctx.fillRect(0, 0, width, canvas.height)
	ctx.fillStyle = "#000000"
	ctx.textAlign = "right"
	ctx.textBaseline = "top"
	let y = 20
	lines.forEach((line) => {
		if (line.rule) {
			ctx.fillRect(16, y + 10, width - 32, 2)
			y += 24
			return
		}
		ctx.font = (line.bold ? "bold " : "") + line.size + "px sans-serif"
		ctx.fillText(line.text, width - 16, y)
		y += line.size + 18
	})
	return canvas
}

export async function printReceipt(result) {
	const printer = plugin("SunmiPrinter")
	if (!printer) return false
	const state = await printer.updatePrinterState().catch(() => null)
	if (state && state.status !== "NormalOperation") throw new Error(PRINTER_ERRORS[state.status] || __("Printer error"))
	const bitmap = receiptCanvas(result).toDataURL("image/png").split(",")[1]
	await printer.printerInit()
	await printer.printBitmapCustom({ bitmap, type: 2 })
	await printer.lineWrap({ lines: 3 })
	await printer.cutPaper().catch(() => null)
	return true
}

export async function openSettings() {
	const shell = plugin("Shell")
	if (shell) await shell.settings()
}
