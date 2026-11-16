"""Independent semantic-forgery and real-process publication adversaries.

The earlier CLI suite owns ordinary flag/path/write failure coverage. This suite
adds OS-delivered interrupts, an unavailable diagnostic pipe, POSIX byte paths,
and well-shaped certificate changes which must fail bounded reconstruction.
Run: python3 -B tests/test_contact_grid_conversion_adversarial.py -v
"""

from __future__ import annotations

import copy
import errno
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tests" / "reference"))
import contact_grid_conversion as conversion
import contact_switching_io as admission
import contact_grid_conversion_cases as corpus


IMPLEMENTATIONS = ("tools/contact_grid_conversion.py", "tools/convert_contact_grid.py",
                   "tools/contact_switching_io.py", "tools/fractional_contact_reference.py")
CONTRACT = "docs/CONTACT_GRID_CONVERSION_CONTRACT.md"
PRIOR = b"retained previous certificate\x00\xff\n"
CASES = {row["name"]: row for row in corpus.cases()}
REFUSAL_FIELDS = {"schema_version", "conversion_id", "status", "code", "path", "witness"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def input_bytes(name="ordinary-44100"):
    return corpus.canonical_input_bytes(CASES[name]["input"])


class CertificateSemanticAdversaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = conversion.convert_document(admission.parse_input(input_bytes()))
        cls.hashes = {path: sha(REPO / path) for path in IMPLEMENTATIONS}
        cls.contract_hash = sha(REPO / CONTRACT)

    def encode(self, result, hashes=None, contract_hash=None):
        return conversion.encode_certificate(
            result, implementation_sha256=self.hashes if hashes is None else hashes,
            contract_sha256=self.contract_hash if contract_hash is None else contract_hash)

    def assert_rejected(self, result, **kwargs):
        with self.assertRaises(conversion.ConversionRefusal) as caught:
            self.encode(result, **kwargs)
        self.assertEqual(caught.exception.code, "certificate")
        self.assertIs(type(caught.exception.path), str)
        self.assertIs(type(caught.exception.witness), dict)

    def test_duplicate_edge_and_arrival_identities_are_not_ignored(self):
        for name in ("edges", "arrivals", "root_bounds"):
            with self.subTest(array=name):
                value = copy.deepcopy(self.original)
                self.assertGreaterEqual(len(value[name]), 2)
                value[name][1] = copy.deepcopy(value[name][0])
                self.assert_rejected(value)

    def test_record_orders_are_certificate_facts(self):
        for name in ("edges", "arrivals", "root_bounds", "commands", "position_samples"):
            with self.subTest(array=name):
                value = copy.deepcopy(self.original)
                self.assertGreaterEqual(len(value[name]), 2)
                value[name].reverse()
                self.assert_rejected(value)

    def test_equality_group_order_membership_and_labels_are_checked(self):
        mutations = []
        value = copy.deepcopy(self.original)
        value["preorder"][0].reverse()
        mutations.append(("label-order", value))
        value = copy.deepcopy(self.original)
        value["preorder"].reverse()
        mutations.append(("group-order", value))
        value = copy.deepcopy(self.original)
        first = value["preorder"].pop(0)
        self.assertGreaterEqual(len(first), 2)
        value["preorder"][0:0] = [[label] for label in first]
        mutations.append(("split-equality", value))
        value = copy.deepcopy(self.original)
        value["preorder"][0].append(value["preorder"][0][0])
        mutations.append(("duplicate-label", value))
        for name, value in mutations:
            with self.subTest(mutation=name):
                self.assert_rejected(value)

    def test_command_identity_and_final_contact_facts_cannot_be_forged(self):
        mutations = []
        value = copy.deepcopy(self.original)
        value["commands"][1]["ordinal"] = value["commands"][0]["ordinal"]
        mutations.append(("duplicate-command", value))
        value = copy.deepcopy(self.original)
        value["commands"][0]["key_index"] = 1
        mutations.append(("other-key", value))
        value = copy.deepcopy(self.original)
        value["final_keys"][0]["closed9"][0] = not value["final_keys"][0]["closed9"][0]
        mutations.append(("contact-bit", value))
        value = copy.deepcopy(self.original)
        value["summary"]["position_witness"] = None
        mutations.append(("missing-position-witness", value))
        for name, value in mutations:
            with self.subTest(mutation=name):
                self.assert_rejected(value)

    def test_transport_changes_fail_even_with_a_matching_recomputed_hash(self):
        for text in (self.original["transport"]["text"] + "0\n",
                     self.original["transport"]["text"].replace("44100", "48000", 1)):
            with self.subTest(transport_bytes=len(text)):
                value = copy.deepcopy(self.original)
                value["transport"]["text"] = text
                value["transport"]["sha256"] = hashlib.sha256(text.encode("ascii")).hexdigest()
                self.assert_rejected(value)

    def test_provenance_requires_exact_paths_and_canonical_hashes(self):
        extra = dict(self.hashes, unexpected="a" * 64)
        missing = dict(self.hashes)
        del missing[IMPLEMENTATIONS[0]]
        upper = dict(self.hashes)
        upper[IMPLEMENTATIONS[0]] = "A" * 64
        boolean = dict(self.hashes)
        boolean[IMPLEMENTATIONS[0]] = True
        for name, hashes in (("extra", extra), ("missing", missing),
                             ("uppercase", upper), ("boolean", boolean)):
            with self.subTest(mutation=name):
                self.assert_rejected(self.original, hashes=hashes)
        self.assert_rejected(self.original, contract_hash="A" * 64)

    def test_pure_encoder_does_not_authenticate_unprovided_original_bytes(self):
        # A deliberate negative control for the documented authority boundary.
        # Metadata and a trajectory-irrelevant source amplitude can be changed
        # consistently; only the CLI's actual input read authenticates them.
        value = copy.deepcopy(self.original)
        value["input_sha256"] = "0" * 64
        value["input_bytes"] = 1
        value["sidecar"]["sources"][0]["amplitude"] = "3fd0000000000000"  # 0.25
        decoded = json.loads(self.encode(value))
        self.assertEqual(decoded["input_sha256"], "0" * 64)
        self.assertEqual(decoded["input_bytes"], 1)
        self.assertEqual(decoded["sidecar"]["sources"][0]["amplitude"], "3fd0000000000000")
        self.assertEqual(decoded["audio_accuracy"], "unqualified")


INTERRUPT_CHILD = r'''
import json, os, signal, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import convert_contact_grid as command
mode, source, destination, ready, observed, result_path = sys.argv[2:]
# A raw, preopened acknowledgment avoids codec lookup/file-object acquisition
# inside the signal handler. The parent waits for bytes, not file creation.
acknowledgment = os.open(observed, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
real_defer = command._DeferredSigint._defer
def observed_defer(self, signum, frame):
    real_defer(self, signum, frame)
    os.write(acknowledgment, b"delivered")
command._DeferredSigint._defer = observed_defer
def pause():
    Path(ready).write_bytes(b"ready")
    sys.stdin.buffer.read(1)
if mode == "acquisition":
    original = command.tempfile.mkstemp
    def acquire(*args, **kwargs):
        answer = original(*args, **kwargs)
        pause()
        return answer
    command.tempfile.mkstemp = acquire
elif mode == "precommit":
    original = command.os.fsync
    def sync(descriptor):
        original(descriptor)
        pause()
    command.os.fsync = sync
elif mode == "committed":
    original = command.os.replace
    def replace(source, destination):
        original(source, destination)
        pause()
    command.os.replace = replace
else:
    raise RuntimeError("unknown phase")
def fd_count():
    return len(os.listdir("/proc/self/fd")) if Path("/proc/self/fd").is_dir() else None
before = fd_count()
previous = signal.getsignal(signal.SIGINT)
status = command.main(["--input", source, "--output", destination])
after = fd_count()
os.close(acknowledgment)
Path(result_path).write_text(json.dumps({"status": status, "fds_before": before,
    "fds_after": after, "handler_restored": signal.getsignal(signal.SIGINT) == previous}))
raise SystemExit(status)
'''


class ProcessPublicationAdversaries(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="contact-grid-adversary-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "input.json"
        self.destination = self.root / "certificate.json"
        self.source.write_bytes(input_bytes("empty-epoch"))
        self.destination.write_bytes(PRIOR)

    def assert_refusal(self, result, status=2):
        self.assertEqual(result.returncode, status, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertLessEqual(len(result.stdout), 8192)
        self.assertEqual(result.stdout.count(b"\n"), 1)
        self.assertTrue(result.stdout.endswith(b"\n"))
        result.stdout.decode("ascii")
        value = json.loads(result.stdout)
        self.assertEqual(set(value), REFUSAL_FIELDS)
        self.assertEqual(value["status"], "refused")
        self.assertEqual(self.destination.read_bytes(), PRIOR)
        self.assertEqual(list(self.root.glob(".contact-grid-*.tmp")), [])
        return value

    def test_closed_refusal_pipe_preserves_exit_status_without_shutdown_exception(self):
        # Handshake guarantees the read end is closed before the CLI can write.
        child = ("import pathlib,runpy,sys;sys.stdin.buffer.read(1);"
                 "sys.argv=[sys.argv[1]];sys.path.insert(0,str(pathlib.Path(sys.argv[0]).parent));"
                 "runpy.run_path(sys.argv[0],run_name='__main__')")
        process = subprocess.Popen([sys.executable, "-B", "-c", child,
                                    str(REPO / "tools/convert_contact_grid.py")],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            process.stdout.close()
            process.stdout = None
            _, stderr = process.communicate(b"x", timeout=10)
            self.assertEqual(process.returncode, 2, stderr)
            self.assertEqual(stderr, b"")
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=10)
        self.assertEqual(self.destination.read_bytes(), PRIOR)

    def test_normal_refusal_remains_ascii_under_ascii_stdio(self):
        environment = dict(os.environ, PYTHONIOENCODING="ascii:strict")
        result = subprocess.run([sys.executable, "-B", str(REPO / "tools/convert_contact_grid.py"),
                                 "--input", str(self.source), "--output", str(self.destination),
                                 "unrecognized-\u03b1-\x1b[31m"], capture_output=True, env=environment,
                                timeout=10, check=False)
        value = self.assert_refusal(result)
        self.assertEqual(value["code"], "argument")
        self.assertNotIn("\x1b", value["witness"]["reason"])

    @unittest.skipUnless(os.name == "posix", "undecodable byte filenames are POSIX-specific")
    def test_valid_input_and_output_accept_non_utf8_posix_path_names(self):
        source = self.root / os.fsdecode(b"input-\xff.json")
        destination = self.root / os.fsdecode(b"certificate-\xfe.json")
        data = input_bytes("time-midpoint-even")
        # POSIX alone does not promise arbitrary-byte filenames: the hosted
        # macOS filesystem rejects these names before the CLI can run. Probe
        # both exact names and skip only that demonstrated encoding limitation.
        for path, payload in ((source, data), (destination, PRIOR)):
            try:
                path.write_bytes(payload)
            except OSError as error:
                if error.errno == errno.EILSEQ:
                    self.skipTest("filesystem rejects this non-UTF8 byte filename (EILSEQ)")
                raise
        destination.unlink()  # Preserve the original absent-output CLI journey.
        result = subprocess.run([sys.executable, "-B", str(REPO / "tools/convert_contact_grid.py"),
                                 "--input", str(source), "--output", str(destination)],
                                capture_output=True, timeout=10, check=False)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
        certificate = json.loads(destination.read_bytes())
        self.assertEqual(certificate["input_sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(source.read_bytes(), data)

    def test_unicode_paths_preserve_input_and_publication_on_success_and_refusal(self):
        # This journey is not restricted to POSIX or arbitrary-byte filesystems.
        parent = self.root / "\u6f14\u594f"
        parent.mkdir()
        self.source = parent / "\u5165\u529b-\u03a9.json"
        self.destination = parent / "\u8a3c\u660e-\u03bb.json"
        data = input_bytes("time-midpoint-even")
        self.source.write_bytes(data)
        self.destination.write_bytes(PRIOR)
        ascii_source, ascii_destination = self.root / "ascii-input.json", self.root / "ascii-output.json"
        ascii_source.write_bytes(data)
        for source, destination in ((self.source, self.destination), (ascii_source, ascii_destination)):
            result = subprocess.run([sys.executable, "-B", str(REPO / "tools/convert_contact_grid.py"),
                                     "--input", str(source), "--output", str(destination)],
                                    capture_output=True, timeout=10, check=False)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
            self.assertEqual(source.read_bytes(), data)
            self.assertEqual(list(destination.parent.glob(".contact-grid-*.tmp")), [])
        self.assertEqual(self.destination.read_bytes(), ascii_destination.read_bytes())
        certificate = json.loads(self.destination.read_bytes())
        self.assertEqual(certificate["status"], "accepted")
        self.assertEqual(certificate["input_sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(certificate["input_bytes"], len(data))
        refused = input_bytes("reviewed-f09-equality")
        self.source.write_bytes(refused)
        self.destination.write_bytes(PRIOR)
        result = subprocess.run([sys.executable, "-B", str(REPO / "tools/convert_contact_grid.py"),
                                 "--input", str(self.source), "--output", str(self.destination)],
                                capture_output=True, timeout=10, check=False)
        value = self.assert_refusal(result)
        self.assertEqual(value["code"], "event_order")
        self.assertEqual(self.source.read_bytes(), refused)
        self.assertEqual(list(parent.glob(".contact-grid-*.tmp")), [])

    @unittest.skipUnless(os.name == "posix", "OS-delivered SIGINT journey is POSIX-specific")
    def test_real_sigint_before_commit_during_acquisition_and_after_replace(self):
        for mode, expected in (("precommit", 130), ("acquisition", 130), ("committed", 0)):
            with self.subTest(phase=mode):
                self.destination.write_bytes(PRIOR)
                ready, observed, receipt = [self.root / (mode + suffix)
                                            for suffix in (".ready", ".observed", ".json")]
                process = subprocess.Popen([sys.executable, "-B", "-c", INTERRUPT_CHILD,
                                            str(REPO / "tools"), mode, str(self.source),
                                            str(self.destination), str(ready), str(observed), str(receipt)],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                try:
                    deadline = time.monotonic() + 10
                    while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                        time.sleep(0.005)
                    self.assertTrue(ready.exists(), "child did not reach the selected publication boundary")
                    process.send_signal(signal.SIGINT)
                    if mode != "precommit":
                        while observed.stat().st_size == 0 and process.poll() is None and time.monotonic() < deadline:
                            time.sleep(0.005)
                        self.assertGreater(observed.stat().st_size, 0, "child did not observe SIGINT in its deferred window")
                    stdout, stderr = process.communicate(b"x", timeout=10)
                    result = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
                    if expected:
                        value = self.assert_refusal(result, status=130)
                        self.assertEqual(value["code"], "interrupted")
                    else:
                        self.assertEqual((result.returncode, stdout, stderr), (0, b"", b""))
                        self.assertEqual(json.loads(self.destination.read_bytes())["status"], "accepted")
                        self.assertEqual(list(self.root.glob(".contact-grid-*.tmp")), [])
                    observation = json.loads(receipt.read_text())
                    self.assertEqual(observation["status"], expected)
                    self.assertTrue(observation["handler_restored"])
                    if observation["fds_before"] is not None:
                        self.assertEqual(observation["fds_before"], observation["fds_after"])
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.communicate(timeout=10)


if __name__ == "__main__":
    unittest.main()
