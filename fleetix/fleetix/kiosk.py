# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

KIOSK_PAGES = ("maintenance", "gate")


def revalidate_kiosk_pages(response, request):
	if response.mimetype == "text/html" and request.path.strip("/").split("/")[0] in KIOSK_PAGES:
		response.headers["Cache-Control"] = "no-cache"
