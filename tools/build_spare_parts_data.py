#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA_FILE = REPO / "fleetix" / "fleetix" / "stock_import" / "spare_parts.json"
IMAGE_DIR = REPO / "fleetix" / "public" / "parts"
IMAGE_URL = "/assets/fleetix/parts/{}.jpg"
ATTACHED_CONFIDENCE = {"high", "medium"}
MAX_SIDE = 640
JPEG_QUALITY = "80"
CODE_PREFIX = "SP-"
ITEM_GROUPS = {
	"tyre": "Tires",
	"battery": "Battery",
	"other": "Spare Parts",
	"brake": "Brake Parts",
	"spark plug": "Spark Plugs",
	"bulb": "Bulbs",
	"filter": "Filters",
}


def normalise(text):
	return re.sub(r"\s+", " ", text or "").strip()


def load_previous_codes():
	if not DATA_FILE.exists():
		return {}
	return {part["key"]: part["item_code"] for part in json.loads(DATA_FILE.read_text())["parts"]}


def load_images(source):
	rows = {}
	for path in sorted(glob.glob(str(source / "images" / "index-*.jsonl"))):
		for line in Path(path).read_text().splitlines():
			if line.strip():
				row = json.loads(line)
				rows[row["key"]] = row
	return rows


def assign_codes(parts, previous):
	taken = set(previous.values())
	next_no = max((int(code[len(CODE_PREFIX) :]) for code in taken), default=0) + 1
	codes = {}
	for part in sorted(parts, key=lambda p: (p["category"], normalise(p["name_ar"]))):
		code = previous.get(part["key"])
		if not code:
			code = f"{CODE_PREFIX}{next_no:05d}"
			next_no += 1
		codes[part["key"]] = code
	return codes


def pixel_size(path):
	out = subprocess.run(
		["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
		capture_output=True,
		text=True,
		check=True,
	).stdout
	return max(int(value) for value in re.findall(r"pixel(?:Width|Height): (\d+)", out))


def write_image(src, dest):
	args = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", JPEG_QUALITY]
	if pixel_size(src) > MAX_SIDE:
		args += ["-Z", str(MAX_SIDE)]
	with tempfile.TemporaryDirectory() as tmp:
		out = Path(tmp) / dest.name
		subprocess.run([*args, str(src), "--out", str(out)], capture_output=True, check=True)
		dest.write_bytes(out.read_bytes())


def build(source):
	sheet = json.loads((source / "parts-unique.json").read_text())
	parts = sheet["parts"]
	names = [normalise(p["name_ar"]) for p in parts]
	if len(set(names)) != len(names):
		sys.exit("duplicate normalised name_ar in parts-unique.json")
	unknown = {p["category"] for p in parts} - set(ITEM_GROUPS)
	if unknown:
		sys.exit(f"unmapped category: {sorted(unknown)}")

	codes = assign_codes(parts, load_previous_codes())
	images = load_images(source)
	IMAGE_DIR.mkdir(parents=True, exist_ok=True)
	shipped = set()
	rows = []
	for part in sorted(parts, key=lambda p: codes[p["key"]]):
		code = codes[part["key"]]
		image = images.get(part["key"]) or {}
		image_url = None
		if image.get("confidence") in ATTACHED_CONFIDENCE and image.get("file"):
			write_image(source / "images" / os.path.basename(image["file"]), IMAGE_DIR / f"{code}.jpg")
			shipped.add(f"{code}.jpg")
			image_url = IMAGE_URL.format(code)
		rows.append(
			{
				"item_code": code,
				"key": part["key"],
				"name_ar": normalise(part["name_ar"]),
				"name_en": normalise(part["name_en"]),
				"item_group": ITEM_GROUPS[part["category"]],
				"vehicle_models": [normalise(m) for m in part["vehicle_models"] if normalise(m)],
				"qty": part["total_qty"],
				"rate": part.get("rate"),
				"image": image_url,
			}
		)

	data = {
		"revision": source.name.rsplit("-", 1)[-1],
		"as_of": sheet["generated_at"][:10],
		"parts": rows,
	}
	DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
	print(json.dumps({"parts": len(rows), "images": len(shipped), "qty": sum(r["qty"] for r in rows)}))


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("source", type=Path)
	build(parser.parse_args().source.resolve())


if __name__ == "__main__":
	main()
