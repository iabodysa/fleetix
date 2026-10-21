function __(text) {
	return (window.TRANSLATIONS && window.TRANSLATIONS[text]) || text
}

var DEFAULT_URL = "http://fleetix15.localhost:8004"
var plugins = (window.Capacitor && window.Capacitor.Plugins) || {}

document.getElementById("title").textContent = __("Fleetix Maintenance")
document.getElementById("url-label").textContent = __("Server address")
document.getElementById("save").textContent = __("Save")
document.getElementById("url").value = DEFAULT_URL

document.getElementById("config").addEventListener("submit", function (event) {
	event.preventDefault()
	var url = document.getElementById("url").value.replace(/\/+$/, "")
	if (!/^https?:\/\/[^/]+$/.test(url)) {
		document.getElementById("error").textContent = __("Server address")
		return
	}
	plugins.ServerConfig.set({ url: url })
})
