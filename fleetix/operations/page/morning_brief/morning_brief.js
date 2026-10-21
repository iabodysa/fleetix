frappe.pages["morning-brief"].on_page_load = (wrapper) => {
	frappe.require(["fleet.bundle.js", "fleet.bundle.css"], () => {
		const fx = fleetix.fleet;

		class MorningBrief extends fx.Shell {
			constructor() {
				super(wrapper, { route: "morning-brief", title: __("Morning Brief") });
				this.$root.on("click", ".fx-lampbtn", () => frappe.set_route("fleet-board"));
				this.refresh();
			}

			refresh() {
				return frappe
					.call({ method: "fleetix.operations.api.morning_brief.get_brief" })
					.then((r) => {
						this.data = r.message;
						this.render();
					});
			}

			list(title, state, rows, cell) {
				const body = rows.length
					? rows
							.map(
								(
									r
								) => `<div class="fx-row" data-open-doctype="Vehicle" data-open-name="${fx.esc(
									r.vehicle
								)}">
								${fx.lamp(state || r.state)}<span class="grow"><bdi dir="ltr">${fx.esc(r.plate)}</bdi> · ${fx.esc(
									r.driver_name || r.city || ""
								)}</span>${cell(r)}</div>`
							)
							.join("")
					: `<div class="fx-row" style="cursor:default"><span class="grow meta">—</span></div>`;
				return `<div class="fx-card"><div class="fx-section" style="margin-block:0 6px">${__(
					title
				)}</div>${body}</div>`;
			}

			render() {
				if (!this.data) return;
				const d = this.data;
				const maxIdle = Math.max(1, ...d.idle.map((r) => r.idle_days || 0));
				const since = [
					["handovers", __("Handovers")],
					["maintenance", __("Maintenance")],
					["accidents", __("Accidents")],
					["requests", __("Vehicle Requests")],
				]
					.map(
						([k, l]) =>
							`<div class="fx-stat"><b>${d.since[k]}</b><span>${l}</span></div>`
					)
					.join("");
				this.$body.html(`
					<div class="fx-hero"><h3>${__("Good morning, {0}", [fx.esc(d.user)])}</h3>
						<span class="text-muted">${frappe.datetime.str_to_user(frappe.datetime.get_today())}</span></div>
					${this.ribbon(d.counts)}
					<div class="fx-cols">
						${this.list(
							__("First Three Things Today"),
							"red",
							d.first,
							(r) =>
								`<span class="num" style="color:var(--st-red)">${__("{0} h", [
									Math.round(r.late_hours || 0),
								])}</span>`
						)}
						${this.list(
							__("Periodic Maintenance Missed"),
							"gray",
							d.gray,
							(r) =>
								`<span class="meta">${fx.esc(
									r.reason
										.split(", ")
										.map((c) => __(c))
										.join("، ")
								)}</span>`
						)}
						${this.list(
							__("Longest Idle"),
							"black",
							d.idle,
							(r) =>
								`<span style="width:72px"><div class="fx-meter" style="width:${Math.round(
									((r.idle_days || 0) / maxIdle) * 100
								)}%"></div></span><span class="num">${r.idle_days || 0}</span>`
						)}
						${this.list(
							__("Expiring in 7 Days"),
							null,
							d.expiring,
							(r) => `<span class="num">${r.expiry_days}</span>`
						)}
						<div class="fx-card"><div class="fx-section" style="margin-block:0 6px">${__(
							"Since Yesterday"
						)}</div><div class="fx-stats">${since}</div></div>
					</div>`);
			}
		}

		wrapper.morning_brief = new MorningBrief();
	});
};

frappe.pages["morning-brief"].on_page_show = (wrapper) => wrapper.morning_brief?.refresh();
