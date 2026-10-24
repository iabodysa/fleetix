const VERSION_URL = "/api/method/fleetix.fleetix.api.app_version.get_app_version"
const VERSION_PARAM = "v"
const CHECK_MS = 60000

function openVersion(version) {
	const url = new URL(window.location.href)
	if (url.searchParams.get(VERSION_PARAM) === version) return
	url.searchParams.set(VERSION_PARAM, version)
	window.location.replace(url.toString())
}

export function reloadOnNewVersion(idle) {
	const loaded = window.frappe && window.frappe.boot && window.frappe.boot.app_version
	if (!loaded) return
	let live = null
	function check() {
		if (live) return idle() && openVersion(live)
		fetch(VERSION_URL + "?_=" + Date.now(), { credentials: "same-origin", headers: { Accept: "application/json" } })
			.then((response) => (response.ok ? response.json() : null))
			.then((data) => {
				live = data && data.message && data.message !== loaded ? data.message : null
				if (live && idle()) openVersion(live)
			})
			.catch(() => null)
	}
	check()
	window.setInterval(check, CHECK_MS)
	document.addEventListener("visibilitychange", () => document.hidden || check())
}
