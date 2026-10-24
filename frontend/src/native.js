import call from "frappe-ui/src/utils/call.js"
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

export function showStepOnCustomerDisplay(plate, step, card) {
	const display = plugin("CustomerDisplay")
	if (!display) return
	const call = plate ? display.step({ plate, step, delegate: (card && card.delegate) || "", qr: (card && card.qr) || [] }) : display.idle()
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

const P = "fleetix.fleetix.api.thermal_print."

export function printImage(doctype, name, format) {
	return call(P + "get_print_image", { doctype, name, print_format: format })
}

export async function printBitmap(bitmap) {
	const printer = plugin("SunmiPrinter")
	if (!printer) return false
	const state = await printer.updatePrinterState().catch(() => null)
	if (state && state.status !== "NormalOperation") throw new Error(PRINTER_ERRORS[state.status] || __("Printer error"))
	await printer.printerInit()
	await printer.printBitmapCustom({ bitmap, type: "Default" })
	await printer.lineWrap({ lines: 3 })
	await printer.cutPaper().catch(() => null)
	return true
}

export async function printDocument(doctype, name, format) {
	if (!hasPrinter()) return false
	return printBitmap(await printImage(doctype, name, format))
}

export function sampleImage(sample) {
	return call(P + "get_sample_image", { label: sample.label })
}

export function imageStats(bitmap) {
	return new Promise((resolve) => {
		const image = new Image()
		image.onload = () => {
			const canvas = document.createElement("canvas")
			canvas.width = image.width
			canvas.height = image.height
			const context = canvas.getContext("2d")
			context.drawImage(image, 0, 0)
			const pixels = context.getImageData(0, 0, image.width, image.height).data
			let ink = 0
			for (let i = 0; i < pixels.length; i += 4) if (pixels[i] < 128 && pixels[i + 3] > 127) ink++
			resolve({ width: image.width, height: image.height, kb: Math.round((bitmap.length * 3) / 4096), ink: ((100 * ink) / (image.width * image.height)).toFixed(1) })
		}
		image.onerror = () => resolve(null)
		image.src = "data:image/png;base64," + bitmap
	})
}

export async function openSettings() {
	const shell = plugin("Shell")
	if (shell) await shell.settings()
}
