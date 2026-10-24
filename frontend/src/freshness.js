const VERSION_URL = "/api/method/fleetix.fleetix.api.app_version.get_app_version"
const CHECK_MS = 60000

export function reloadOnNewVersion(idle) {
	const loaded = window.frappe && window.frappe.boot && window.frappe.boot.app_version
	if (!loaded) return
	let stale = false
	function check() {
		if (stale) return idle() && window.location.reload()
		fetch(VERSION_URL + "?_=" + Date.now(), { credentials: "same-origin", headers: { Accept: "application/json" } })
			.then((response) => (response.ok ? response.json() : null))
			.then((data) => {
				stale = !!(data && data.message && data.message !== loaded)
				if (stale && idle()) window.location.reload()
			})
			.catch(() => null)
	}
	window.setInterval(check, CHECK_MS)
	document.addEventListener("visibilitychange", () => document.hidden || check())
}
