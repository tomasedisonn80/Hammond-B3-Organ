"""Strict CLI/provenance/transaction checks using the frozen A12 input corpus.

Numerical acceptance is independently checked elsewhere. These tests exercise
the actual converter/encoder for accepted and refused inputs, then inject
filesystem and interruption failures around its single publication boundary.
Run: python3 -B tests/test_contact_grid_conversion_cli.py -v
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tests" / "reference"))
import contact_grid_conversion as conversion
import contact_grid_conversion_cases as corpus
import convert_contact_grid as command


CASES = {row["name"]: row for row in corpus.cases()}
PRIOR = b"prior certificate\x00\xff\nretain exactly on refusal\n"
IMPLEMENTATIONS = ("tools/contact_grid_conversion.py", "tools/convert_contact_grid.py",
                   "tools/contact_switching_io.py", "tools/fractional_contact_reference.py")
REFUSAL_FIELDS = {"schema_version", "conversion_id", "status", "code", "path", "witness"}


class _BrokenWriter:
    def __init__(self, stream, phase):
        self.stream, self.phase = stream, phase

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        self.stream.close()

    def write(self, payload):
        if self.phase == "write":
            raise OSError("injected write failure")
        if self.phase == "short_write":
            self.stream.write(payload[:17])
            return 17
        return self.stream.write(payload)

    def flush(self):
        if self.phase == "flush":
            raise OSError("injected flush failure")
        self.stream.flush()

    def fileno(self):
        return self.stream.fileno()


class ConversionCliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="contact-grid-cli-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "input.json"
        self.destination = self.root / "certificate.json"
        self.write_case("empty-epoch")
        self.destination.write_bytes(PRIOR)

    def write_case(self, name):
        data = corpus.canonical_input_bytes(CASES[name]["input"])
        self.source.write_bytes(data)
        return data

    def invoke(self, arguments=None):
        arguments = (["--input", str(self.source), "--output", str(self.destination)]
                     if arguments is None else arguments)
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = command.main(arguments)
        return status, stdout.getvalue(), stderr.getvalue()

    def assert_refused(self, result, *, code=None, status=2, previous=PRIOR):
        actual_status, stdout, stderr = result
        self.assertEqual(actual_status, status, (stdout, stderr))
        self.assertEqual(stderr, "")
        self.assertTrue(stdout.endswith("\n"))
        self.assertEqual(stdout.count("\n"), 1)
        self.assertLessEqual(len(stdout.encode("ascii")), 8192)
        value = json.loads(stdout)
        self.assertEqual(set(value), REFUSAL_FIELDS)
        self.assertEqual(value["schema_version"], 1)
        self.assertEqual(value["conversion_id"], "fractional-to-contact-grid-rne-v1")
        self.assertEqual(value["status"], "refused")
        self.assertIs(type(value["witness"]), dict)
        if code is not None:
            self.assertEqual(value["code"], code)
        if previous is not None:
            self.assertEqual(self.destination.read_bytes(), previous)
        self.assertEqual(list(self.root.glob(".contact-grid-*.tmp")), [])
        return value

    def assert_success(self, result):
        self.assertEqual(result, (0, "", ""))
        payload = self.destination.read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertEqual(payload.count(b"\n"), 1)
        self.assertLessEqual(len(payload), 32 * 1024 * 1024)
        value = json.loads(payload)
        self.assertEqual(value["status"], "accepted")
        self.assertEqual(value["audio_accuracy"], "unqualified")
        self.assertEqual(value["evidence_class"], "synthetic")
        self.assertEqual(list(self.root.glob(".contact-grid-*.tmp")), [])
        return value

    def test_actual_subprocess_certificate_binds_original_bytes_and_five_files(self):
        original = self.write_case("time-midpoint-odd")
        result = subprocess.run([sys.executable, "-B", str(REPO / "tools" / "convert_contact_grid.py"),
                                 "--input", str(self.source), "--output", str(self.destination)],
                                capture_output=True, text=True, timeout=60, check=False)
        value = self.assert_success((result.returncode, result.stdout, result.stderr))
        self.assertEqual(value["grid_case"]["targets"][0]["tick"], 32770)
        self.assertEqual(value["input_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(value["input_bytes"], len(original))
        expected = {path: hashlib.sha256((REPO / path).read_bytes()).hexdigest()
                    for path in IMPLEMENTATIONS}
        self.assertEqual(value["provenance"]["implementation_sha256"], expected)
        expected_contract = hashlib.sha256((REPO / "docs" / "CONTACT_GRID_CONVERSION_CONTRACT.md").read_bytes()).hexdigest()
        self.assertEqual(value["provenance"]["contract_sha256"], expected_contract)
        self.assertEqual(value["transport"]["sha256"],
                         hashlib.sha256(value["transport"]["text"].encode("ascii")).hexdigest())

    def test_actual_empty_epoch_creates_previously_absent_output(self):
        self.destination.unlink()
        value = self.assert_success(self.invoke())
        self.assertEqual(value["grid_case"]["frames"], 0)
        self.assertEqual(value["transport"]["partitions"], [])

    def test_required_flags_accept_equals_syntax_once(self):
        self.assert_success(self.invoke([f"--output={self.destination}", f"--input={self.source}"]))

    def test_strict_argument_refusals_preserve_output(self):
        base = ["--input", str(self.source), "--output", str(self.destination)]
        trials = [[], base[:2], base[2:], base + ["--input", str(self.source)],
                  base + [f"--output={self.destination}"],
                  ["--in", str(self.source), "--output", str(self.destination)],
                  ["--input", str(self.source), "--out", str(self.destination)],
                  ["--input", "-", "--output", str(self.destination)],
                  ["--input", str(self.source), "--output", "-"],
                  ["--input=", f"--output={self.destination}"],
                  base + ["--factor", "64"], base + ["extra"], base + ["--help"]]
        for arguments in trials:
            with self.subTest(arguments=arguments):
                self.assert_refused(self.invoke(arguments), code="argument")

    def test_invalid_argument_diagnostic_is_sanitized_and_bounded(self):
        result = self.invoke(["--input", str(self.source), "--output", str(self.destination),
                              "x" * 20000 + "\n\x1b[31m"])
        value = self.assert_refused(result, code="argument")
        self.assertLessEqual(len(value["witness"]["reason"]), 480)
        self.assertNotIn("\n", value["witness"]["reason"])
        self.assertNotIn("\x1b", value["witness"]["reason"])

    def test_malformed_input_uses_original_strict_admission(self):
        valid = corpus.canonical_input_bytes(CASES["empty-epoch"]["input"])
        bad = [b"", b"\xff", b"{", b"[]", valid + b"{}",
               valid.replace(b'"frames":0', b'"frames":0,"frames":0'),
               valid.replace(b'"frames":0', b'"frames":true'),
               valid.replace(b'"amplitude":0.5', b'"amplitude":NaN'),
               b"[" * 13 + b"0" + b"]" * 13]
        for index, payload in enumerate(bad):
            with self.subTest(index=index):
                self.source.write_bytes(payload)
                self.assert_refused(self.invoke(), code="input")

    def test_oversized_source_is_rejected_before_reading(self):
        self.source.write_bytes(b" " * (256 * 1024 + 1))
        with patch.object(command.contact_io, "load_input") as load:
            self.assert_refused(self.invoke(), code="path")
            load.assert_not_called()

    def test_actual_frozen_mathematical_refusals_preserve_destination(self):
        names = ("reviewed-target-threshold", "reviewed-hysteresis-collapse", "reviewed-time-collision",
                 "reviewed-threshold-order", "reviewed-f09-equality", "position-budget-above",
                 "root-budget-slow-travel")
        for name in names:
            with self.subTest(name=name):
                self.write_case(name)
                self.assert_refused(self.invoke(), code=CASES[name]["expected_code_or_stage"])

    def test_same_path_and_hardlink_aliases_are_rejected(self):
        source_bytes = self.source.read_bytes()
        self.assert_refused(self.invoke(["--input", str(self.source), "--output", str(self.source)]), code="path")
        self.assertEqual(self.source.read_bytes(), source_bytes)
        alias = self.root / "hardlink.json"
        os.link(self.source, alias)
        self.assert_refused(self.invoke(["--input", str(self.source), "--output", str(alias)]), code="path")
        self.assertEqual(alias.read_bytes(), source_bytes)

    def make_symlink(self, link, target, *, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlink creation unavailable: {error}")

    def test_output_leaf_symlink_rejected_without_touching_target(self):
        link = self.root / "output-link.json"
        self.make_symlink(link, self.destination)
        self.assert_refused(self.invoke(["--input", str(self.source), "--output", str(link)]), code="path")
        self.assertTrue(link.is_symlink())

    def test_input_symlink_and_output_parent_symlink_are_supported(self):
        link = self.root / "input-link.json"
        parent_link = self.root / "parent-link"
        self.make_symlink(link, self.source)
        self.make_symlink(parent_link, self.root, directory=True)
        self.assert_success(self.invoke(["--input", str(link), "--output", str(parent_link / self.destination.name)]))

    def test_missing_parent_and_directory_endpoints_are_refused(self):
        arguments = [
            ["--input", str(self.source), "--output", str(self.root / "missing" / "result.json")],
            ["--input", str(self.root), "--output", str(self.destination)],
            ["--input", str(self.source), "--output", str(self.root)],
            ["--input", str(self.source), "--output", str(self.root) + os.sep],
        ]
        for trial in arguments:
            with self.subTest(arguments=trial):
                self.assert_refused(self.invoke(trial), code="path")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "platform has no FIFO creation")
    def test_fifo_endpoints_are_refused_without_blocking(self):
        fifo = self.root / "pipe"
        os.mkfifo(fifo)
        before = time.monotonic()
        self.assert_refused(self.invoke(["--input", str(fifo), "--output", str(self.destination)]), code="path")
        self.assert_refused(self.invoke(["--input", str(self.source), "--output", str(fifo)]), code="path")
        self.assertLess(time.monotonic() - before, 5.0)

    def test_encoding_refusal_creates_no_temporary(self):
        refusal = conversion.ConversionRefusal("certificate", "summary", {"reason": "injected inconsistent result"})
        with patch.object(conversion, "encode_certificate", side_effect=refusal), \
                patch.object(command.tempfile, "mkstemp") as create:
            self.assert_refused(self.invoke(), code="certificate")
            create.assert_not_called()

    def test_one_absolute_deadline_is_shared_by_conversion_and_encoding(self):
        with patch.object(conversion, "convert_document", wraps=conversion.convert_document) as convert, \
                patch.object(conversion, "encode_certificate", wraps=conversion.encode_certificate) as encode:
            before = time.monotonic()
            self.assert_success(self.invoke())
            deadline = convert.call_args_list[0].kwargs["deadline"]
            self.assertEqual(encode.call_args.kwargs["deadline"], deadline)
            self.assertGreaterEqual(deadline, before + 29.9)
            self.assertLessEqual(deadline, time.monotonic() + 30.0)

    def test_expired_deadline_is_structured_and_does_not_publish(self):
        with patch.object(command, "DEADLINE_SECONDS", 0.0):
            self.assert_refused(self.invoke(), code="resource")

    def test_deadline_after_encoding_precedes_temporary_creation(self):
        refusal = command._CliRefusal("resource", "deadline", {"reason": "injected deadline"})
        with patch.object(command, "_check_deadline", side_effect=[None, None, refusal]), \
                patch.object(command.tempfile, "mkstemp") as create:
            self.assert_refused(self.invoke(), code="resource")
            create.assert_not_called()

    def test_deadline_at_last_precommit_checkpoint_preserves_destination(self):
        refusal = command._CliRefusal("resource", "deadline", {"reason": "injected deadline"})
        with patch.object(command, "_check_deadline", side_effect=[None] * 5 + [refusal]):
            self.assert_refused(self.invoke(), code="resource")

    def test_changed_implementation_binding_is_refused_before_temporary(self):
        real = command._provenance()
        changed = (dict(real[0]), "0" * 64)
        with patch.object(command, "_provenance", side_effect=[real, changed]), \
                patch.object(command.tempfile, "mkstemp") as create:
            self.assert_refused(self.invoke(), code="certificate")
            create.assert_not_called()

    def assert_complete_payload_precedes_all_output_io(self):
        original = conversion.encode_certificate
        events = []

        def encoded(*args, **kwargs):
            value = original(*args, **kwargs)
            events.append("encoded")
            return value

        real_create = command.tempfile.mkstemp

        def created(*args, **kwargs):
            self.assertEqual(events, ["encoded"])
            # Admission resolves the output parent, including /var aliases and
            # Windows short names. Keep the actual argument canonical, rather
            # than comparing it with the caller's possibly aliased spelling.
            self.assertEqual(Path(kwargs["dir"]), self.destination.parent.resolve(strict=True))
            events.append("temporary")
            return real_create(*args, **kwargs)

        with patch.object(conversion, "encode_certificate", side_effect=encoded), \
                patch.object(command.tempfile, "mkstemp", side_effect=created):
            self.assert_success(self.invoke())
        self.assertEqual(events, ["encoded", "temporary"])

    def test_complete_payload_precedes_all_output_io(self):
        self.assert_complete_payload_precedes_all_output_io()

    def test_complete_payload_precedes_output_io_through_parent_alias(self):
        alias = self.root / "parent-alias"
        self.make_symlink(alias, self.root, directory=True)
        self.assertNotEqual(alias, alias.resolve(strict=True))
        self.destination = alias / self.destination.name
        self.assert_complete_payload_precedes_all_output_io()

    def test_temporary_creation_and_fdopen_failures_preserve_destination(self):
        real_open = command.os.fdopen

        def failed_output_open(descriptor, mode, *args, **kwargs):
            if mode == "wb":
                raise OSError("injected output setup failure")
            return real_open(descriptor, mode, *args, **kwargs)

        for function in ("mkstemp", "fdopen"):
            owner = command.tempfile if function == "mkstemp" else command.os
            effect = failed_output_open if function == "fdopen" else OSError("injected setup failure")
            with self.subTest(function=function), patch.object(owner, function, side_effect=effect):
                self.assert_refused(self.invoke(), code="operation")

    def test_partial_write_write_and_flush_failures_remove_owned_temporary(self):
        real_open = command.os.fdopen

        def broken_output(descriptor, mode, *args, **kwargs):
            stream = real_open(descriptor, mode, *args, **kwargs)
            return _BrokenWriter(stream, phase) if mode == "wb" else stream

        for phase in ("write", "short_write", "flush"):
            with self.subTest(phase=phase), patch.object(command.os, "fdopen", side_effect=broken_output):
                self.assert_refused(self.invoke(), code="operation")

    def test_fsync_and_replace_failures_preserve_destination(self):
        for function in ("fsync", "replace"):
            with self.subTest(function=function), patch.object(command.os, function, side_effect=OSError("injected publication failure")):
                self.assert_refused(self.invoke(), code="operation")

    def test_input_change_before_temporary_creation_is_detected(self):
        real_encode = conversion.encode_certificate

        def change_input(*args, **kwargs):
            value = real_encode(*args, **kwargs)
            self.source.write_bytes(self.source.read_bytes() + b" ")
            return value

        with patch.object(conversion, "encode_certificate", side_effect=change_input), \
                patch.object(command.tempfile, "mkstemp") as create:
            self.assert_refused(self.invoke(), code="operation")
            create.assert_not_called()

    def test_input_change_after_fsync_is_detected_and_temporary_removed(self):
        real_fsync = command.os.fsync

        def change_input(descriptor):
            real_fsync(descriptor)
            self.source.write_bytes(self.source.read_bytes() + b" ")

        with patch.object(command.os, "fsync", side_effect=change_input):
            self.assert_refused(self.invoke(), code="operation")

    def test_changed_output_is_not_overwritten_during_recheck(self):
        real_encode = conversion.encode_certificate
        external = b"separate writer's newer result\n"

        def change_output(*args, **kwargs):
            value = real_encode(*args, **kwargs)
            self.destination.write_bytes(external)
            return value

        with patch.object(conversion, "encode_certificate", side_effect=change_output):
            self.assert_refused(self.invoke(), code="operation", previous=external)

    def test_precommit_keyboard_interruptions_return_130(self):
        for owner, function in ((conversion, "convert_document"), (command.os, "fsync"), (command.os, "replace")):
            with self.subTest(function=function), patch.object(owner, function, side_effect=KeyboardInterrupt):
                self.assert_refused(self.invoke(), code="interrupted", status=130)

    @unittest.skipUnless(hasattr(signal, "raise_signal"), "platform lacks raise_signal")
    def test_sigint_during_temporary_acquisition_cleans_owned_file(self):
        real_create = command.tempfile.mkstemp

        def created_then_signal(*args, **kwargs):
            created = real_create(*args, **kwargs)
            signal.raise_signal(signal.SIGINT)
            return created

        with patch.object(command.tempfile, "mkstemp", side_effect=created_then_signal):
            self.assert_refused(self.invoke(), code="interrupted", status=130)

    @unittest.skipUnless(hasattr(signal, "raise_signal"), "platform lacks raise_signal")
    def test_sigint_observed_before_replace_aborts(self):
        real_signal = signal.signal
        installed = 0

        def interrupt_on_install(signum, handler):
            nonlocal installed
            previous = real_signal(signum, handler)
            installed += 1
            if installed == 3:  # Temp acquisition has already installed/restored once.
                signal.raise_signal(signal.SIGINT)
            return previous

        with patch.object(command.signal, "signal", side_effect=interrupt_on_install), \
                patch.object(command.os, "replace") as replace:
            self.assert_refused(self.invoke(), code="interrupted", status=130)
            replace.assert_not_called()

    @unittest.skipUnless(hasattr(signal, "raise_signal"), "platform lacks raise_signal")
    def test_sigint_during_successful_replace_cannot_report_refusal(self):
        real_replace = command.os.replace
        previous_handler = signal.getsignal(signal.SIGINT)

        def committed_then_signal(source, destination):
            real_replace(source, destination)
            signal.raise_signal(signal.SIGINT)

        with patch.object(command.os, "replace", side_effect=committed_then_signal):
            self.assert_success(self.invoke())
        self.assertEqual(signal.getsignal(signal.SIGINT), previous_handler)

    @unittest.skipUnless(hasattr(signal, "raise_signal"), "platform lacks raise_signal")
    def test_sigint_during_failed_replace_preserves_destination(self):
        def failed_then_signal(source, destination):
            signal.raise_signal(signal.SIGINT)
            raise OSError("replace failed before publication")

        with patch.object(command.os, "replace", side_effect=failed_then_signal):
            self.assert_refused(self.invoke(), code="interrupted", status=130)

    def test_interruption_while_restoring_handler_after_commit_is_success(self):
        real_signal = signal.signal
        calls = 0

        def interrupted_restore(signum, handler):
            nonlocal calls
            previous = real_signal(signum, handler)
            calls += 1
            if calls == 4:  # The second restoration follows successful replacement.
                raise KeyboardInterrupt
            return previous

        with patch.object(command.signal, "signal", side_effect=interrupted_restore):
            self.assert_success(self.invoke())

    def test_oversized_exact_refusal_becomes_resource_without_truncation(self):
        ratio = {"numerator": "9" * 1233, "denominator": "1"}
        witness = {str(index): ratio for index in range(7)}
        refusal = conversion.ConversionRefusal("position_budget", "keys[0]", witness)
        with patch.object(conversion, "convert_document", side_effect=refusal):
            value = self.assert_refused(self.invoke(), code="resource")
        self.assertEqual(value["path"], "diagnostic")
        self.assertIn(value["witness"]["reason"],
                      ("diagnostic-size", "refusal diagnostic exceeds 8192 bytes; exact witness not emitted"))
        self.assertNotIn("numerator", json.dumps(value))

        # The public numerical exception can bound its witness before the CLI
        # sees it. Exercise the CLI's independent byte cap with the raw witness.
        encoded = command._refusal_line("position_budget", "keys[0]", witness)
        self.assertLessEqual(len(encoded.encode("ascii")), 8192)
        fallback = json.loads(encoded)
        self.assertEqual(fallback["code"], "resource")
        self.assertIn("exact witness not emitted", fallback["witness"]["reason"])
        self.assertNotIn("numerator", encoded)


if __name__ == "__main__":
    unittest.main()
