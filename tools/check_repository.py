#!/usr/bin/env python3
"""Read-only, bounded source-archive integrity checks; no Git or network needed.

Byte agreement and reconstructed index coverage do not establish source
authenticity, review quality, redistribution rights, or physical fidelity.
"""

import argparse
import bisect
import hashlib
import html
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/research/source-manifest.json"
INDEX = "docs/research/chapter-index.json"
NOTES = "docs/development/agent-notes"
PROFILE = "data/profiles/nominal-unmeasured-v1.json"
CATALOG = "examples/fixtures/catalog-v1.json"
SOURCE_DIRS = (".github", "data", "docs", "examples", "include", "src", "tests", "tools")
MAX_SOURCE_BYTES = 64 * 1024 * 1024
MAX_TEXT_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_ENTRIES = 10000
MAX_DEPTH = 24
MAX_LINKS = 20000
MAX_ERRORS = 100
MAX_AGENTS = 10000
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
NOTE_NAME = re.compile(r"([0-9]{2,5})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md\Z")
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
ESCAPE = re.compile(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])")


class IntegrityError(ValueError):
    """A source contract or a documented resource bound was not satisfied."""


def require(condition, message):
    if not condition:
        raise IntegrityError(message)


def same(actual, expected, location):
    require(type(actual) is type(expected) and actual == expected,
            f"{location}: expected {repr(expected)[:160]}, got {repr(actual)[:160]}")


def obj(value, location):
    require(type(value) is dict, f"{location}: expected an object")
    return value


def items(value, location, maximum):
    require(type(value) is list and len(value) <= maximum,
            f"{location}: expected an array of at most {maximum} entries")
    return value


def integer(value, low, high, location):
    require(type(value) is int and low <= value <= high,
            f"{location}: expected an integer in {low}..{high}")
    return value


def digest(value, location):
    require(type(value) is str and SHA256.fullmatch(value) is not None,
            f"{location}: expected a lowercase SHA-256 digest")
    return value


def _unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key[:120]}")
        result[key] = value
    return result


def _number(token, convert):
    require(len(token) <= 128, "JSON numeric token exceeds 128 characters")
    value = convert(token)
    require(not isinstance(value, float) or math.isfinite(value), "nonfinite JSON number")
    return value


def _constant(token):
    raise IntegrityError(f"non-JSON numeric constant: {token}")


def _label(text):
    return " ".join(html.unescape(ESCAPE.sub(r"\1", text)).split()).casefold()


def _mask(text):
    """Mask fenced examples, HTML comments and inline code, preserving offsets."""
    def blank(value):
        return "".join("\n" if char == "\n" else " " for char in value)

    lines = []
    fence = None
    for line in text.splitlines(keepends=True):
        # Also recognize fences in block quotes; no nested code is interpreted.
        content = re.sub(r"^(?: {0,3}> ?)+", "", line)
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", content.rstrip("\r\n"))
        if fence is not None:
            lines.append(blank(line))
            if match and match[1][0] == fence[0] and len(match[1]) >= fence[1] and not match[2].strip():
                fence = None
        elif match and (match[1][0] != "`" or "`" not in match[2]):
            fence = (match[1][0], len(match[1]))
            lines.append(blank(line))
        else:
            lines.append(line)
    text = re.sub(r"<!--.*?(?:-->|\Z)", lambda match: blank(match[0]), "".join(lines), flags=re.S)
    runs = list(re.finditer(r"`+", text))
    following = {}
    next_run = {}
    for index in range(len(runs) - 1, -1, -1):
        length = len(runs[index][0])
        next_run[index] = following.get(length)
        following[length] = index
    chars = list(text)
    index = 0
    while index < len(runs):
        end = next_run[index]
        start = runs[index].start()
        before = start
        while before and text[before - 1] == "\\":
            before -= 1
        slashes = start - before
        if end is not None and slashes % 2 == 0:
            stop = runs[end].end()
            chars[start:stop] = blank(text[start:stop])
            index = end + 1
        else:
            index += 1
    return "".join(chars)


