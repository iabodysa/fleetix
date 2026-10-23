import { createApp, reactive } from "vue"
import { setConfig } from "frappe-ui/src/utils/config.js"
import { frappeRequest } from "frappe-ui/src/utils/frappeRequest.js"
import App from "./App.vue"
import { __ } from "./translate.js"
import "./style.css"

const nativeFetch = window.fetch.bind(window)
window.fetch = (input, init) => nativeFetch(input, Object.assign({ credentials: "same-origin" }, init))

window.frappe.boot = reactive(window.frappe.boot)
setConfig("resourceFetcher", frappeRequest)
document.documentElement.lang = (window.frappe.boot && window.frappe.boot.lang) || "ar"

const app = createApp(App)
app.config.globalProperties.__ = __
app.mount("#app")

if ("serviceWorker" in navigator) {
	navigator.serviceWorker
		.register("/assets/fleetix/maintenance/sw.js", { scope: "/maintenance" })
		.catch(() => navigator.serviceWorker.register("/assets/fleetix/maintenance/sw.js"))
		.catch(() => null)
}
