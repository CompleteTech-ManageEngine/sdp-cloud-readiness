"""Verified local publication of already-sanitized report documents.

No network, credential handling, source-record serialization, or directory
archiving occurs here. ZIPs are built from explicit in-memory report documents,
not from whatever other files happen to be present in a report directory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import errno
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
from typing import Any, Mapping
import uuid
import zipfile

from . import __version__

REPORT_NAMES = ("report.html", "report.md", "assessment.json", "findings.csv",
                "coverage.csv", "vendor-questions.md")
DOCUMENT_NAMES = frozenset((*REPORT_NAMES, "diagnostics.json"))


class ArtifactError(OSError):
    """A fixed, secret-free error; never retains an underlying exception."""

    def __init__(self, code: str = "OUTPUT_VERIFICATION_FAILED") -> None:
        allowed = {"OUTPUT_VERIFICATION_FAILED", "OUTPUT_CONTENT_MISMATCH",
                   "OUTPUT_NOT_REGULAR_FILE", "OUTPUT_PROBE_FAILED"}
        self.code = code if code in allowed else "OUTPUT_VERIFICATION_FAILED"
        super().__init__(self.code)


def failure_metadata(error: OSError, filename: str, operation: str) -> dict[str, Any]:
    """Do not store exception strings, filenames from exceptions, or tracebacks."""
    code = getattr(error, "code", None)
    number = error.errno if isinstance(error.errno, int) and not isinstance(error.errno, bool) else None
    windows = getattr(error, "winerror", None)
    windows = windows if isinstance(windows, int) and not isinstance(windows, bool) else None
    if not isinstance(error, ArtifactError):
        if isinstance(error, PermissionError) or number in {errno.EACCES, errno.EPERM} or windows == 5:
            code = "ACCESS_DENIED"
        elif isinstance(error, FileNotFoundError) or number == errno.ENOENT:
            code = "FILE_NOT_FOUND"
        elif number == errno.ENOSPC or windows in {39, 112}:
            code = "DISK_FULL"
        elif number == errno.ENAMETOOLONG or windows == 206:
            code = "PATH_TOO_LONG"
        elif number == errno.EROFS:
            code = "READ_ONLY_FILESYSTEM"
        elif isinstance(error, FileExistsError):
            code = "ALREADY_EXISTS"
        else:
            code = "FILESYSTEM_ERROR"
    return {"file": filename, "operation": operation, "classification": code,
            "errno": number, "winerror": windows,
            "message": "Local file operation or read-back verification failed; underlying exception text omitted."}


def verify_bytes(path: Path, expected: bytes) -> None:
    """Reopen a regular file, check length and content digest; never echo bytes."""
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ArtifactError("OUTPUT_NOT_REGULAR_FILE")
    if info.st_size != len(expected):
        raise ArtifactError("OUTPUT_CONTENT_MISMATCH")
    with path.open("rb") as handle:
        actual = handle.read(len(expected) + 1)
    if len(actual) != len(expected) or hashlib.sha256(actual).digest() != hashlib.sha256(expected).digest():
        raise ArtifactError("OUTPUT_CONTENT_MISMATCH")


def atomic_write_bytes(destination: Path, contents: bytes) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent,
                                         prefix="." + destination.name + ".", suffix=".tmp",
                                         delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(contents)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
        verify_bytes(destination, contents)
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                # No dynamic filesystem exception may replace a safe failure.
                pass


def prepare_output(output: Path) -> None:
    """Create the fresh run directory and verify write/read before any API call."""
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    probe = output / (".write-read-check-" + uuid.uuid4().hex + ".txt")
    try:
        atomic_write_bytes(probe, b"SDP read-only assessment local output check\n")
    finally:
        probe.unlink(missing_ok=True)


@dataclass
class Publication:
    directory: Path
    paths: dict[str, Path] = field(default_factory=dict)
    failures: dict[str, dict[str, Any]] = field(default_factory=dict)
    bundle: Path | None = None
    manifest: Path | None = None
    _expected: dict[str, bytes] = field(default_factory=dict, repr=False)
    _bundle_expected: bytes | None = field(default=None, repr=False)

    def verify(self) -> None:
        """Recheck at the CLI boundary; a stale/nonexistent path is not returned."""
        for name, contents in self._expected.items():
            path = self.directory / name
            try:
                verify_bytes(path, contents)
            except OSError as error:
                self.paths.pop(name, None)
                self.failures[name] = failure_metadata(error, name, "final_read_back")
                if name == "report-manifest.json":
                    self.manifest = None
            else:
                self.paths[name] = path
                self.failures.pop(name, None)
                if name == "report-manifest.json":
                    self.manifest = path
        if self._bundle_expected is not None:
            candidate = self.directory.parent / (self.directory.name + ".zip")
            try:
                verify_bytes(candidate, self._bundle_expected)
            except OSError as error:
                self.bundle = None
                self.failures["report-bundle.zip"] = failure_metadata(error, "report-bundle.zip", "final_read_back")
            else:
                self.bundle = candidate
                self.failures.pop("report-bundle.zip", None)

    @property
    def complete(self) -> bool:
        return not self.failures and self.bundle is not None and self.manifest is not None and all(name in self.paths for name in REPORT_NAMES)


def publish_documents(documents: Mapping[str, str], output: Path) -> Publication:
    """Write and verify reports, a manifest and a sibling ZIP recovery copy.

    Failed individual files do not prevent the other formats or ZIP being
    attempted. This cannot guarantee retention after verification or defeat a
    filesystem/security policy that blocks both the individual files and ZIP.
    """
    if not set(REPORT_NAMES).issubset(documents) or not set(documents).issubset(DOCUMENT_NAMES):
        raise ValueError("Only the explicit report and diagnostics filenames may be published.")
    if not all(isinstance(text, str) for text in documents.values()):
        raise ValueError("Report documents must be text.")
    result = Publication(output)
    encoded = {name: text.encode("utf-8") for name, text in documents.items()}
    result._expected.update(encoded)
    try:
        output.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError as error:
        result.failures["report-directory"] = failure_metadata(error, "report-directory", "create_directory")
    for name, contents in encoded.items():
        try:
            atomic_write_bytes(output / name, contents)
        except OSError as error:
            result.failures[name] = failure_metadata(error, name, "write_and_read_back")
        else:
            result.paths[name] = output / name
    # Verify again after the entire set is written, not just immediately after
    # each rename. A watcher can remove an earlier file during later writes.
    result.verify()
    manifest = {
        "schema_version": "1.0", "tool_version": __version__,
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "verification": "Regular files reopened; byte lengths and SHA-256 checked. Point-in-time check only; later retention is not guaranteed.",
        "files": [{"name": name, "bytes": len(contents), "sha256": hashlib.sha256(contents).hexdigest(),
                   "individual_file_verified": name in result.paths} for name, contents in encoded.items()],
        "individual_file_errors": list(result.failures.values()),
        "zip_contents": "Explicit sanitized report documents and this manifest only; no source files or directory sweep.",
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    result._expected["report-manifest.json"] = manifest_bytes
    try:
        atomic_write_bytes(output / "report-manifest.json", manifest_bytes)
    except OSError as error:
        result.failures["report-manifest.json"] = failure_metadata(error, "report-manifest.json", "write_and_read_back")
    else:
        result.manifest = output / "report-manifest.json"
        result.paths["report-manifest.json"] = result.manifest
    archive_documents = {**encoded, "report-manifest.json": manifest_bytes}
    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, contents in archive_documents.items():
            archive.writestr(name, contents)
    archive_bytes = archive_buffer.getvalue()
    # Validate the exact in-memory ZIP before writing it. No disk files are
    # added, so a failed HTML write cannot leave the recovery ZIP without HTML.
    with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(archive_documents):
            raise ArtifactError()
        for name, contents in archive_documents.items():
            if archive.read(name) != contents:
                raise ArtifactError()
    result._bundle_expected = archive_bytes
    try:
        atomic_write_bytes(output.parent / (output.name + ".zip"), archive_bytes)
    except OSError as error:
        result.failures["report-bundle.zip"] = failure_metadata(error, "report-bundle.zip", "write_and_read_back")
    else:
        result.bundle = output.parent / (output.name + ".zip")
    result.verify()
    return result
