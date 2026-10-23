const FLEX = /^(inline-)?flex$/
const COLUMN = /^column/

function value(rule, prop) {
	let found = ""
	rule.walkDecls(prop, (decl) => {
		found = decl.value.trim()
	})
	return found
}

function fallback(rule, scope, prop, size) {
	const selector = rule.selectors.map((s) => `html.no-flex-gap${scope} ${s} > :not(:last-child)`).join(",\n")
	rule.after(rule.clone({ selector, nodes: [] }).append({ prop, value: size }))
}

export default function flexGapFallback() {
	return {
		postcssPlugin: "flex-gap-fallback",
		Rule(rule) {
			const gap = value(rule, "gap")
			if (!gap || value(rule, "grid-gap")) return
			rule.walkDecls("gap", (decl) => {
				decl.cloneBefore({ prop: "grid-gap" })
			})
			if (!FLEX.test(value(rule, "display"))) return
			const sizes = gap.split(/\s+(?![^(]*\))/)
			const column = sizes[1] || sizes[0]
			if (COLUMN.test(value(rule, "flex-direction"))) {
				fallback(rule, "", "margin-bottom", sizes[0])
				return
			}
			fallback(rule, '[dir="ltr"]', "margin-right", column)
			fallback(rule, '[dir="rtl"]', "margin-left", column)
		},
	}
}
flexGapFallback.postcss = true
