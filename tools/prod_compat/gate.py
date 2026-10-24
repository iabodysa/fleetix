#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa

import ast
import subprocess
import sys
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[2]
VERSIONS_FILE = Path(__file__).resolve().parent / "versions.toml"
WATCHED_ROOTS = ("frappe", "erpnext", "hrms")


def load_versions():
	data = tomllib.loads(VERSIONS_FILE.read_text())
	cache_root = Path(data["cache_root"]).expanduser()
	return cache_root, {name: data[name] for name in WATCHED_ROOTS}


def ensure_clone(cache_root, name, spec):
	dest = cache_root / name
	if (dest / ".git").is_dir():
		return dest
	dest.parent.mkdir(parents=True, exist_ok=True)
	subprocess.run(
		["git", "clone", "--depth", "1", "--branch", spec["ref"], spec["repo"], str(dest)],
		check=True,
		capture_output=True,
	)
	return dest


def module_file_candidates(clone_dir, package_dir, dotted_module):
	parts = dotted_module.split(".")
	base = clone_dir / package_dir
	for part in parts[1:]:
		base = base / part
	return [(base.with_suffix(".py"), False), (base / "__init__.py", True)]


def relative_target(current_module, is_package, level, submodule):
	anchor_package = current_module if is_package else current_module.rsplit(".", 1)[0]
	parts = anchor_package.split(".")
	base_parts = parts[: len(parts) - (level - 1)] if level > 1 else parts
	base = ".".join(base_parts)
	return f"{base}.{submodule}" if submodule else base


class SymbolIndex:
	SANCTIONED_PRIVATE_NAMES = frozenset({"_"})

	def __init__(self, clone_dir, package_dir):
		self.clone_dir = clone_dir
		self.package_dir = package_dir
		self._module_cache = {}

	def module_exists(self, dotted_module):
		return self._names_for(dotted_module) is not None

	def has_name(self, dotted_module, name):
		if name in self.SANCTIONED_PRIVATE_NAMES:
			return self._names_for(dotted_module) is not None
		names = self._names_for(dotted_module)
		return names is not None and name in names

	def _names_for(self, dotted_module, _visiting=None):
		if dotted_module in self._module_cache:
			return self._module_cache[dotted_module]
		visiting = _visiting or set()
		if dotted_module in visiting:
			self._module_cache[dotted_module] = set()
			return self._module_cache[dotted_module]
		visiting = visiting | {dotted_module}

		result = None
		for path, is_package in module_file_candidates(self.clone_dir, self.package_dir, dotted_module):
			if path.is_file():
				result = self._top_level_names(path, dotted_module, is_package, visiting)
				break
		self._module_cache[dotted_module] = result
		return result

	def _top_level_names(self, py_file, dotted_module, is_package, visiting):
		names = set()
		tree = ast.parse(py_file.read_text(errors="replace"))
		for node in tree.body:
			if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
				names.add(node.name)
			elif isinstance(node, (ast.Assign, ast.AnnAssign)):
				targets = node.targets if isinstance(node, ast.Assign) else [node.target]
				for target in targets:
					if isinstance(target, ast.Name):
						names.add(target.id)
			elif isinstance(node, ast.ImportFrom):
				target_module = (
					relative_target(dotted_module, is_package, node.level, node.module)
					if node.level
					else node.module
				)
				for alias in node.names:
					if alias.name == "*":
						if target_module and target_module.split(".")[0] == self.package_dir:
							sub = self._names_for(target_module, visiting)
							names |= sub or set()
						continue
					names.add(alias.asname or alias.name)
			elif isinstance(node, ast.Import):
				for alias in node.names:
					names.add((alias.asname or alias.name).split(".")[0])
		return names


def watched_root(dotted_module):
	head = dotted_module.split(".")[0]
	return head if head in WATCHED_ROOTS else None


def scan_file(py_file, indexes):
	findings = []
	try:
		tree = ast.parse(py_file.read_text(errors="replace"), filename=str(py_file))
	except SyntaxError as exc:
		return [(py_file, exc.lineno or 0, "<parse-error>", "", str(exc))]

	for node in ast.walk(tree):
		if isinstance(node, ast.Import):
			for alias in node.names:
				root = watched_root(alias.name)
				if root is None:
					continue
				index = indexes[root]
				if not index.module_exists(alias.name):
					findings.append(
						(py_file, node.lineno, alias.name, "", "module absent from pinned prod source")
					)
		elif isinstance(node, ast.ImportFrom):
			if node.level or node.module is None:
				continue
			root = watched_root(node.module)
			if root is None:
				continue
			index = indexes[root]
			for alias in node.names:
				if alias.name == "*":
					continue
				if alias.name.startswith("_") and alias.name not in SymbolIndex.SANCTIONED_PRIVATE_NAMES:
					findings.append(
						(py_file, node.lineno, node.module, alias.name, "private name (leading underscore)")
					)
					continue
				if not index.has_name(node.module, alias.name):
					findings.append(
						(py_file, node.lineno, node.module, alias.name, "name absent from pinned prod source")
					)
	return findings


def iter_fleetix_py_files(root):
	fleetix_dir = root / "fleetix"
	if not fleetix_dir.is_dir():
		return
	for path in sorted(fleetix_dir.rglob("*.py")):
		if "node_modules" in path.parts or "__pycache__" in path.parts:
			continue
		yield path


def main():
	cache_root, specs = load_versions()
	indexes = {}
	for name, spec in specs.items():
		clone_dir = ensure_clone(cache_root, name, spec)
		indexes[name] = SymbolIndex(clone_dir, spec["package_dir"])

	all_findings = []
	for py_file in iter_fleetix_py_files(REPO_ROOT):
		all_findings.extend(scan_file(py_file, indexes))

	if not all_findings:
		print("prod-compat: 0 finding(s) against pinned frappe/erpnext/hrms")
		return 0

	print(f"prod-compat: {len(all_findings)} finding(s) against pinned frappe/erpnext/hrms")
	for py_file, lineno, module, name, reason in all_findings:
		rel = py_file.relative_to(REPO_ROOT)
		target = f"{module}.{name}" if name else module
		print(f"  {rel}:{lineno} {target} — {reason}")
	return 1


if __name__ == "__main__":
	sys.exit(main())