def _destination(text, start):
    """Read a CommonMark-style angle/bare destination without evaluating it."""
    size = len(text)
    while start < size and text[start].isspace():
        start += 1
    if start == size:
        return None
    if text[start] == "<":
        end = start + 1
        while end < size:
            if text[end] == "\\" and end + 1 < size:
                end += 2
            elif text[end] == ">":
                return text[start + 1:end], end + 1
            elif text[end] in "\r\n<":
                return None
            else:
                end += 1
        return None
    end, depth = start, 0
    while end < size:
        char = text[end]
        if char == "\\" and end + 1 < size:
            end += 2
            continue
        if char.isspace() or (char == ")" and depth == 0):
            break
        if char == "(":
            depth += 1
            require(depth <= 32, "Markdown destination nesting exceeds 32")
        elif char == ")":
            depth -= 1
        elif char == "<":
            return None
        end += 1
    return (text[start:end], end) if depth == 0 else None


def _inline(text, start):
    result = _destination(text, start)
    if result is None:
        return None
    target, end = result
    separator = end
    while end < len(text) and text[end].isspace():
        end += 1
    if end < len(text) and text[end] in "\"'(" and end > separator:
        close = ")" if text[end] == "(" else text[end]
        end += 1
        while end < len(text) and text[end] != close:
            end += 2 if text[end] == "\\" else 1
        if end == len(text):
            return None
        end += 1
        while end < len(text) and text[end].isspace():
            end += 1
    return (target, end + 1) if end < len(text) and text[end] == ")" else None


def markdown_links(text):
    """Yield (destination, one-based line) for inline/image and used references.

    Undefined or unused reference labels are not rendered links. Anchors and
    external destinations are filtered by the caller. HTML href/src is outside
    this Markdown-only contract; heading/fragment validation is not attempted.
    """
    masked = _mask(text)
    definitions = {}
    chars = list(masked)
    pattern = re.compile(r"^ {0,3}\[((?:\\.|[^\]\\\n]){1,999})\]:[ \t]*(?:\n[ \t]*)?", re.M)
    for match in pattern.finditer(masked):
        result = _destination(text, match.end())
        if result is not None:
            target, end = result
            definitions.setdefault(_label(match[1]), target)
            stop = masked.find("\n", end)
            if stop == -1:
                stop = len(masked)
            chars[match.start():stop] = " " * (stop - match.start())
    masked = "".join(chars)
    newlines = [match.start() for match in re.finditer("\n", text)]
    stack = []
    index = 0
    count = 0
    while index < len(masked):
        char = masked[index]
        if char == "\\":
            index += 2
            continue
        if char == "[":
            stack.append(index)
            require(len(stack) <= 128, "Markdown bracket nesting exceeds 128")
        elif char == "]" and stack:
            start = stack.pop()
            label = _label(text[start + 1:index])
            end = index + 1
            result = _inline(text, end + 1) if masked[end:end + 1] == "(" else None
            if result is None:
                reference = label
                if masked[end:end + 1] == "[":
                    stop = masked.find("]", end + 1, end + 1001)
                    if stop != -1:
                        reference = _label(text[end + 1:stop]) or label
                        end = stop + 1
                if reference in definitions:
                    result = (definitions[reference], end)
            if result is not None:
                count += 1
                require(count <= MAX_LINKS, f"Markdown links exceed {MAX_LINKS} per file")
                yield result[0], bisect.bisect_left(newlines, start) + 1
                index = result[1]
                continue
        index += 1


