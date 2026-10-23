frappe.provide("fleetix.fleet");

const STATES = ["red", "black", "gray", "suspended", "maintenance", "green"];
const REFRESH_MS = 60 * 1000;
const PLATE_LETTERS = {
	A: "ا",
	B: "ب",
	J: "ح",
	D: "د",
	R: "ر",
	S: "س",
	X: "ص",
	T: "ط",
	E: "ع",
	G: "ق",
	K: "ك",
	L: "ل",
	Z: "م",
	N: "ن",
	H: "هـ",
	U: "و",
	V: "ى",
};
const ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩";
const ICONS = {
	"fleet-board":
		'<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
	"drivers-board": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
	"assignment-timeline":
		'<path d="M3 6h12M3 12h18M3 18h8"/><circle cx="18" cy="6" r="2"/><circle cx="14" cy="18" r="2"/>',
	"city-grid": '<path d="M4 21V9l5-3v15M9 21V4l6 3v14M15 21v-9l5 2v7M2 21h20"/>',
	"morning-brief":
		'<circle cx="12" cy="14" r="4"/><path d="M12 3v3M4.2 7.2l2 2M19.8 7.2l-2 2M2 18h20M6 21h12"/>',
};

fleetix.fleet.STATES = STATES;
fleetix.fleet.TABS = [
	{ route: "fleet-board", label: __("Board") },
	{ route: "drivers-board", label: __("Drivers") },
	{ route: "assignment-timeline", label: __("Timeline") },
	{ route: "city-grid", label: __("Cities") },
	{ route: "morning-brief", label: __("Brief") },
];
fleetix.fleet.STATE_LABELS = {
	red: __("Due for Handover"),
	gray: __("Periodic Maintenance Missed"),
	black: __("Idle, No Assignment"),
	suspended: __("Suspended"),
	maintenance: __("In Maintenance"),
	green: __("All Clear"),
};

fleetix.fleet.esc = (value) => frappe.utils.escape_html(value == null ? "" : String(value));

fleetix.fleet.plate = (text, state) => {
	const raw = String(text || "")
		.toUpperCase()
		.trim();
	const digits = (raw.match(/\d+/) || [""])[0];
	const letters = raw.replace(/[^A-Z]/g, "").split("");
	const arLetters = letters.map((c) => PLATE_LETTERS[c] || c).join(" ");
	const arDigits = digits.replace(/\d/g, (d) => ARABIC_DIGITS[d]);
	const esc = fleetix.fleet.esc;
	const top = letters.length
		? `<div class="pl-row ar"><span>${esc(
				arDigits
		  )}</span><span class="sep"></span><span dir="rtl">${esc(arLetters)}</span></div>`
		: "";
	const bottom = letters.length
		? `<div class="pl-row en"><span>${esc(digits)}</span><span class="sep"></span><span>${esc(
				letters.join(" ")
		  )}</span></div>`
		: `<div class="pl-row en" style="grid-template-columns:1fr"><span>${esc(
				raw
		  )}</span></div>`;
	return `<div class="plate"><div class="pl-body">${top}${bottom}</div><div class="pl-strip">KSA</div></div>`;
};

fleetix.fleet.when = (value, withTime = true) =>
	value ? `\u2066${moment(value).format(withTime ? "D/M HH:mm" : "D/M")}\u2069` : "";

fleetix.fleet.lamp = (state) => `<span class="lamp l-${state}"></span>`;

fleetix.fleet.chips = (chips, row) => {
	const label = {
		workshop: __("In Workshop"),
		training: __("Training"),
		suspended: __("Suspended"),
		note: __("Open Note"),
		expiry: row && row.expiry_days != null ? __("Expires in {0} days", [row.expiry_days]) : "",
	};
	if (!chips || !chips.length) return "";
	return `<div class="fx-chips">${chips
		.map((c) => `<span class="fx-chip">${fleetix.fleet.esc(label[c] || __(c))}</span>`)
		.join("")}</div>`;
};

fleetix.fleet.late = (hours) => {
	const h = Math.abs(hours || 0);
	const big = h >= 48 ? Math.round(h / 24) : Math.round(h);
	let unit;
	if (hours >= 0) unit = h >= 48 ? __("days late") : __("hours late");
	else unit = __("hours left");
	return `<b>${big}</b><small>${unit}</small>`;
};

fleetix.fleet.Shell = class Shell {
	constructor(wrapper, { route, title, filters = [] }) {
		this.route = route;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __(title),
			single_column: true,
		});
		$(wrapper).addClass("fx-page");
		this.page.set_secondary_action(__("Refresh"), () => this.refresh(), "refresh");
		this.fields = {};
		filters.forEach((df) => {
			this.fields[df.fieldname] = this.page.add_field({
				...df,
				change: () => (df.local ? this.render() : this.refresh()),
			});
		});
		this.$root = $(`<div class="fx"><div class="fx-body"></div>${this.tabs()}</div>`).appendTo(
			this.page.main
		);
		this.$body = this.$root.find(".fx-body");
		this.$root.on("click", "[data-open-doctype]", (e) => {
			if ($(e.target).closest("[data-act]").length) return;
			const el = e.currentTarget;
			frappe.set_route("Form", el.dataset.openDoctype, el.dataset.openName);
		});
		this.timer = setInterval(() => {
			if (document.visibilityState === "visible" && frappe.get_route()[0] === this.route)
				this.refresh();
		}, REFRESH_MS);
	}

	values() {
		const out = {};
		Object.entries(this.fields).forEach(([key, field]) => {
			const value = field.get_value();
			if (value) out[key] = value;
		});
		return out;
	}

	tabs() {
		return `<nav class="fx-tabs">${fleetix.fleet.TABS.map(
			(t) => `<a class="fx-tab ${t.route === this.route ? "active" : ""}" href="/app/${
				t.route
			}">
				<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${
					ICONS[t.route]
				}</svg>
				<span>${t.label}</span></a>`
		).join("")}</nav>`;
	}

	ribbon(counts, active, labels = fleetix.fleet.STATE_LABELS) {
		const shown = STATES.filter((s) => s in labels);
		const total = shown.reduce((sum, s) => sum + (counts[s] || 0), 0);
		const bar = shown.filter((s) => counts[s])
			.map((s) => `<i style="flex:${counts[s]};background:var(--st-${s})"></i>`)
			.join("");
		const lamps = shown.map(
			(s) => `<button class="fx-lampbtn s-${s} ${
				active === s ? "active" : ""
			}" data-state="${s}">
				${fleetix.fleet.lamp(s)}<b>${counts[s] || 0}</b><span>${labels[s]}</span></button>`
		).join("");
		return `<div class="fx-ribbon" data-total="${total}"><div class="fx-bar">${bar}</div><div class="fx-lamps">${lamps}</div></div>`;
	}

	section(state, count, labels = fleetix.fleet.STATE_LABELS) {
		return `<div class="fx-section">${fleetix.fleet.lamp(state)}<span>${__(
			labels[state]
		)}</span><small>${count}</small></div>`;
	}

	empty() {
		return `<div class="fx-empty">${__("No vehicles")}</div>`;
	}
};
