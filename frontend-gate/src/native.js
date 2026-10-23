function plugin(name) {
	const capacitor = window.Capacitor
	if (!capacitor || !capacitor.isNativePlatform || !capacitor.isNativePlatform()) return null
	return (capacitor.Plugins && capacitor.Plugins[name]) || null
}

export function hasShell() {
	return !!plugin("Shell")
}

export function onShellBack(handler) {
	window.fleetixShell = { back: handler }
}

export async function openSettings() {
	const shell = plugin("Shell")
	if (shell) await shell.settings()
}

export async function hasCamera() {
	const shell = plugin("Shell")
	if (shell) return shell.hasCamera().then((result) => !!result.value).catch(() => false)
	if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return false
	try {
		const devices = await navigator.mediaDevices.enumerateDevices()
		return devices.some((device) => device.kind === "videoinput")
	} catch (e) {
		return false
	}
}
