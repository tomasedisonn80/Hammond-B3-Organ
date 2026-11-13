#!/usr/bin/env python3
"""Independent documentary-registration export and file-admission acceptance.

Expected rows come from atlas reading B, and state bytes from B3CONTROLS3.
The exporter is imported only to exercise public entry points and inject I/O
failure; its constants, formatter and private validators are never oracles.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/chapel_controls.py"
COMPILER = ROOT / "tools/compile_chapel_presets.py"
AUTHORING = ROOT / "data/registrations/atlas-chapel-nominal-v1.json"
REVIEWS = (ROOT / "data/registrations/review-a-chapel.csv", ROOT / "data/registrations/review-b-chapel.csv")
KEYS = ("C#", "D", "D#", "E", "F", "F#", "G", "G#", "A")
UPPER = ("005320000", "004432000", "008740000", "004544222", "005403000", "004675300", "005644320", "006876540", "327645222")
LOWER = ("004545440", "004423220", "007373430", "004544220", "006644322", "005642200", "006845433", "008030000", "427866244")
CATALOG_HASH = "f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91"
SENTINEL = b"Existing state must survive\x00\xff\n"
ZERO = "0 0 0 0 0 0 0 0 0"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def expected_state(upper: str = "off", lower: str = "off", bank: str = "A", expression: str = "0.75") -> bytes:
    # This template is the retained state grammar. The input expression is the
    # independently expected serialized token, never a producer conversion.
    u = " ".join(UPPER[KEYS.index(upper)]) if upper != "off" else ZERO
    l = " ".join(LOWER[KEYS.index(lower)]) if lower != "off" else ZERO
    ua, ub = (u, ZERO) if bank == "A" else (ZERO, u)
    la, lb = (l, ZERO) if bank == "A" else (ZERO, l)
    return (f"B3CONTROLS3\nexpression {expression}\n"
            "percussion enabled 0 harmonic second volume normal decay slow\n"
            "pedal drawbars 0 0\n"
            f"manual upper selected {bank} route_enabled {int(upper != 'off')}\n"
            f"bank A {ua}\nbank B {ub}\n"
            f"manual lower selected {bank} route_enabled {int(lower != 'off')}\n"
            f"bank A {la}\nbank B {lb}\nend\n").encode("ascii")


def tree_snapshot(root: Path) -> dict:
    result = {}
    def visit(directory: Path) -> None:
        for path in sorted(directory.iterdir()):
            metadata = path.lstat()
            kind = stat.S_IFMT(metadata.st_mode)
            reparse = bool(getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
            if stat.S_ISLNK(metadata.st_mode) or reparse:
                content = os.readlink(path)
            elif stat.S_ISREG(metadata.st_mode):
                content = path.read_bytes()
            else:
                content = None
            result[path.relative_to(root).as_posix()] = (kind, stat.S_IMODE(metadata.st_mode), metadata.st_ino, content)
            if stat.S_ISDIR(metadata.st_mode) and not reparse:
                visit(path)
    visit(root)
    return result


def reader_metadata(metadata, **changes):
    """Keep real file facts except the deliberately injected observation."""
    values = {name: getattr(metadata, name) for name in (
        "st_mode", "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")}
    values["st_file_attributes"] = getattr(metadata, "st_file_attributes", 0)
    values.update(changes)
    return SimpleNamespace(**values)


def make_catalog(destination: Path) -> bytes:
    process = subprocess.run([sys.executable, str(COMPILER), "--input", str(AUTHORING),
                              "--review-a", str(REVIEWS[0]), "--review-b", str(REVIEWS[1]),
                              "--output", str(destination)], capture_output=True, timeout=5,
                             env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), check=False)
    if process.returncode != 0 or process.stdout or process.stderr:
        raise AssertionError(f"Catalog prerequisite failed: {process.returncode}, {process.stdout!r}, {process.stderr!r}")
    payload = destination.read_bytes()
    if digest(payload) != CATALOG_HASH or len(payload) != 4837:
        raise AssertionError("Compiled source fixture differs from the independently accepted catalog")
    return payload


class ChapelControlsAcceptance(unittest.TestCase):
    cli_invocations = 0
    api_rejections = 0
    io_failures = 0
    valid_exports = 0
    reader_rejections = 0

    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("chapel_controls_acceptance_subject", TOOL)
        if spec is None or spec.loader is None:
            raise RuntimeError("Exporter implementation is required")
        sys.path.insert(0, str(ROOT / "tools"))
        try:
            cls.subject = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.subject)
        finally:
            sys.path.pop(0)
        cls.originals = {p: p.read_bytes() for p in (TOOL, COMPILER, AUTHORING, *REVIEWS)}
        with tempfile.TemporaryDirectory(prefix="chapel-controls-catalog-") as temporary:
            cls.catalog_bytes = make_catalog(Path(temporary) / "catalog.json")
        cls.catalog_value = json.loads(cls.catalog_bytes)
        print(f"Chapel exporter SHA-256: {digest(cls.originals[TOOL])}", flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        for path, data in cls.originals.items():
            if path.read_bytes() != data:
                raise AssertionError(f"Input source changed during acceptance: {path}")
        print(f"Chapel controls acceptance: {cls.cli_invocations} exporter CLI invocations, "
              f"{cls.valid_exports} exact exported states, {cls.api_rejections} API rejections, "
              f"{cls.io_failures} publication fault probes, "
              f"{cls.reader_rejections} reader rejection probes", flush=True)

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="chapel-controls-acceptance-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.catalog = self.root / "catalog.json"
        self.catalog.write_bytes(self.catalog_bytes)
        self.output = self.root / "audition.b3controls"

    def arguments(self, *extra: str, output: Path | None = None, catalog: Path | None = None) -> list[str]:
        return ["--catalog", str(catalog or self.catalog), "--output", str(output or self.output), *extra]

    def invoke(self, arguments: list[str], expected: int = 0) -> subprocess.CompletedProcess:
        self.__class__.cli_invocations += 1
        process = subprocess.run([sys.executable, str(TOOL), *arguments], cwd=self.root,
                                 stdin=subprocess.DEVNULL, capture_output=True, timeout=5,
                                 env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), check=False)
        self.assertEqual(process.returncode, expected, process.stdout.decode(errors="replace") + process.stderr.decode(errors="replace"))
        if expected == 0:
            self.assertEqual(process.stderr, b"")
        else:
            self.assertTrue(process.stderr)
            self.assertNotIn(b"Traceback", process.stderr)
            self.assertEqual(process.stdout, b"")
        return process

    def rejected_cli(self, arguments: list[str], expected: int = 1) -> None:
        before = tree_snapshot(self.root)
        self.invoke(arguments, expected)
        self.assertEqual(tree_snapshot(self.root), before, "Rejected invocation changed its fixture")

    def rejected_api(self, function, *arguments, **kwargs) -> None:
        self.__class__.api_rejections += 1
        before = tree_snapshot(self.root)
        with self.assertRaises(self.subject.ChapelControlsError):
            function(*arguments, **kwargs)
        self.assertEqual(tree_snapshot(self.root), before)

    def export(self, upper: str, lower: str, bank: str, *, expression: str = "0.75", serialized: str = "0.75") -> None:
        destination = self.root / f"state-{self.valid_exports}.b3controls"
        process = self.invoke(self.arguments("--upper", upper, "--lower", lower, "--bank", bank,
                                             "--expression", expression, output=destination))
        self.assertEqual(process.stdout, b"")
        expected = expected_state(upper, lower, bank, serialized)
        self.assertEqual(destination.read_bytes(), expected)
        self.assertEqual(len(expected.split()), 73)
        self.assertEqual(len(expected.splitlines()), 11)
        self.assertEqual(self.catalog.read_bytes(), self.catalog_bytes)
        self.__class__.valid_exports += 1

    def test_all_manual_selections_and_banks(self) -> None:
        for bank in ("A", "B"):
            for upper in (*KEYS, "off"):
                for lower in (*KEYS, "off"):
                    if upper == lower == "off":
                        continue
                    with self.subTest(upper=upper, lower=lower, bank=bank):
                        self.export(upper, lower, bank)
        self.assertEqual(len(list(self.root.glob("*.b3controls"))), 198)

    def test_defaults_help_and_equals_options(self) -> None:
        process = self.invoke(self.arguments("--upper", "C#"))
        self.assertEqual(process.stdout, b"")
        self.assertEqual(self.output.read_bytes(), expected_state("C#"))
        other = self.root / "equals options.b3controls"
        self.invoke([f"--catalog={self.catalog}", f"--output={other}", "--lower=G#", "--bank=B"])
        self.assertEqual(other.read_bytes(), expected_state("off", "G#", "B"))
        before = tree_snapshot(self.root)
        help_result = self.invoke(["--help"])
        for option in (b"--catalog", b"--output", b"--upper", b"--lower", b"--bank", b"--expression"):
            self.assertIn(option, help_result.stdout)
        self.assertEqual(tree_snapshot(self.root), before)

    def test_expression_values_and_exact_canonical_tokens(self) -> None:
        pairs = (("0", "0"), ("1", "1"), ("0.1", "0.10000000000000001"),
                 ("0.375", "0.375"), ("0.001", "0.001"), ("0.9", "0.90000000000000002"),
                 ("0." + "0" * 61 + "1", "1e-62"))
        for value, serialized in pairs:
            with self.subTest(value=value):
                self.export("A", "F#", "B", expression=value, serialized=serialized)
        for token in (None, True, 0.75, 0, "", "0.0", "1.0", "0.10", "00", ".5", "00.5", "0.",
                      "+0.5", "-0", "-0.1", "1.1", "2", "1e-1", "nan", "inf", " 0.5", "0.5 ",
                      "0.5\n", "0,5", "０.5", "0." + "0" * 62 + "1"):
            with self.subTest(token=token):
                self.rejected_api(self.subject.expression_value, token)

    def test_strict_cli_errors_preserve_files(self) -> None:
        base = self.arguments("--upper", "D")
        cases = [[], ["--help", "--upper", "D"], ["--help", "--help"],
                 ["--catalog", str(self.catalog)], ["--output", str(self.output)],
                 self.arguments(), self.arguments("--upper", "off", "--lower", "off"),
                 base + ["--unknown", "x"], base + ["--upper", "E"], base + ["--catalog", str(self.catalog)],
                 base + ["--output", str(self.output)], base + ["--bank", "A", "--bank", "B"],
                 base + ["--expression", "0.5", "--expression", "0.25"],
                 self.arguments("--upper", "d"), self.arguments("--upper", "A#"),
                 self.arguments("--upper", "B"), self.arguments("--upper", "C"),
                 self.arguments("--lower", "OFF"), base + ["--bank", "a"],
                 base + ["--bank"], base + ["--expression"],
                 ["--cat", str(self.catalog), "--output", str(self.output), "--upper", "D"],
                 ["--catalog", "", "--output", str(self.output), "--upper", "D"],
                 ["--catalog", str(self.catalog), "--output", "", "--upper", "D"]]
        cases += [base + ["--expression=" + token] for token in
                  ("0.0", "1.0", ".5", "+0.5", "-0", "1e-1", "0.50", "NaN", "inf", "1.1")]
        for arguments in cases:
            with self.subTest(arguments=arguments):
                self.rejected_cli(arguments, expected=2)

    def test_catalog_shape_and_provenance_rejections(self) -> None:
        variants = [None, [], True, {}, dict(self.catalog_value, extra=0)]
        for path, value in ((('format',), 'future'), (('schema_version',), True),
                            (('source','page'), 121), (('source','sha256'), '0'*64),
                            (('source','primary_reference','status'), 'verified'),
                            (('limitations','physical_latch'), 'modeled'),
                            (('inputs','authoring','bytes'), True), (('inputs','authoring','bytes'), 0),
                            (('inputs','authoring','bytes'), 65537), (('inputs','authoring','bytes'), 4298.0),
                            (('inputs','authoring','sha256'), 'A'*64), (('inputs','authoring','sha256'), '0'*63),
                            (('inputs','authoring','canonical_sha256'), '0'*64),
                            (('inputs','review_a','bytes'), 465), (('inputs','review_b','bytes'), True),
                            (('inputs','review_a','sha256'), '0'*64), (('inputs','review_b','sha256'), None)):
            value_copy = deepcopy(self.catalog_value)
            parent = value_copy
            for part in path[:-1]: parent = parent[part]
            parent[path[-1]] = value
            variants.append(value_copy)
        for field in self.catalog_value:
            value = deepcopy(self.catalog_value); del value[field]; variants.append(value)
        for label in ("authoring", "review_a", "review_b"):
            value = deepcopy(self.catalog_value); value["inputs"][label]["extra"] = 0; variants.append(value)
        for value in variants:
            original = deepcopy(value)
            self.rejected_api(self.subject.validate_catalog, value)
            self.assertEqual(value, original)
        # Raw metadata has shape only; this deliberately does not authenticate
        # unavailable raw authoring bytes. Its canonical semantics still match.
        for count in (1, 65536):
            value = deepcopy(self.catalog_value)
            value["inputs"]["authoring"].update(sha256="f" * 64, bytes=count)
            self.subject.validate_catalog(value)

    def test_every_wrong_in_range_tap_rejects_even_with_new_hash(self) -> None:
        for row in range(18):
            for position in range(9):
                value = deepcopy(self.catalog_value)
                taps = list(value["registrations"][row]["drawbars"])
                taps[position] = str((int(taps[position]) + 1) % 9)
                value["registrations"][row]["drawbars"] = "".join(taps)
                authoring = {k:v for k,v in value.items() if k not in ("format", "inputs")}
                value["inputs"]["authoring"]["canonical_sha256"] = digest(json.dumps(
                    authoring, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
                self.rejected_api(self.subject.validate_catalog, value)
        for field, replacement in (("manual", "lower"), ("preset_key", "D"),
                                   ("preset_name", "invented"), ("drawbars", "00532000")):
            value = deepcopy(self.catalog_value); value["registrations"][0][field] = replacement
            self.rejected_api(self.subject.validate_catalog, value)

    def test_malformed_catalog_bytes_reject_before_output(self) -> None:
        cases = [b"", b"{", b"[]", b"null", b"\xff", b"\xef\xbb\xbf" + self.catalog_bytes,
                 self.catalog_bytes + b"\x00", self.catalog_bytes + b"{}",
                 self.catalog_bytes.replace(b'"schema_version": 1', b'"schema_version": 1.0'),
                 self.catalog_bytes.replace(b'"schema_version": 1', b'"schema_version": NaN'),
                 b'{"format":"duplicate",' + self.catalog_bytes[1:], b"[" * 5000 + b"]" * 5000]
        for index, payload in enumerate(cases):
            with self.subTest(index=index):
                self.catalog.write_bytes(payload)
                self.rejected_cli(self.arguments("--upper", "D"))
        self.catalog.write_bytes(self.catalog_bytes + b" " * (65536 - len(self.catalog_bytes)))
        self.invoke(self.arguments("--lower", "G"))
        self.assertEqual(self.output.read_bytes(), expected_state("off", "G"))
        self.output.unlink()
        self.catalog.write_bytes(self.catalog_bytes + b" " * (65537 - len(self.catalog_bytes)))
        self.rejected_cli(self.arguments("--upper", "D"))

    def test_windows_ctime_domains_and_posix_cross_api_guard(self) -> None:
        selected = self.catalog.lstat()
        before = tree_snapshot(self.root)
        for platform in ("nt", "posix"):
            observed = []

            def descriptor_stat(descriptor):
                observed.append(descriptor)
                return reader_metadata(os.fstat(descriptor), st_ctime_ns=selected.st_ctime_ns + 97)

            # Isolate the producer reference; never change global os.name or
            # cause pathlib on this runner to construct another platform's paths.
            isolated_os = SimpleNamespace(**vars(os))
            isolated_os.name, isolated_os.fstat = platform, descriptor_stat
            with self.subTest(platform=platform), mock.patch.object(self.subject, "os", isolated_os):
                if platform == "nt":
                    self.assertEqual(self.subject.load_catalog(self.catalog), self.catalog_value)
                    self.assertEqual(len(observed), 2)
                else:
                    with self.assertRaisesRegex(self.subject.ChapelControlsError, "changed before its bounded read"):
                        self.subject.load_catalog(self.catalog)
                    self.assertEqual(len(observed), 1)
                    self.__class__.api_rejections += 1
                    self.__class__.reader_rejections += 1
            self.assertEqual(tree_snapshot(self.root), before)

    def test_cross_api_identity_size_and_mtime_remain_exact(self) -> None:
        selected = self.catalog.lstat()
        before = tree_snapshot(self.root)
        for platform in ("nt", "posix"):
            for field in ("st_dev", "st_ino", "st_size", "st_mtime_ns"):
                observed = []

                def descriptor_stat(descriptor):
                    observed.append(descriptor)
                    value = reader_metadata(os.fstat(descriptor), st_ctime_ns=selected.st_ctime_ns)
                    return reader_metadata(value, **{field: getattr(value, field) + 1})

                isolated_os = SimpleNamespace(**vars(os))
                isolated_os.name, isolated_os.fstat = platform, descriptor_stat
                with self.subTest(platform=platform, field=field), mock.patch.object(self.subject, "os", isolated_os):
                    with self.assertRaisesRegex(self.subject.ChapelControlsError, "changed before its bounded read"):
                        self.subject.load_catalog(self.catalog)
                self.assertEqual(len(observed), 1)
                self.assertEqual(tree_snapshot(self.root), before)
                self.__class__.api_rejections += 1
                self.__class__.reader_rejections += 1

    def test_each_descriptor_or_path_change_during_read_is_rejected(self) -> None:
        selected = self.catalog.lstat()
        original_lstat = Path.lstat
        before = tree_snapshot(self.root)
        fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns",
                  "st_mode", "st_file_attributes")
        for platform in ("nt", "posix"):
            for domain in ("descriptor", "path"):
                for field in fields:
                    calls = {"descriptor": 0, "path": 0}

                    def change(value):
                        replacement = (stat.S_IFDIR if field == "st_mode" else
                                       value.st_file_attributes | 0x400 if field == "st_file_attributes" else
                                       getattr(value, field) + 1)
                        return reader_metadata(value, **{field: replacement})

                    def descriptor_stat(descriptor):
                        calls["descriptor"] += 1
                        value = reader_metadata(os.fstat(descriptor),
                                                st_ctime_ns=selected.st_ctime_ns + (97 if platform == "nt" else 0))
                        return change(value) if domain == "descriptor" and calls["descriptor"] == 2 else value

                    def path_stat(path, *args, **kwargs):
                        value = original_lstat(path, *args, **kwargs)
                        if path == self.catalog:
                            calls["path"] += 1
                            if domain == "path" and calls["path"] == 2:
                                return change(reader_metadata(value))
                        return value

                    isolated_os = SimpleNamespace(**vars(os))
                    isolated_os.name, isolated_os.fstat = platform, descriptor_stat
                    with self.subTest(platform=platform, domain=domain, field=field), \
                            mock.patch.object(self.subject, "os", isolated_os), \
                            mock.patch.object(Path, "lstat", autospec=True, side_effect=path_stat):
                        with self.assertRaisesRegex(self.subject.ChapelControlsError, "changed during its bounded read"):
                            self.subject.load_catalog(self.catalog)
                    self.assertEqual(calls["descriptor"], 2, "must reach descriptor post-read observation")
                    self.assertEqual(calls["path"], 2, "must reach path post-read observation")
                    self.assertEqual(tree_snapshot(self.root), before)
                    self.__class__.api_rejections += 1
                    self.__class__.reader_rejections += 1

    def test_fdopen_failure_closes_the_acquired_read_descriptor(self) -> None:
        acquired = []
        before = tree_snapshot(self.root)

        def acquire(*args, **kwargs):
            descriptor = os.open(*args, **kwargs)
            acquired.append(descriptor)
            return descriptor

        def fail_wrap(*args, **kwargs):
            raise OSError("controlled read fdopen failure")

        isolated_os = SimpleNamespace(**vars(os))
        isolated_os.open, isolated_os.fdopen = acquire, fail_wrap
        try:
            with mock.patch.object(self.subject, "os", isolated_os):
                with self.assertRaisesRegex(self.subject.ChapelControlsError, "controlled read fdopen failure"):
                    self.subject.load_catalog(self.catalog)
            self.assertEqual(len(acquired), 1)
            with self.assertRaises(OSError):
                os.fstat(acquired[0])
            self.assertEqual(tree_snapshot(self.root), before)
            self.__class__.api_rejections += 1
            self.__class__.reader_rejections += 1
        finally:
            for descriptor in acquired:
                try:
                    os.close(descriptor)
                except OSError:
                    pass

    def test_real_rewritten_catalogs_load_and_export_exact_controls(self) -> None:
        for index, payload in enumerate((self.catalog_bytes + b" \n",
                                         json.dumps(self.catalog_value, sort_keys=True).encode("utf-8"),
                                         self.catalog_bytes)):
            self.catalog.write_bytes(payload)
            self.assertEqual(self.subject.load_catalog(self.catalog), self.catalog_value)
            output = self.root / f"rewritten-{index}.b3controls"
            self.invoke(self.arguments("--upper", "C#", "--lower", "G", "--bank", "B", output=output))
            self.assertEqual(output.read_bytes(), expected_state("C#", "G", "B"))
            self.assertEqual(self.catalog.read_bytes(), payload)

    def test_invalid_public_selection_types_preserve_catalog(self) -> None:
        for kwargs in ({}, {"upper": "off", "lower": "off"}, {"upper": None}, {"upper": True},
                       {"upper": ["D"]}, {"upper": "D", "bank": None}, {"upper": "D", "bank": 0},
                       {"upper": "D", "bank": "a"}, {"upper": "D", "lower": "B"},
                       {"upper": "D", "expression": 0.75}):
            data = deepcopy(self.catalog_value)
            self.rejected_api(self.subject.render_controls, data, **kwargs)
            self.assertEqual(data, self.catalog_value)

    def test_catalog_file_admission_and_unicode_success(self) -> None:
        missing = self.root / "missing.json"
        directory = self.root / "directory.json"; directory.mkdir()
        for path in (missing, directory):
            self.rejected_cli(self.arguments("--upper", "D", catalog=path))
        if hasattr(os, "mkfifo"):
            fifo = self.root / "catalog.fifo"; os.mkfifo(fifo)
            self.rejected_cli(self.arguments("--upper", "D", catalog=fifo))
        folder = self.root / "é espaço 音"; folder.mkdir()
        catalog = folder / "matriz ♯.json"; catalog.write_bytes(self.catalog_bytes)
        output = folder / "registração 音.b3controls"
        self.invoke(self.arguments("--lower", "G#", "--bank", "B", catalog=catalog, output=output))
        self.assertEqual(output.read_bytes(), expected_state("off", "G#", "B"))

    def test_symbolic_link_inputs_and_outputs_are_rejected(self) -> None:
        target = self.root / "sentinel"; target.write_bytes(SENTINEL)
        link = self.root / "link"
        try:
            link.symlink_to(self.catalog)
        except OSError as error:
            self.skipTest(f"Symbolic-link fixture unavailable: {error}")
        self.rejected_cli(self.arguments("--upper", "D", catalog=link))
        link.unlink(); link.symlink_to(target)
        self.rejected_cli(self.arguments("--upper", "D", output=link))
        link.unlink(); link.symlink_to(self.root / "absent-target")
        self.rejected_cli(self.arguments("--upper", "D", output=link))
        self.rejected_cli(self.arguments("--upper", "D", catalog=link))

    def test_existing_destinations_aliases_and_parents_preserved(self) -> None:
        self.output.write_bytes(SENTINEL)
        folder = self.root / "occupied"; folder.mkdir(); (folder / "entry").write_bytes(SENTINEL)
        hardlink = self.root / "catalog-hardlink"; os.link(self.catalog, hardlink)
        file_parent = self.root / "file-parent"; file_parent.write_bytes(SENTINEL)
        for output in (self.output, folder, self.catalog, hardlink,
                       self.root / "missing-parent" / "state", file_parent / "state"):
            self.rejected_cli(self.arguments("--upper", "D", output=output))
        self.assertEqual(self.catalog.read_bytes(), self.catalog_bytes)

    def test_writer_rejects_forged_noncanonical_or_unreviewed_states(self) -> None:
        valid = expected_state("C#", "A", "B").decode()
        variants = [None, valid.encode(), "", valid[:-1], valid + "\n", valid.replace("\n", "\r\n"),
                    valid.replace("\n", "\v"), valid.replace("\n", "\f"), valid + "note 60\n",
                    valid.replace("B3CONTROLS3", "B3CONTROLS2"),
                    valid.replace("expression 0.75", "expression 0.750"),
                    valid.replace("expression 0.75", "expression -0"),
                    valid.replace("expression 0.75", "expression NaN"),
                    valid.replace("percussion enabled 0", "percussion enabled 1"),
                    valid.replace("pedal drawbars 0 0", "pedal drawbars 1 0"),
                    valid.replace("manual lower selected B", "manual lower selected A"),
                    valid.replace("bank B 0 0 5 3 2 0 0 0 0", "bank B 0 0 5 3 1 0 0 0 0"),
                    valid.replace("bank A 0 0 0 0 0 0 0 0 0", "bank A 1 0 0 0 0 0 0 0 0", 1),
                    valid.replace("end", "énd"), "x" * 16385]
        for value in variants:
            self.rejected_api(self.subject.write_controls_file, self.output, value, self.catalog)
        self.subject.write_controls_file(self.output, valid, self.catalog)
        self.assertEqual(self.output.read_bytes(), valid.encode())

    def test_writer_revalidates_changed_catalog(self) -> None:
        text = self.subject.render_controls(deepcopy(self.catalog_value), upper="D")
        value = deepcopy(self.catalog_value); value["source"]["page"] = 121
        self.catalog.write_text(json.dumps(value), encoding="utf-8")
        self.rejected_api(self.subject.write_controls_file, self.output, text, self.catalog)

    def test_prepublication_faults_leave_no_output_or_temporary(self) -> None:
        text = expected_state("A").decode()
        named_temporary = self.subject.tempfile.NamedTemporaryFile
        class Sink:
            def __init__(self, original, kind): self.original, self.kind = original, kind
            def __enter__(self): self.original.__enter__(); return self
            def __exit__(self, *arguments): return self.original.__exit__(*arguments)
            @property
            def name(self): return self.original.name
            def fileno(self): return self.original.fileno()
            def write(self, payload):
                if self.kind == "short-write": return self.original.write(payload[:-1])
                return self.original.write(payload)
            def flush(self):
                if self.kind == "flush": raise OSError("injected flush failure")
                return self.original.flush()
        for kind in ("create", "short-write", "flush", "fsync", "link"):
            if kind == "create":
                patch = mock.patch.object(self.subject.tempfile, "NamedTemporaryFile", side_effect=OSError("injected create"))
            elif kind in ("short-write", "flush"):
                def factory(*args, **kwargs): return Sink(named_temporary(*args, **kwargs), kind)
                patch = mock.patch.object(self.subject.tempfile, "NamedTemporaryFile", side_effect=factory)
            else:
                patch = mock.patch.object(self.subject.os, kind, side_effect=OSError("injected " + kind))
            with self.subTest(kind=kind), patch:
                self.rejected_api(self.subject.write_controls_file, self.output, text, self.catalog)
                self.__class__.io_failures += 1

    def test_competing_file_wins_atomic_no_clobber_publication(self) -> None:
        original_link = self.subject.os.link
        def competing_link(source, destination, **kwargs):
            Path(destination).write_bytes(SENTINEL)
            return original_link(source, destination, **kwargs)
        before_input = self.catalog.read_bytes()
        with mock.patch.object(self.subject.os, "link", side_effect=competing_link):
            with self.assertRaises(self.subject.ChapelControlsError):
                self.subject.write_controls_file(self.output, expected_state("D").decode(), self.catalog)
        self.assertEqual(self.output.read_bytes(), SENTINEL)
        self.assertEqual(self.catalog.read_bytes(), before_input)
        self.assertEqual({p.name for p in self.root.iterdir()}, {self.catalog.name, self.output.name})
        self.__class__.io_failures += 1


if __name__ == "__main__":
    unittest.main()
