import "../../frontend/src/shell.js"
import "../../frontend/compat/flex-gap.js"
import { createApp } from "vue"
import App from "./App.vue"
import { __, applyDirection, ensureLanguage } from "./i18n.js"
import "./style.css"

if (ensureLanguage()) {
	applyDirection()
	const app = createApp(App)
	app.config.globalProperties.__ = __
	app.mount("#app")
}
