export default function classicFallback() {
	return {
		name: "classic-fallback",
		apply: "build",
		transformIndexHtml: {
			order: "post",
			handler: (html) =>
				html.replace(/<script type="module" crossorigin src="([^"]+)"><\/script>/, (tag, src) => `${tag}\n\t\t<script nomodule defer src="${src}"></script>`),
		},
	}
}
