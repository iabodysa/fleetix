frappe.pages["city-grid"].on_page_load = (wrapper) => {
	frappe.require(["fleet.bundle.js", "fleet.bundle.css"], () => {
		const fx = fleetix.fleet;

		class CityGrid extends fx.Shell {
			constructor() {
				super(wrapper, { route: "city-grid", title: __("City Grid") });
				this.$root.on("click", ".fx-lampbtn", (e) => {
					const state = e.currentTarget.dataset.state;
					this.state = this.state === state ? null : state;
					this.render();
				});
				this.$root.on("click", "[data-act=match]", (e) => {
					const { request, vehicle } = e.currentTarget.dataset;
					frappe.set_route("Form", "Vehicle Request", request).then(() => {
						if (
							cur_frm &&
							cur_frm.doc.name === request &&
							!cur_frm.doc.selected_vehicle
						) {
							cur_frm.set_value("selected_vehicle", vehicle);
						}
					});
				});
				this.refresh();
			}

			refresh() {
				return frappe
					.call({ method: "fleetix.fleetix.api.city_grid.get_city_grid" })
					.then((r) => {
						this.data = r.message;
						this.render();
					});
			}

			render() {
				if (!this.data) return;
				const e = fx.esc;
				let html = this.ribbon(this.data.counts, this.state);
				const cards = this.data.cities.map((c) => {
					const bar = fx.STATES.filter((s) => c.counts[s])
						.map(
							(s) => `<i style="flex:${c.counts[s]};background:var(--st-${s})"></i>`
						)
						.join("");
					const pixels = c.vehicles
						.filter((v) => !this.state || v.state === this.state)
						.map(
							(v) =>
								`<span class="fx-px s-${v.state}" title="${e(
									v.plate
								)}" data-open-doctype="Vehicle" data-open-name="${e(
									v.vehicle
								)}">${e(
									(String(v.plate).match(/\d+/) || [v.plate])[0].slice(-4)
								)}</span>`
						)
						.join("");
					const matches = c.matches
						.map(
							(m) => `<div class="fx-row">${fx.lamp("black")}<span class="grow">${e(
								m.plate
							)} · ${e(m.request)}</span>
								<span class="meta">${__("Idle {0} days", [m.idle_days || 0])}</span>
								<button class="fx-btn small" data-act="match" data-request="${e(m.request)}" data-vehicle="${e(
								m.vehicle
							)}">${__("Assign")}</button></div>`
						)
						.join("");
					return `<div class="fx-card">
						<div class="fx-row" style="cursor:default"><b class="grow">${e(
							c.city ? __(c.city) : __("No City")
						)}</b>
							<span class="fx-region">${e(__(c.region))}</span>
							<span class="fx-chip">${__("Waiting Requests")}: ${c.waiting.length}</span></div>
						<div class="fx-bar" style="margin-block:10px 4px">${bar}</div>
						<div class="fx-pixels">${pixels}</div>
						${matches}
					</div>`;
				});
				html += cards.length
					? `<div class="fx-cols">${cards.join("")}</div>`
					: this.empty();
				this.$body.html(html);
			}
		}

		wrapper.city_grid = new CityGrid();
	});
};

frappe.pages["city-grid"].on_page_show = (wrapper) => wrapper.city_grid?.refresh();
