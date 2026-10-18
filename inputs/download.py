"""Secure training implementation. Virtual file map only."""

from __future__ import annotations

import json
import pathlib
import posixpath
import sys
import typing
import urllib.parse

TENANTS = ("red", "blue")


def _response(request, status, body):
    return {
        "request_id": request.get("request_id"),
        "status": status,
        "body": body,
    }


def _denied(request):
    return _response(request, 403, "Denied")


def _safe_key(raw_path, tenant):
    if not isinstance(raw_path, str) or not raw_path:
        return None

    # Decode percent-encoding exactly once.
    try:
        decoded = urllib.parse.unquote(raw_path, errors="strict")
    except UnicodeDecodeError:
        return None


    # Reject backslashes and control characters.
    if "\\" in decoded or any(ord(c) < 32 or ord(c) == 127 for c in decoded):
        return None

    # Reject absolute paths.
    if decoded.startswith("/"):
        return None

    # Normalize legitimate dot segments before checking authorization.
    normalized = posixpath.normpath(decoded)
    root = f"exports/{tenant}"

    # Require the exact tenant directory boundary.
    if not normalized.startswith(root + "/"):
        return None

    if any(segment in ("", ".", "..") for segment in normalized.split("/")):
        return None

    return normalized


def download(request: dict[str, str], files: dict[str, str]) -> dict[str, typing.Any]:
    tenant = request.get("tenant")

    if tenant not in TENANTS:
        return _denied(request)

    key = _safe_key(request.get("path"), tenant)
    if key is None:
        return _denied(request)

    content = files.get(key)
    if content is None:
        return _response(request, 404, "Missing")

    return _response(request, 200, content)


def main():
    base = pathlib.Path(__file__).parent
    files = json.loads(
        (base / "files.json").read_text(encoding="utf-8")
    )
    requests = json.loads(
        pathlib.Path(sys.argv[1]).read_text(encoding="utf-8-sig")
    )
    print(json.dumps([download(req, files) for req in requests], indent=2))


if __name__ == "__main__":
    main()