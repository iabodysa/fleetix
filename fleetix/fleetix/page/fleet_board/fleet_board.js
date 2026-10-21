frappe.pages["fleet-board"].on_page_load = (wrapper) => {
	frappe.require(["fleet.bundle.js", "fleet.bundle.css"], () => {
		const fx = fleetix.fleet;
		const REASON = {
			return_due: (r) => __("Return due {0}", [fleetix.fleet.when(r.due)]),
			deliver_due: (r) => __("Delivery due {0}", [fleetix.fleet.when(r.due, false)]),
			open_note: () => __("Open accident or damage"),
		};

		class FleetBoard extends fx.Shell {
			constructor() {
				super(wrapper, {
					route: "fleet-board",
					title: __("Fleet Board"),
					filters: [
						{
							fieldname: "project",
							fieldtype: "Link",
							options: "Project",
							label: __("Project"),
						},
						{
							fieldname: "city",
							fieldtype: "Link",
							options: "City",
							label: __("City"),
						},
						{
							fieldname: "q",
							fieldtype: "Data",
							label: __("Plate or Driver"),
							local: true,
						},
					],
				});
				this.$root.on("click", ".fx-lampbtn", (e) => {
					const state = e.currentTarget.dataset.state;
					this.state = this.state === state ? null : state;
					this.render();
				});
				this.$root.on("click", "[data-act]", (e) => this.act(e));
				this.refresh();
			}

			refresh() {
				const { q, ...args } = this.values();
				return frappe
					.call({ method: "fleetix.fleetix.api.fleet_board.get_board", args })
					.then((r) => {
						this.data = r.message;
						this.render();
					});
			}

			render() {
				if (!this.data) return;
				const q = (this.fields.q.get_value() || "").toLowerCase();
				const rows = this.data.rows.filter(
					(r) =>
						(!this.state || r.state === this.state) &&
						(!q ||
							[r.plate, r.vehicle, r.driver_name, r.project_name]
								.join(" ")
								.toLowerCase()
								.includes(q))
				);
				this.byName = Object.fromEntries(this.data.rows.map((r) => [r.vehicle, r]));
				let html = this.ribbon(this.data.counts, this.state);
				fx.STATES.forEach((state) => {
					const group = rows.filter((r) => r.state === state);
					if (!group.length) return;
					html += this.section(state, group.length);
					html +=
						state === "red"
							? `<div class="fx-lane">${group
									.map((r) => this.redCard(r))
									.join("")}</div>`
							: `<div class="fx-grid">${group
									.map((r) => this.tile(r))
									.join("")}</div>`;
				});
				if (!rows.length) html += this.empty();
				this.$body.html(html);
			}

			redCard(r) {
				const e = fx.esc;
				const main = {
					return_due: ["return", __("Record Return")],
					deliver_due: ["request", __("Open Request")],
					open_note: ["note", __("Open Note")],
				}[r.reason];
				const call = r.phone
					? `<a class="fx-btn" data-act="call" href="tel:${e(r.phone)}">${__(
							"Call Driver"
					  )}</a>`
					: "";
				return `<div class="fx-rcard" data-open-doctype="Vehicle" data-open-name="${e(
					r.vehicle
				)}">
					${fx.plate(r.plate)}
					<div class="info">
						<div class="who">${e(r.driver_name || r.model || r.vehicle)}</div>
						<div class="meta">${e([r.project_name, r.city].filter(Boolean).join(" · "))}</div>
						<div class="meta">${e(REASON[r.reason](r))}</div>
						${fx.chips(r.chips, r)}
					</div>
					<div class="late">${r.reason === "open_note" ? "" : fx.late(r.late_hours)}</div>
					<div class="acts"><button class="fx-btn primary" data-act="${main[0]}" data-vehicle="${e(
					r.vehicle
				)}">${main[1]}</button>${call}</div>
				</div>`;
			}

			tile(r) {
				const e = fx.esc;
				let meta = [r.project_name, r.city].filter(Boolean).join(" · ");
				let act = "";
				if (r.state === "gray") {
					meta = r.reason
						.split(", ")
						.map((c) => __(c))
						.join("، ");
					act = `<button class="fx-btn small" data-act="maintenance" data-vehicle="${e(
						r.vehicle
					)}">${__("Book Maintenance")}</button>`;
				} else if (r.state === "black") {
					meta = [__("Idle {0} days", [r.idle_days || 0]), r.city]
						.filter(Boolean)
						.join(" · ");
					act = `<button class="fx-btn small" data-act="assign" data-vehicle="${e(
						r.vehicle
					)}">${__("Assign")}</button>`;
				}
				return `<div class="fx-tile t-${
					r.state
				}" data-open-doctype="Vehicle" data-open-name="${e(r.vehicle)}">
					${fx.plate(r.plate)}
					<div class="head">${fx.lamp(r.state)}<span class="who">${e(
					r.driver_name || r.model || r.vehicle
				)}</span></div>
					<div class="meta">${e(meta)}</div>
					${fx.chips(r.chips, r)}${act}
				</div>`;
			}

			act(e) {
				const el = e.currentTarget;
				if (el.dataset.act === "call") return;
				e.preventDefault();
				const r = this.byName[el.dataset.vehicle];
				const actions = {
					return: () =>
						frappe.new_doc("Vehicle Handover", {
							vehicle: r.vehicle,
							handover_type: "Return",
							from_driver: r.driver,
							from_project: r.project,
						}),
					request: () => frappe.set_route("Form", r.ref_doctype, r.ref_name),
					note: () => frappe.set_route("Form", r.notes[0].doctype, r.notes[0].name),
					maintenance: () =>
						r.ref_name
							? frappe.set_route("Form", "Maintenance", r.ref_name)
							: frappe.new_doc("Maintenance", {
									vehicle: r.vehicle,
									maintenance_type: "Periodic",
							  }),
					assign: () => frappe.new_doc("Vehicle Assignment", { vehicle: r.vehicle }),
				};
				actions[el.dataset.act]();
			}
		}

		wrapper.fleet_board = new FleetBoard();
	});
};

frappe.pages["fleet-board"].on_page_show = (wrapper) => wrapper.fleet_board?.refresh();
