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

function dataUrl(src) {
	return fetch(src, { credentials: "same-origin" })
		.then((response) => response.blob())
		.then(
			(blob) =>
				new Promise((resolve) => {
					const reader = new FileReader()
					reader.onload = () => resolve(reader.result)
					reader.readAsDataURL(blob)
				})
		)
}

function loadImage(src) {
	return new Promise((resolve, reject) => {
		const image = new Image()
		image.onload = () => resolve(image)
		image.onerror = () => reject(new Error(__("Printer error")))
		image.src = src
	})
}

export async function formatCanvas(html) {
	const width = 576
	const holder = document.createElement("div")
	holder.style.cssText = "position:fixed;left:-10000px;top:0;background:#FFFFFF"
	holder.innerHTML = html
	document.body.appendChild(holder)
	try {
		const images = Array.prototype.slice.call(holder.querySelectorAll("img"))
		await Promise.all(
			images
				.filter((img) => (img.getAttribute("src") || "").indexOf("data:") !== 0)
				.map((img) => dataUrl(img.src).then((src) => img.setAttribute("src", src)))
		)
		const page = holder.querySelector(".tp") || holder
		const cssWidth = page.offsetWidth
		const cssHeight = holder.scrollHeight
		const scale = width / cssWidth
		const body = new XMLSerializer().serializeToString(holder)
		const svg =
			'<svg xmlns="http://www.w3.org/2000/svg" width="' + width + '" height="' + Math.ceil(cssHeight * scale) + '" viewBox="0 0 ' + cssWidth + " " + cssHeight + '">' +
			'<foreignObject x="0" y="0" width="' + cssWidth + '" height="' + cssHeight + '">' + body + "</foreignObject></svg>"
		const image = await loadImage("data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg))
		const canvas = document.createElement("canvas")
		canvas.width = width
		canvas.height = Math.ceil(cssHeight * scale)
		const ctx = canvas.getContext("2d")
		ctx.fillStyle = "#FFFFFF"
		ctx.fillRect(0, 0, canvas.width, canvas.height)
		ctx.drawImage(image, 0, 0, canvas.width, canvas.height)
		const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height)
		const data = pixels.data
		for (let i = 0; i < data.length; i += 4) {
			const ink = data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114 < 150 ? 0 : 255
			data[i] = data[i + 1] = data[i + 2] = ink
			data[i + 3] = 255
		}
		ctx.putImageData(pixels, 0, 0)
		return canvas
	} finally {
		document.body.removeChild(holder)
	}
}

export async function printDocument(doctype, name, format) {
	const printer = plugin("SunmiPrinter")
	if (!printer) return false
	const page = await call("frappe.www.printview.get_html_and_style", { doc: doctype, name, print_format: format, no_letterhead: 1 })
	return printCanvas(printer, await formatCanvas(page.html))
}

export async function printSample(sample) {
	const printer = plugin("SunmiPrinter")
	if (!printer) return false
	const page = await call("frappe.www.printview.get_html_and_style", { doc: JSON.stringify(sample.doc), print_format: sample.format, no_letterhead: 1 })
	return printCanvas(printer, await formatCanvas(page.html))
}

export async function printReceipt(result) {
	const printer = plugin("SunmiPrinter")
	if (!printer) return false
	return printCanvas(printer, receiptCanvas(result))
}

async function printCanvas(printer, canvas) {
	const state = await printer.updatePrinterState().catch(() => null)
	if (state && state.status !== "NormalOperation") throw new Error(PRINTER_ERRORS[state.status] || __("Printer error"))
	const bitmap = canvas.toDataURL("image/png").split(",")[1]
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