class _Checker:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.total_bytes = 0
        self.entries = 0
        self.errors = []
        self.error_count = 0

    def error(self, check, message):
        self.error_count += 1
        if len(self.errors) < MAX_ERRORS:
            self.errors.append({"check": check, "message": str(message)[:2000]})

    def path(self, value, base=None, directory=False):
        require(type(value) is str and 0 < len(value) <= 4096 and "\x00" not in value,
                "local path: expected a nonempty string of at most 4096 characters")
        require("\\" not in value and not SCHEME.match(value), f"nonportable local path: {value[:160]}")
        relative = PurePosixPath(value)
        require(not relative.is_absolute(), f"expected a repository-relative path: {value[:160]}")
        path = ((base or self.root) / relative).resolve()
        require(path.is_relative_to(self.root), f"local path escapes repository: {value[:160]}")
        mode = path.stat().st_mode
        require(stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode),
                f"expected {'directory' if directory else 'regular file'}: {value[:160]}")
        return path

    def read(self, path, limit=MAX_TEXT_BYTES, retain=True):
        mode = path.stat()
        require(stat.S_ISREG(mode.st_mode), f"not a regular file: {path}")
        require(mode.st_size <= limit, f"{path}: exceeds {limit} byte read bound")
        sha = hashlib.sha256()
        data = bytearray()
        length = 0
        with path.open("rb") as stream:
            while True:
                block = stream.read(min(65536, limit + 1 - length))
                if not block:
                    break
                length += len(block)
                self.total_bytes += len(block)
                require(length <= limit, f"{path}: exceeds {limit} byte read bound")
                require(self.total_bytes <= MAX_TOTAL_BYTES, "repository read exceeds 128 MiB total bound")
                sha.update(block)
                if retain:
                    data.extend(block)
        return bytes(data), length, sha.hexdigest()

    def json(self, value, base=None, limit=MAX_TEXT_BYTES):
        path = self.path(value, base)
        raw = self.read(path, limit)[0]
        try:
            value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique,
                               parse_constant=_constant,
                               parse_int=lambda token: _number(token, int),
                               parse_float=lambda token: _number(token, float))
        except (ValueError, UnicodeError, RecursionError) as error:
            raise IntegrityError(f"{path}: {error}") from error
        pending = [(value, 0)]
        nodes = 0
        while pending:
            item, depth = pending.pop()
            nodes += 1
            require(nodes <= 100000 and depth <= 48, f"{path}: JSON tree exceeds depth/value bounds")
            if type(item) is dict:
                pending.extend((child, depth + 1) for child in item.values())
            elif type(item) is list:
                pending.extend((child, depth + 1) for child in item)
        return obj(value, str(path))

    def manifest(self):
        manifest = self.json(MANIFEST, limit=64 * 1024)
        same(manifest.get("schema_version"), 1, MANIFEST + ": schema_version")
        same(manifest.get("pages"), 500, MANIFEST + ": pages")
        require(type(manifest.get("path")) is str and bool(manifest["path"]),
                MANIFEST + ": path is missing or invalid")
        integer(manifest.get("bytes"), 1, MAX_SOURCE_BYTES, MANIFEST + ": bytes")
        digest(manifest.get("sha256"), MANIFEST + ": sha256")
        require(type(manifest.get("edition")) is str and bool(manifest["edition"].strip()),
                MANIFEST + ": edition is missing")
        return manifest

    def source(self):
        manifest = self.manifest()
        path = self.path(manifest.get("path"))
        _, length, sha = self.read(path, MAX_SOURCE_BYTES, retain=False)
        same(length, manifest["bytes"], MANIFEST + ": source byte length")
        same(sha, manifest["sha256"], MANIFEST + ": source SHA-256")
        return {"path": manifest["path"], "bytes": length, "sha256": sha, "declared_pages": 500}

    def source_reference(self, record, location, manifest, keys=("path", "sha256", "edition")):
        record = obj(record, location)
        for key in keys:
            same(record.get(key), manifest[key], location + ": " + key)
        self.path(record["path"])

    def chapter_index(self):
        manifest = self.manifest()
        index = self.json(INDEX, limit=256 * 1024)
        same(index.get("schema_version"), 1, INDEX + ": schema_version")
        self.source_reference(index.get("source"), INDEX + ": source", manifest,
                              ("path", "sha256", "bytes", "pages", "edition"))
        provenance = obj(index.get("index_provenance"), "index_provenance")
        same(provenance.get("status"), "reconstructed_from_supplied_pdf_not_recovered_companion",
             "index_provenance.status")
        same(provenance.get("contents_pages"), [7, 8, 9, 10, 11], "index_provenance.contents_pages")
        sections = items(index.get("sections"), "sections", 3)
        expected = [("front_matter", 1, 12), ("chapters", 13, 492), ("source_directory", 493, 500)]
        same(len(sections), len(expected), "section count")
        for section, (kind, start, end) in zip(sections, expected):
            section = obj(section, "section")
            for key, target in (("kind", kind), ("start_page", start), ("end_page", end),
                                ("page_count", end - start + 1)):
                same(section.get(key), target, f"section {kind}.{key}")
            if kind == "chapters":
                same(section.get("chapter_count"), 80, "section chapters.chapter_count")
        ranges = items(index.get("review_ranges"), "review_ranges", 500)
        position, reviews = 1, []
        review_ids = set()
        for item in ranges:
            item = obj(item, "review range")
            identity = integer(item.get("review"), 1, MAX_AGENTS, "review ID")
            require(identity not in review_ids, f"duplicate review ID: {identity}")
            review_ids.add(identity)
            same(item.get("start_page"), position, f"review {identity}.start_page (gap/overlap)")
            end = integer(item.get("end_page"), position, 500, f"review {identity}.end_page")
            same(item.get("page_count"), end - position + 1, f"review {identity}.page_count")
            note = self.path(item.get("note"), self.root / "docs/research")
            require(note.parent == self.root / NOTES, f"review {identity}: note is outside {NOTES}")
            reviews.append((position, end, note))
            position = end + 1
        same(position, 501, "review ranges must cover all 500 pages")
        chapters = items(index.get("chapters"), "chapters", 80)
        same(len(chapters), 80, "chapter count")
        for number, chapter in enumerate(chapters, 1):
            chapter = obj(chapter, f"chapter {number}")
            start = 13 + 6 * (number - 1)
            for key, target in (("number", number), ("chapter_id", f"{number:03d}"),
                                ("start_page", start), ("end_page", start + 5),
                                ("research_wave", (number - 1) // 8 + 1),
                                ("contents_page", (number - 1) // 16 + 7)):
                same(chapter.get(key), target, f"chapter {number}.{key}")
            require(type(chapter.get("title")) is str and bool(chapter["title"].strip()),
                    f"chapter {number}: title is missing")
            note = self.path(chapter.get("review_note"), self.root / "docs/research")
            require(any(low <= start and start + 5 <= high and note == target for low, high, target in reviews),
                    f"chapter {number}: review_note does not cover its complete page range")
        waves = items(index.get("research_waves"), "research_waves", 10)
        same(len(waves), 10, "research wave count")
        for number, wave in enumerate(waves, 1):
            wave = obj(wave, f"research wave {number}")
            for key, target in (("number", number), ("first_chapter", 8 * number - 7),
                                ("last_chapter", 8 * number), ("start_page", 48 * number - 35),
                                ("end_page", 48 * number + 12)):
                same(wave.get(key), target, f"research wave {number}.{key}")
        return {"pages": 500, "chapters": 80, "review_ranges": len(ranges), "research_waves": 10}

    def entries_in(self, directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                self.entries += 1
                require(self.entries <= MAX_ENTRIES, f"source inventory exceeds {MAX_ENTRIES} entries")
                yield entry

    @staticmethod
    def excluded(name):
        return (name in {".git", ".venv", "venv", "node_modules", "__pycache__", "out", "dist", "CMakeFiles"}
                or name == "build" or name.startswith(("build-", "build_", "cmake-build-")))

    def markdown_files(self):
        pending = []
        for entry in self.entries_in(self.root):
            if entry.name.lower().endswith(".md") and not entry.is_dir(follow_symlinks=False):
                yield self.path(entry.name)
            elif entry.name in SOURCE_DIRS and entry.is_dir(follow_symlinks=False):
                pending.append((Path(entry.path), 1))
        while pending:
            directory, depth = pending.pop()
            require(depth <= MAX_DEPTH, f"source directory depth exceeds {MAX_DEPTH}: {directory}")
            if (directory / "CMakeCache.txt").exists() or (directory / "CMakeFiles").is_dir():
                continue
            for entry in self.entries_in(directory):
                if entry.is_dir(follow_symlinks=False):
                    if not self.excluded(entry.name):
                        pending.append((Path(entry.path), depth + 1))
                elif entry.name.lower().endswith(".md"):
                    yield self.path(entry.name, directory)

    def markdown(self):
        count = local = external = 0
        for path in self.markdown_files():
            count += 1
            text = self.read(path)[0].decode("utf-8")
            for target, line in markdown_links(text):
                target = html.unescape(ESCAPE.sub(r"\1", target))
                if SCHEME.match(target) or target.startswith("//"):
                    external += 1
                    continue
                try:
                    relative = unquote(urlsplit(target).path, encoding="utf-8", errors="strict")
                    if not relative:
                        continue
                    local += 1
                    base = self.root if relative.startswith("/") else path.parent
                    relative = (relative.lstrip("/") or ".") if relative.startswith("/") else relative
                    candidate = base / relative
                    self.path(relative, base, directory=candidate.is_dir())
                except (ValueError, OSError, RuntimeError) as error:
                    self.error("markdown_links", f"{path.relative_to(self.root)}:{line}: {target[:200]}: {error}")
        return {"files": count, "local_links": local, "external_links_skipped": external}

    def agent_notes(self, expected):
        directory = self.path(NOTES, directory=True)
        identities = {}
        for entry in self.entries_in(directory):
            if not entry.name.lower().endswith(".md"):
                continue
            match = NOTE_NAME.fullmatch(entry.name)
            require(match is not None, f"invalid agent-note filename: {entry.name}")
            identity = integer(int(match[1]), 1, MAX_AGENTS, f"{entry.name}: agent ID")
            same(match[1], f"{identity:02d}", f"{entry.name}: canonical agent ID")
            require(identity not in identities,
                    f"duplicate agent-note ID {identity}: {identities.get(identity)} and {entry.name}")
            self.path(entry.name, directory)
            identities[identity] = entry.name
        if expected is not None:
            required = set(range(1, expected + 1))
            require(set(identities) == required,
                    f"expected agent IDs 1..{expected}; missing={sorted(required - identities.keys())}; "
                    f"unexpected={sorted(identities.keys() - required)}")
        return {"ids": sorted(identities), "count": len(identities), "expected_agents": expected}

    def data_references(self):
        manifest = self.manifest()
        profile = self.json(PROFILE, limit=256 * 1024)
        self.source_reference(profile.get("source_document"), PROFILE + ": source_document", manifest)
        pedal = self.json("data/pedal-map.json", limit=64 * 1024)
        provenance = obj(pedal.get("provenance"), "pedal provenance")
        self.source_reference(provenance.get("source_document"), "pedal source_document", manifest)
        schema = self.json("data/profile.schema.json")
        source = obj(obj(obj(schema.get("properties"), "schema properties").get("source_document"),
                         "schema source_document").get("properties"), "schema source properties")
        for key in ("path", "sha256", "edition"):
            same(obj(source.get(key), "schema source " + key).get("const"), manifest[key], "schema source " + key)
        catalog = self.json(CATALOG, limit=128 * 1024)
        same(catalog.get("schema_version"), 1, CATALOG + ": schema_version")
        bound_profile = obj(catalog.get("profile"), "catalog profile")
        require(type(bound_profile.get("id")) is str and bool(bound_profile["id"].strip()),
                "catalog profile ID is missing")
        authoring_path = self.path(bound_profile.get("authoring_path"))
        authoring = self.json(bound_profile["authoring_path"], limit=256 * 1024)
        canonical = json.dumps(authoring, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode("utf-8")
        same(hashlib.sha256(canonical).hexdigest(), digest(bound_profile.get("authoring_sha256"),
             "catalog authoring_sha256"), "catalog canonical authoring SHA-256")
        same(authoring.get("profile_id"), bound_profile.get("id"), "catalog profile ID")
        self.source_reference(authoring.get("source_document"), str(authoring_path) + ": source_document", manifest)
        fixtures = items(catalog.get("fixtures"), "catalog fixtures", 1000)
        require(bool(fixtures), "catalog fixtures are empty")
        paths = set()
        for number, fixture in enumerate(fixtures, 1):
            fixture = obj(fixture, f"fixture {number}")
            record = obj(fixture.get("events"), f"fixture {number}.events")
            name = record.get("path")
            require(type(name) is str and bool(name) and len(PurePosixPath(name).parts) == 1,
                    f"fixture {number}: event path must be a filename inside fixtures/")
            path = self.path(name, self.root / "examples/fixtures")
            require(path.parent == self.root / "examples/fixtures", f"fixture {number}: event path escapes fixtures/")
            require(path not in paths, f"fixture {number}: duplicate event path {name}")
            paths.add(path)
            _, _, sha = self.read(path, 16384, retain=False)
            same(sha, digest(record.get("sha256"), f"fixture {number}.events.sha256"), f"{name}: event SHA-256")
        return {"atlas_references": 4, "canonical_profiles": 1, "event_files": len(paths),
                "compiled_profile_hash": "not_checked_generated_build_artifact"}


def check_repository(root=ROOT, expected_agents=None):
    """Return a JSON-serializable report, collecting independent check failures."""
    checker = _Checker(root)
    checks = {}
    if expected_agents is not None:
        integer(expected_agents, 1, MAX_AGENTS, "expected_agents")
    operations = (("source_identity", checker.source), ("chapter_index", checker.chapter_index),
                  ("markdown_links", checker.markdown),
                  ("agent_notes", lambda: checker.agent_notes(expected_agents)),
                  ("data_references", checker.data_references))
    for name, operation in operations:
        before = checker.error_count
        try:
            detail = operation()
        except (IntegrityError, OSError, UnicodeError, RuntimeError) as error:
            checker.error(name, error)
            detail = {}
        checks[name] = {"status": "passed" if before == checker.error_count else "failed", **detail}
    return {"status": "passed" if checker.error_count == 0 else "failed", "root": str(checker.root),
            "checks": checks, "errors": checker.errors, "error_count": checker.error_count,
            "errors_truncated": checker.error_count > len(checker.errors),
            "scope": "source_archive_integrity_only", "physical_fidelity": "not_established"}


def _positive_agents(text):
    try:
        value = int(text)
        integer(value, 1, MAX_AGENTS, "expected_agents")
        return value
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--root", type=Path, default=ROOT, help="source archive root (default: tool's parent)")
    parser.add_argument("--expected-agents", type=_positive_agents,
                        help="require exactly agent-note IDs 1..N; default permits partial progress")
    parser.add_argument("--json", action="store_true", help="print one machine-readable JSON report")
    options = parser.parse_args(argv)
    try:
        report = check_repository(options.root, options.expected_agents)
    except (OSError, RuntimeError, ValueError) as error:
        report = {"status": "failed", "checks": {}, "errors": [{"check": "arguments", "message": str(error)}],
                  "scope": "source_archive_integrity_only", "physical_fidelity": "not_established"}
    if options.json:
        print(json.dumps(report, sort_keys=True, allow_nan=False))
    else:
        print(f"Repository integrity: {report['status']}")
        for name, result in report["checks"].items():
            print(f"  {name}: {result['status']}")
        for error in report["errors"]:
            print(f"  {error['check']}: {error['message']}")
        if report.get("errors_truncated"):
            print(f"  Further errors omitted after {MAX_ERRORS} diagnostics.")
        print("Scope: source-archive consistency; physical fidelity is not established.")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
