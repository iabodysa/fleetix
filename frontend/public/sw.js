const CACHE = "fleetix-maintenance-assets"
const ASSET_PREFIX = "/assets/"

self.addEventListener("install", () => self.skipWaiting())
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()))
self.addEventListener("fetch", (event) => {
	const url = new URL(event.request.url)
	if (event.request.method !== "GET" || url.origin !== self.location.origin || url.pathname.indexOf(ASSET_PREFIX) !== 0) {
		return
	}
	event.respondWith(
		caches.open(CACHE).then((cache) =>
			cache.match(event.request).then(
				(cached) =>
					cached ||
					fetch(event.request).then((response) => {
						if (response.ok) cache.put(event.request, response.clone())
						return response
					})
			)
		)
	)
})
