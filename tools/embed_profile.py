#!/usr/bin/env python3
"""Embed bounded compiler-produced profile bytes in a generated C++ header."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys
import tempfile


MAX_PROFILE_BYTES = 128 * 1024


class EmbeddingError(ValueError):
    """The generated input/output contract was not satisfied."""


def make_header(raw: bytes) -> bytes:
    # This transports the compiler's text, not a second semantic profile parser.
    # RuntimeProfile's strict loader still validates it before activation.
    if not raw or len(raw) > MAX_PROFILE_BYTES:
        raise EmbeddingError("compiled profile must contain 1..131072 bytes")
    if not raw.startswith(b"B3PROFILE 1\n") or not raw.endswith(b"end\n"):
        raise EmbeddingError("compiled profile must have the canonical version-1 envelope")
    if any(byte not in (9, 10) and not 32 <= byte <= 126 for byte in raw):
        raise EmbeddingError("compiled profile must use ASCII text with LF line endings")
    rows = ["    " + ", ".join(f"0x{byte:02x}" for byte in raw[start:start + 16]) + ","
            for start in range(0, len(raw), 16)]
    header = [
        "// Generated from compiled profile bytes; do not edit.",
        f"// SHA-256: {hashlib.sha256(raw).hexdigest()}",
        "#pragma once", "", "#include <string_view>", "",
        "namespace hammond::vst3 {", "",
        "inline constexpr char kEmbeddedProfileBytes[] = {", *rows, "};", "",
        "inline constexpr std::string_view kEmbeddedProfileText{",
        "    kEmbeddedProfileBytes, sizeof(kEmbeddedProfileBytes)};", "",
        "} // namespace hammond::vst3", "",
    ]
    return "\n".join(header).encode("ascii")


def embed_profile(source: Path, destination: Path) -> str:
    try:
        with source.open("rb") as stream:
            raw = stream.read(MAX_PROFILE_BYTES + 1)
        header = make_header(raw)
        if source.resolve() == destination.resolve():
            raise EmbeddingError("input and generated header must be different files")
        if destination.is_symlink() or (destination.exists() and not destination.is_file()):
            raise EmbeddingError("generated header destination is not a regular file")
        if destination.exists():
            with destination.open("rb") as stream:
                if stream.read(len(header) + 1) == header:
                    return hashlib.sha256(raw).hexdigest()
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary: str | None = None
        try:
            with tempfile.NamedTemporaryFile(prefix=".embedded-profile-", dir=destination.parent,
                                             delete=False) as stream:
                temporary = stream.name
                stream.write(header)
            os.replace(temporary, destination)
            temporary = None
        finally:
            if temporary is not None:
                os.unlink(temporary)
    except OSError as exc:
        raise EmbeddingError(f"cannot embed compiled profile: {exc}") from exc
    return hashlib.sha256(raw).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        digest = embed_profile(args.input, args.output)
    except EmbeddingError as exc:
        print(f"Profile embedding error: {exc}", file=sys.stderr)
        return 1
    print(f"Embedded compiled profile SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
