#!/usr/bin/env python3
"""Build a deterministic source ZIP and stdlib-only portable Python zipapp.

Only the explicit source/documentation/synthetic-fixture manifest is included.
Generated customer assessment directories, secrets and local caches cannot be
picked up by a recursive archive of the working directory.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import shutil
import zipfile


STAMP = (2026, 10, 14, 0, 0, 0)
BASE_FILES = ("README.md", "connection.example.json", "answers.example.json",
              "sdp_cloud_readiness.py", "__main__.py", "Run-Assessment.cmd", "Run-All-Portals.cmd", "portals.example.json")
PATTERNS = ("sdp_audit/*.py", "tests/*.py", "tests/fixtures/*.json", "tests/fixtures/*.md",
            "docs/*.md", "tools/*.py", "examples/synthetic-assessment/*", "examples/recovery-assessment/*")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_zip(target: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, entries[name])


def build(root: Path, output: Path) -> dict[str, Path]:
    output.mkdir(parents=True, exist_ok=True)
    version_text = (root / "sdp_audit/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([0-9.]+)"', version_text)
    if match is None:
        raise ValueError("Project version not found.")
    version = match.group(1)
    app_entries = {"__main__.py": (root / "__main__.py").read_bytes()}
    app_entries.update({path.relative_to(root).as_posix(): path.read_bytes()
                        for path in sorted((root / "sdp_audit").glob("*.py"))})
    app = output / "sdp_cloud_readiness.pyz"
    write_zip(app, app_entries)
    # Python executes a .pyz ZIP directly; a shebang is unnecessary on Windows
    # and users invoke this portable artifact with python on all platforms.
    paths = {root / name for name in BASE_FILES}
    for pattern in PATTERNS:
        paths.update(path for path in root.glob(pattern) if path.is_file())
    entries = {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(paths)}
    entries["sdp_cloud_readiness.pyz"] = app.read_bytes()
    inner_hashes = "".join(hashlib.sha256(data).hexdigest() + "  " + name + "\n"
                           for name, data in sorted(entries.items()))
    entries["SHA256SUMS.txt"] = inner_hashes.encode("utf-8")
    distribution = output / "sdp-cloud-readiness.zip"
    write_zip(distribution, {"sdp-cloud-readiness/" + name: data for name, data in entries.items()})
    example = output / "Example-Assessment.html"
    shutil.copyfile(root / "examples/synthetic-assessment/report.html", example)
    launcher = output / "Run-Assessment.cmd"
    shutil.copyfile(root / "Run-Assessment.cmd", launcher)
    all_launcher = output / "Run-All-Portals.cmd"
    shutil.copyfile(root / "Run-All-Portals.cmd", all_launcher)
    sums = output / "SHA256SUMS.txt"
    published = (distribution, app, launcher, all_launcher, example)
    sums.write_text("".join(digest(path) + "  " + path.name + "\n" for path in published), encoding="utf-8")
    print("Built ServiceDesk Plus Cloud Readiness v" + version)
    for path in (*published, sums):
        print(str(path))
    return {path.name: path for path in (*published, sums)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    args = parser.parse_args()
    build(Path(__file__).resolve().parents[1], args.output_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
