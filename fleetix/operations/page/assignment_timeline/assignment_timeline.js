frappe.pages["assignment-timeline"].on_page_load = (wrapper) => {
	frappe.require(["fleet.bundle.js", "fleet.bundle.css"], () => {
		const fx = fleetix.fleet;
		const DAY_MS = 86400000;

		class AssignmentTimeline extends fx.Shell {
			constructor() {
				super(wrapper, {
					route: "assignment-timeline",
					title: __("Assignment Timeline"),
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
							fieldname: "days",
							fieldtype: "Select",
							options: "7\n14\n31",
							default: "14",
							label: __("Days"),
						},
					],
				});
				this.$root.on("click", "[data-doc]", (e) => {
					e.stopPropagation();
					const [doctype, name] = e.currentTarget.dataset.doc.split("::");
					frappe.set_route("Form", doctype, name);
				});
				this.refresh();
			}

			refresh() {
				return frappe
					.call({
						method: "fleetix.operations.api.assignment_timeline.get_timeline",
						args: this.values(),
					})
					.then((r) => {
						this.data = r.message;
						this.render();
					});
			}

			render() {
				if (!this.data) return;
				const e = fx.esc;
				const { start, days, rows } = this.data;
				const t0 = moment(start).valueOf();
				const t1 = t0 + days * DAY_MS;
				const pos = (v) =>
					Math.min(100, Math.max(0, ((moment(v).valueOf() - t0) / (t1 - t0)) * 100));
				const now = pos(moment());
				const cols = `grid-template-columns:repeat(${days},1fr)`;
				const head = Array.from({ length: days }, (_, i) => {
					const d = moment(start).add(i, "days");
					return `<div class="${d.isSame(moment(), "day") ? "today" : ""}">${d.format(
						"D/M"
					)}</div>`;
				}).join("");
				const bar = (kind, from, to, label, doc) => {
					const a = pos(from);
					const b = to ? pos(to) : 100;
					if (b <= a && kind !== "late") return "";
					return `<div class="fx-span k-${kind}" style="inset-inline-start:${a}%;width:${Math.max(
						b - a,
						1.5
					)}%" ${doc ? `data-doc="${e(doc)}"` : ""}>${e(label || "")}</div>`;
				};
				const lines = rows.map((r) => {
					let track = "";
					r.spans.forEach((s) => {
						const doc = `${s.doctype}::${s.name}`;
						if (s.kind === "maintenance" || s.kind === "handover") {
							track += `<div class="fx-mark k-${
								s.kind
							}" style="inset-inline-start:${pos(s.start)}%" title="${e(
								__(s.label || s.doctype)
							)}" data-doc="${e(doc)}"></div>`;
						} else {
							track += bar(
								s.kind,
								s.start,
								s.end,
								s.label === r.project ? r.project_name || s.label : s.label,
								doc
							);
						}
					});
					if (r.state === "red" && r.due)
						track += bar("late", r.due, moment(), __("Late"));
					if (r.state === "black")
						track += bar(
							"idle",
							moment(start),
							null,
							__("Idle {0} days", [r.idle_days || 0])
						);
					return `<div class="fx-tl-line">
						<div class="fx-tl-label" data-open-doctype="Vehicle" data-open-name="${e(r.vehicle)}">${fx.lamp(
						r.state
					)}<bdi class="who" dir="ltr">${e(r.plate)}</bdi></div>
						<div class="fx-tl-track">${track}<div class="fx-tl-now" style="inset-inline-start:${now}%"></div></div>
					</div>`;
				});
				this.$body.html(`<div class="fx-tl"><div class="fx-tl-grid">
					<div class="fx-tl-head"><div class="fx-tl-label">${__(
						"Vehicle"
					)}</div><div class="fx-tl-days" style="${cols}">${head}</div></div>
					${lines.join("") || this.empty()}
				</div></div>`);
			}
		}

		wrapper.assignment_timeline = new AssignmentTimeline();
	});
};

frappe.pages["assignment-timeline"].on_page_show = (wrapper) =>
	wrapper.assignment_timeline?.refresh();
