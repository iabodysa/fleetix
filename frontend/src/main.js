import "./shell.js"
import { createApp, reactive } from "vue"
import { setConfig } from "frappe-ui/src/utils/config.js"
import { frappeRequest } from "frappe-ui/src/utils/frappeRequest.js"
import App from "./App.vue"
import { __ } from "./i18n/index.js"
import "./theme/tokens.css"
import "./theme/base.css"

const nativeFetch = window.fetch.bind(window)
window.fetch = (input, init) => nativeFetch(input, Object.assign({ credentials: "same-origin" }, init))

window.frappe.boot = reactive(window.frappe.boot)
setConfig("resourceFetcher", frappeRequest)

const app = createApp(App)
app.config.globalProperties.__ = __
app.mount("#app")

if ("serviceWorker" in navigator) {
	navigator.serviceWorker
		.register("/assets/fleetix/maintenance/sw.js", { scope: "/maintenance" })
		.catch(() => navigator.serviceWorker.register("/assets/fleetix/maintenance/sw.js"))
		.catch(() => null)
}
