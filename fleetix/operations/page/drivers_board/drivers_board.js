frappe.pages["drivers-board"].on_page_load = (wrapper) => {
	frappe.require(["fleet.bundle.js", "fleet.bundle.css"], () => {
		const fx = fleetix.fleet;
		const LABELS = {
			red: __("Vehicle Due Back"),
			gray: __("Training Not Done"),
			black: __("Trained, No Vehicle"),
			green: __("On Duty"),
		};

		class DriversBoard extends fx.Shell {
			constructor() {
				super(wrapper, {
					route: "drivers-board",
					title: __("Drivers Board"),
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
							label: __("Driver or Plate"),
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
					.call({ method: "fleetix.operations.api.drivers_board.get_drivers", args })
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
						(!q || [r.name, r.plate, r.driver].join(" ").toLowerCase().includes(q))
				);
				this.byName = Object.fromEntries(this.data.rows.map((r) => [r.driver, r]));
				let html = this.ribbon(this.data.counts, this.state, LABELS);
				fx.STATES.forEach((state) => {
					const group = rows.filter((r) => r.state === state);
					if (!group.length) return;
					html += this.section(state, group.length, LABELS);
					html +=
						state === "red"
							? `<div class="fx-lane">${group
									.map((r) => this.redCard(r))
									.join("")}</div>`
							: `<div class="fx-grid">${group
									.map((r) => this.tile(r))
									.join("")}</div>`;
				});
				if (!rows.length) html += `<div class="fx-empty">${__("No drivers")}</div>`;
				this.$body.html(html);
			}

			redCard(r) {
				const e = fx.esc;
				const call = r.phone
					? `<a class="fx-btn" data-act="call" href="tel:${e(r.phone)}">${__(
							"Call Driver"
					  )}</a>`
					: "";
				return `<div class="fx-rcard" data-open-doctype="Driver" data-open-name="${e(
					r.driver
				)}">
					${fx.plate(r.plate)}
					<div class="info">
						<div class="who">${e(r.name)}</div>
						<div class="meta">${e([r.project_name, r.city].filter(Boolean).join(" · "))}</div>
						<div class="meta">${e(__("Return due {0}", [fx.when(r.due)]))}</div>
					</div>
					<div class="late">${fx.late(r.late_hours)}</div>
					<div class="acts"><button class="fx-btn primary" data-act="return" data-driver="${e(
						r.driver
					)}">${__("Record Return")}</button>${call}</div>
				</div>`;
			}

			tile(r) {
				const e = fx.esc;
				let meta = [r.project_name, r.city].filter(Boolean).join(" · ");
				let act = "";
				if (r.state === "gray") meta = __(r.reason);
				if (r.state === "black") {
					act = `<button class="fx-btn small" data-act="assign" data-driver="${e(
						r.driver
					)}">${__("Assign")}</button>`;
				}
				return `<div class="fx-tile t-${
					r.state
				}" data-open-doctype="Driver" data-open-name="${e(r.driver)}">
					<div class="head">${fx.lamp(r.state)}<span class="who">${e(r.name)}</span></div>
					${r.plate ? fx.plate(r.plate) : ""}
					<div class="meta">${e(meta)}</div>${act}
				</div>`;
			}

			act(e) {
				const el = e.currentTarget;
				if (el.dataset.act === "call") return;
				e.preventDefault();
				const r = this.byName[el.dataset.driver];
				if (el.dataset.act === "return") {
					frappe.new_doc("Vehicle Handover", {
						vehicle: r.vehicle,
						handover_type: "Return",
						from_driver: r.driver,
						from_project: r.project,
					});
				} else {
					frappe.new_doc("Vehicle Assignment", { driver: r.driver });
				}
			}
		}

		wrapper.drivers_board = new DriversBoard();
	});
};

frappe.pages["drivers-board"].on_page_show = (wrapper) => wrapper.drivers_board?.refresh();
