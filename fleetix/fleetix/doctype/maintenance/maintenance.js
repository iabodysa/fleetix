// Copyright (c) 2026, Ittihad and contributors
// For license information, please see license.txt

const PHOTOSWIPE_ASSETS = [
	"assets/frappe/js/lib/photoswipe/photoswipe.css",
	"assets/frappe/js/lib/photoswipe/default-skin.css",
	"assets/frappe/js/lib/photoswipe/photoswipe.js",
	"assets/frappe/js/lib/photoswipe/photoswipe-ui-default.js",
];

frappe.ui.form.on("Maintenance", {
	refresh(frm) {
		fleetix.vehicle_type.show(frm, "vehicle");
		render_photo_gallery(frm);
	},
	vehicle(frm) {
		fleetix.vehicle_type.show(frm, "vehicle");
	},
});

function photo_groups(frm) {
	const groups = new Map();
	for (const row of frm.doc.photos || []) {
		if (!row.attachment) continue;
		const key = row.slot || row.caption || row.attachment;
		if (!groups.has(key)) groups.set(key, { caption: row.caption || row.slot || "", urls: [] });
		groups.get(key).urls.push(row.attachment);
	}
	return [...groups.values()];
}

function render_photo_gallery(frm) {
	const field = frm.get_field("photo_gallery");
	if (!field) return;
	const items = [];
	const $grid = $('<div class="mnt-gallery"></div>');
	for (const group of photo_groups(frm)) {
		const index = items.length;
		for (const url of group.urls) items.push({ src: url, title: frappe.utils.escape_html(group.caption) });
		const $tile = $('<button type="button" class="mnt-gallery-tile"></button>').appendTo($grid);
		$('<img loading="lazy">').attr({ src: group.urls[0], alt: group.caption }).appendTo($tile);
		$('<span class="mnt-gallery-caption"></span>').text(group.caption).appendTo($tile);
		if (group.urls.length > 1) {
			$('<span class="mnt-gallery-count"></span>').text(group.urls.length).appendTo($tile);
		}
		$tile.on("click", () => open_lightbox(items, index));
	}
	field.$wrapper.empty().append($grid);
}

function image_size(item) {
	return new Promise((resolve) => {
		const image = new Image();
		image.onload = () => resolve({ ...item, w: image.naturalWidth, h: image.naturalHeight });
		image.onerror = () => resolve({ ...item, w: 1600, h: 1200 });
		image.src = item.src;
	});
}

function photoswipe_root() {
	if (!$("body > .pswp").length) $("body").append(frappe.render_template("photoswipe_dom"));
	return $("body > .pswp").get(0);
}

function open_lightbox(items, index) {
	frappe.require(PHOTOSWIPE_ASSETS, async () => {
		const sized = await Promise.all(items.map(image_size));
		const gallery = new PhotoSwipe(photoswipe_root(), PhotoSwipeUI_Default, sized, {
			index,
			history: false,
			shareEl: false,
			closeOnScroll: false,
		});
		gallery.init();
	});
}
