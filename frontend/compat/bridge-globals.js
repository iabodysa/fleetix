if (typeof window.globalThis === "undefined") window.globalThis = window
if (!Object.fromEntries) {
	Object.fromEntries = (entries) => Array.from(entries).reduce((out, [key, value]) => ((out[key] = value), out), {})
}
