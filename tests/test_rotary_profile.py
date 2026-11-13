#!/usr/bin/env python3
"""Independent rotary-profile geometry, provenance and parsing regressions.

The ordinary suite uses only the standard library. An explicit --schema-audit
also exercises the published schema with an already-installed jsonschema; a
missing optional dependency is an error in that invocation, never a passed skip.
These are synthetic admission checks, not measured Leslie or runtime results.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import pickle
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import validate_rotary_profile as admission

PROFILE_PATH = ROOT / "data/rotary/nominal-research-v1.json"
SCHEMA_PATH = ROOT / "data/rotary-profile.schema.json"
RAW = PROFILE_PATH.read_bytes()
FIXTURE = json.loads(RAW)
ATLAS_SHA = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
ROTORS = ("horn", "drum")


def fixture():
    return copy.deepcopy(FIXTURE)


def node_at(root, path):
    for key in path:
        root = root[key]
    return root


def assign(root, path, value):
    node_at(root, path[:-1])[path[-1]] = value


def quantity_paths():
    yield ("speed_of_sound",)
    yield ("signal_boundary", "reference_distance")
    for rotor in ROTORS:
        for field in ("slow_speed", "fast_speed", "tau_up", "tau_down", "direction"):
            yield ("rotors", rotor, "motion", field)
        for field in ("axis_origin", "radius"):
            yield ("rotors", rotor, "geometry", field)
        for field in ("angle", "speed"):
            yield ("rotors", rotor, "initial_state", field)
    for receiver in range(2):
        yield ("microphones", receiver, "position")


def object_paths(value, path=()):
    if isinstance(value, dict):
        yield path
        for key, child in value.items():
            yield from object_paths(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from object_paths(child, path + (index,))


def mutable_ids(value):
    result = set()
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) not in (dict, list) or id(item) in result:
            continue
        result.add(id(item))
        pending.extend(item.values() if isinstance(item, dict) else item)
    return result


def geometry_case(target="horn"):
    """Two separated axes; target at zero, other at z=2; safe fixed receivers."""
    profile = fixture()
    for name in ROTORS:
        rotor = profile["rotors"][name]
        rotor["geometry"]["axis_origin"]["value"] = [0.0, 0.0, 0.0 if name == target else 2.0]
        rotor["geometry"]["radius"]["value"] = 0.5
        rotor["initial_state"]["angle"]["value"] = math.pi
    for receiver in profile["microphones"]:
        receiver["position"]["value"] = [2.0, 1.0, 1.0]
    return profile


def directory_fingerprint(root):
    return {
        path.relative_to(root).as_posix(): (
            hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns,
        )
        for path in root.rglob("*") if path.is_file()
    }


class RotaryProfileTests(unittest.TestCase):
    def accepted(self, profile):
        before = pickle.dumps(profile, protocol=4)
        identities = mutable_ids(profile)
        self.assertIs(admission.validate_profile(profile), profile)
        self.assertEqual(pickle.dumps(profile, protocol=4), before)
        self.assertEqual(mutable_ids(profile), identities)

    def rejected(self, profile, message=None):
        # Serialize only test-created objects, never deserialize external pickle.
        # This also checks NaN payloads, large integers and cyclic object graphs.
        before = pickle.dumps(profile, protocol=4)
        identities = mutable_ids(profile)
        with self.assertRaises(admission.RotaryProfileError) as caught:
            admission.validate_profile(profile)
        if message is not None:
            self.assertIn(message, str(caught.exception))
        self.assertEqual(pickle.dumps(profile, protocol=4), before)
        self.assertEqual(mutable_ids(profile), identities)

    def run_cli(self, arguments, cwd):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        return subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_rotary_profile.py"), *arguments],
            cwd=cwd, env=env, encoding="utf-8", stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=15, check=False,
        )

    def test_fixture_is_proposed_and_projection_has_separate_physical_inputs(self):
        self.accepted(fixture())
        self.assertEqual(FIXTURE["source"]["sha256"], ATLAS_SHA)
        self.assertEqual(FIXTURE["evidence_class"], "proposed")
        normalized = admission.normalized_profile(fixture())
        self.assertEqual(normalized["model_id"], "nominal-effective-mouth-rotary-v1")
        self.assertEqual(normalized["contract_id"], "rotary-numerics-v1")
        self.assertEqual(normalized["sound_speed_m_s"], 343.0)
        self.assertEqual(normalized["reference_distance_m"], 1.0)
        self.assertEqual(normalized["rotors"]["horn"]["motion"]["fast_rad_s"], 38.0)
        self.assertEqual(normalized["rotors"]["drum"]["motion"]["fast_rad_s"], 32.0)
        self.assertEqual(normalized["rotors"]["horn"]["motion"]["direction"], 1)
        self.assertEqual(normalized["rotors"]["drum"]["motion"]["direction"], -1)
        self.assertEqual([m["id"] for m in normalized["microphones"]], ["left", "right"])
        self.assertEqual(normalized["motion_prehistory"], "constant-initial-speed-before-zero")
        self.assertEqual(normalized["audio_prehistory"], "zero-before-sample-zero")

    def test_normalized_containers_are_detached_from_authoring_and_other_results(self):
        authoring = fixture()
        before = copy.deepcopy(authoring)
        first = admission.normalized_profile(authoring)
        second = admission.normalized_profile(authoring)
        self.assertTrue(mutable_ids(first).isdisjoint(mutable_ids(authoring)))
        self.assertTrue(mutable_ids(first).isdisjoint(mutable_ids(second)))
        first["rotors"]["horn"]["origin_m"][0] = 123.0
        first["rotors"]["drum"]["motion"]["tau_up_s"] = 123.0
        first["microphones"][0]["position_m"][1] = 123.0
        self.assertEqual(authoring, before)
        self.assertEqual(second, admission.normalized_profile(before))

    def test_canonical_identity_ignores_object_order_but_retains_real_changes(self):
        original = fixture()
        reordered = json.loads(json.dumps(original, sort_keys=True, indent=1))
        self.assertEqual(admission.canonical_json(original), admission.canonical_json(reordered))
        self.assertEqual(admission.authoring_sha256(original), admission.authoring_sha256(reordered))
        self.assertEqual(admission.authoring_sha256(original),
                         hashlib.sha256(admission.canonical_json(original)).hexdigest())
        reordered["rotors"]["horn"]["motion"]["fast_speed"]["value"] = 37.0
        self.assertNotEqual(admission.authoring_sha256(original), admission.authoring_sha256(reordered))
        self.assertEqual(reordered["rotors"]["horn"]["motion"]["fast_speed"]["value"], 37.0)

    def test_load_digest_refers_to_the_same_read_even_if_path_is_replaced(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "profile.json"
            path.write_bytes(RAW)
            replacement = fixture()
            replacement["profile_id"] = "replaced-after-read"
            replacement_bytes = json.dumps(replacement).encode("utf-8")
            original_validate = admission.validate_profile

            def replace_after_read(value):
                path.write_bytes(replacement_bytes)
                return original_validate(value)

            with mock.patch.object(admission, "validate_profile", side_effect=replace_after_read):
                loaded, digest = admission.load_profile_with_digest(path)
            self.assertEqual(loaded, FIXTURE)
            self.assertEqual(digest, hashlib.sha256(RAW).hexdigest())
            self.assertEqual(path.read_bytes(), replacement_bytes)
            self.assertNotEqual(digest, hashlib.sha256(replacement_bytes).hexdigest())

    def test_clearance_boundary_is_checked_for_each_of_four_paths(self):
        # At R=a and vertical separation h, closest range is exactly |h|.
        # No subtracting nearly equal horizontal radii is needed for this oracle.
        for rotor in ROTORS:
            for receiver in range(2):
                with self.subTest(rotor=rotor, receiver=receiver):
                    profile = geometry_case(rotor)
                    profile["microphones"][receiver]["position"]["value"] = [0.5, 0.0, 0.02]
                    self.accepted(profile)
                    profile["microphones"][receiver]["position"]["value"][2] = math.nextafter(0.02, 0.0)
                    self.rejected(profile, "full-orbit clearance")

    def test_maximum_range_boundary_is_checked_for_each_of_four_paths(self):
        # Axis -9.75, receiver +9.75 and radius 0.5: the farthest mouth
        # is at -10.25, exactly 20 m away. All authored coordinates remain legal.
        for rotor in ROTORS:
            for receiver in range(2):
                with self.subTest(rotor=rotor, receiver=receiver):
                    profile = geometry_case(rotor)
                    profile["rotors"][rotor]["geometry"]["axis_origin"]["value"] = [-9.75, 0.0, 0.0]
                    profile["microphones"][receiver]["position"]["value"] = [9.75, 0.0, 0.0]
                    self.accepted(profile)
                    outside = math.nextafter(math.nextafter(9.75, math.inf), math.inf)
                    self.assertGreater(outside + 10.25, 20.0)
                    profile["microphones"][receiver]["position"]["value"][0] = outside
                    self.rejected(profile, "full-orbit path")

    def test_safe_initial_position_does_not_hide_later_orbit_intersection(self):
        for rotor in ROTORS:
            for receiver in range(2):
                with self.subTest(rotor=rotor, receiver=receiver):
                    profile = geometry_case(rotor)
                    # theta=pi places the current mouth at x=-0.5, a metre
                    # from this receiver. A half-turn later it intersects it.
                    profile["microphones"][receiver]["position"]["value"] = [0.5, 0.0, 0.0]
                    self.rejected(profile, "full-orbit clearance")

    def test_zero_radius_axis_interior_and_height_are_distinct_valid_geometries(self):
        cases = (
            (0.0, [0.02, 0.0, 0.0]),  # stationary point at the allowed clearance
            (0.5, [0.0, 0.0, 0.0]),   # centre of a circle, not on its path
            (0.5, [0.25, 0.0, 0.0]),  # inside its disk, still clear of the path
            (0.5, [0.5, 0.0, 0.03]),  # directly above path, finite 3D clearance
            (0.5, [0.0, 0.0, 0.25]),  # microphone on the rotor axis
        )
        for rotor in ROTORS:
            for radius, position in cases:
                with self.subTest(rotor=rotor, radius=radius, position=position):
                    profile = geometry_case(rotor)
                    profile["rotors"][rotor]["geometry"]["radius"]["value"] = radius
                    profile["microphones"][0]["position"]["value"] = position
                    self.accepted(profile)

    def test_geometry_admission_is_invariant_under_declared_rigid_scene_changes(self):
        profile = geometry_case()
        self.accepted(profile)
        vectors = [profile["rotors"][r]["geometry"]["axis_origin"]["value"] for r in ROTORS]
        vectors += [m["position"]["value"] for m in profile["microphones"]]
        for vector in vectors:
            x, y, z = vector
            vector[:] = [-y + 1.0, x - 2.0, z + 0.25]
        self.accepted(profile)

    def test_subsonic_boundary_includes_initial_speed_above_both_targets(self):
        for rotor in ROTORS:
            for dominant in ("fast", "initial"):
                with self.subTest(rotor=rotor, dominant=dominant):
                    profile = geometry_case(rotor)
                    profile["speed_of_sound"]["value"] = 320.0
                    target = profile["rotors"][rotor]
                    target["motion"]["fast_speed"]["value"] = 160.0 if dominant == "fast" else 30.0
                    target["initial_state"]["speed"]["value"] = 4.0 if dominant == "fast" else 160.0
                    # Half-metre radius times 160 rad/s is exactly c/4=80 m/s.
                    self.accepted(profile)
                    quantity = target["motion"]["fast_speed"] if dominant == "fast" else target["initial_state"]["speed"]
                    quantity["value"] = math.nextafter(160.0, math.inf)
                    self.rejected(profile, "maximum rim speed")

    def test_scalar_bounds_include_declared_endpoints_and_exclude_neighbours(self):
        cases = [(('speed_of_sound', 'value'), 300.0, 380.0),
                 (('signal_boundary', 'reference_distance', 'value'), 0.02, 10.0)]
        for rotor in ROTORS:
            cases += [(("rotors", rotor, "geometry", "radius", "value"), 0.0, 1.0)]
            cases += [(("rotors", rotor, "motion", tau, "value"), 0.001, 60.0)
                      for tau in ("tau_up", "tau_down")]
            cases += [(("rotors", rotor, "initial_state", "speed", "value"), 0.0, 200.0)]
        for path, low, high in cases:
            for value, valid in ((low, True), (high, True),
                                 (math.nextafter(low, -math.inf), False),
                                 (math.nextafter(high, math.inf), False)):
                with self.subTest(path=path, value=value):
                    profile = geometry_case()
                    if path[-3:-1] == ("initial_state", "speed"):
                        profile["rotors"][path[1]]["geometry"]["radius"]["value"] = 0.0
                    assign(profile, path, value)
                    (self.accepted if valid else self.rejected)(profile)

    def test_speed_order_commands_directions_and_zero_speed_diagnostics(self):
        for rotor in ROTORS:
            for value in (0.0, 200.0):
                profile = geometry_case(rotor)
                target = profile["rotors"][rotor]
                target["geometry"]["radius"]["value"] = 0.0
                target["motion"]["slow_speed"]["value"] = value
                target["motion"]["fast_speed"]["value"] = value
                target["initial_state"]["speed"]["value"] = value
                self.accepted(profile)
            for command in ("chorale", "tremolo"):
                profile = fixture()
                profile["rotors"][rotor]["initial_command"] = command
                self.accepted(profile)
            for direction in (-1, 1, -1.0, 1.0):
                profile = fixture()
                profile["rotors"][rotor]["motion"]["direction"]["value"] = direction
                self.accepted(profile)
                self.assertIs(type(admission.normalized_profile(profile)["rotors"][rotor]["motion"]["direction"]), int)
            for direction in (0, -0.5, 0.5, -2, 2):
                profile = fixture()
                profile["rotors"][rotor]["motion"]["direction"]["value"] = direction
                self.rejected(profile)
            profile = fixture()
            profile["rotors"][rotor]["motion"]["slow_speed"]["value"] = 39.0
            self.rejected(profile, "slow speed")
            for command in ("stop", "brake", "Chorale", 0, None):
                profile = fixture()
                profile["rotors"][rotor]["initial_command"] = command
                self.rejected(profile)

    def test_phase_upper_endpoint_is_exclusive_for_each_rotor(self):
        for rotor in ROTORS:
            for phase in (0.0, -0.0, math.nextafter(math.tau, 0.0)):
                profile = fixture()
                profile["rotors"][rotor]["initial_state"]["angle"]["value"] = phase
                self.accepted(profile)
            for phase in (math.nextafter(0.0, -math.inf), math.tau, math.nextafter(math.tau, math.inf)):
                profile = fixture()
                profile["rotors"][rotor]["initial_state"]["angle"]["value"] = phase
                self.rejected(profile)

    def test_coordinate_components_and_vector_lengths_are_bounded(self):
        paths = [("rotors", r, "geometry", "axis_origin", "value") for r in ROTORS]
        paths += [("microphones", i, "position", "value") for i in range(2)]
        for path in paths:
            for axis in range(3):
                for value in (math.nextafter(-10.0, -math.inf), math.nextafter(10.0, math.inf)):
                    profile = fixture()
                    node_at(profile, path)[axis] = value
                    self.rejected(profile)
            for vector in ([], [0, 0], [0, 0, 0, 0], (0, 0, 0), "0,0,0"):
                profile = fixture()
                assign(profile, path, vector)
                self.rejected(profile)
        # Both signs of the coordinate endpoints can describe valid compact scenes.
        for edge in (-10.0, 10.0):
            profile = geometry_case()
            for r in ROTORS:
                profile["rotors"][r]["geometry"]["axis_origin"]["value"][0] = edge
            for m in profile["microphones"]:
                m["position"]["value"][0] = edge
            self.accepted(profile)

    def test_each_quantity_rejects_boolean_nonfinite_and_huge_numbers(self):
        for path in quantity_paths():
            for value in (True, False, float("nan"), float("inf"), -float("inf"), 10 ** 4000):
                with self.subTest(path=path, kind=type(value).__name__):
                    profile = fixture()
                    quantity = node_at(profile, path)
                    if isinstance(quantity["value"], list):
                        quantity["value"][0] = value
                    else:
                        quantity["value"] = value
                    self.rejected(profile)

    def test_all_authored_objects_are_closed_to_extra_members(self):
        for path in object_paths(FIXTURE):
            with self.subTest(path=path):
                profile = fixture()
                node_at(profile, path)["unexpected"] = 0
                self.rejected(profile, "expected exactly fields")

    def test_every_quantity_keeps_value_unit_and_complete_evidence(self):
        for path in quantity_paths():
            for key in ("value", "unit", "evidence"):
                profile = fixture()
                del node_at(profile, path)[key]
                self.rejected(profile)
            profile = fixture()
            node_at(profile, path)["unit"] = "arbitrary-units"
            self.rejected(profile)
            for key in ("evidence_class", "applicable_variant", "source_pages", "source_role",
                        "uncertainty", "measurement_reference", "reason"):
                profile = fixture()
                del node_at(profile, path)["evidence"][key]
                self.rejected(profile)

    def test_proposed_quantities_cannot_be_relabelled_as_measurements(self):
        for path in quantity_paths():
            for key, value in (("evidence_class", "measured"), ("applicable_variant", "Leslie-122"),
                               ("source_role", "measured-values"), ("uncertainty", 0.01),
                               ("measurement_reference", "invented-capture.wav"), ("reason", " ")):
                profile = fixture()
                node_at(profile, path)["evidence"][key] = value
                self.rejected(profile)

    def test_missing_physical_values_remain_null_with_acquisition_requirements(self):
        expected = {"selected_cabinet", "measured_rotor_geometry", "measured_rotor_speed",
                    "measured_transition_constants", "measured_directivity", "radiation_amplitude_scale",
                    "m6_input_transfer", "cabinet_room_microphone_response"}
        self.assertEqual(set(FIXTURE["unknowns"]), expected)
        for key in expected:
            self.assertIsNone(FIXTURE["unknowns"][key]["value"])
            for member, value in (("value", 0), ("value", "measured"), ("unit", "unspecified"),
                                  ("required_acquisition", "")):
                profile = fixture()
                profile["unknowns"][key][member] = value
                self.rejected(profile)
            profile = fixture()
            profile["unknowns"][key]["evidence"]["evidence_class"] = "proposed"
            self.rejected(profile)
            profile = fixture()
            del profile["unknowns"][key]
            self.rejected(profile)

    def test_source_pages_and_schema_version_have_exact_integer_types(self):
        for value in (1.0, True, "1", 2):
            profile = fixture()
            profile["schema_version"] = value
            self.rejected(profile)
        for path in quantity_paths():
            for mode in ("float", "bool", "wrong", "duplicate", "missing"):
                profile = fixture()
                pages = node_at(profile, path)["evidence"]["source_pages"]
                if mode == "float": pages[0] = float(pages[0])
                elif mode == "bool": pages[0] = True
                elif mode == "wrong": pages[0] += 1
                elif mode == "duplicate": pages.append(pages[0])
                else: pages.pop()
                self.rejected(profile)

    def test_model_frame_boundary_and_prehistory_are_not_silent_options(self):
        paths = [(key,) for key in ("model_id", "contract_id", "evidence_class", "applicable_variant")]
        paths += [("source", key) for key in FIXTURE["source"]]
        paths += [("coordinate_frame", key) for key in FIXTURE["coordinate_frame"]]
        paths += [("startup", key) for key in FIXTURE["startup"]]
        paths += [("signal_boundary", key) for key in ("input", "output", "directivity", "distance_gain")]
        for path in paths:
            profile = fixture()
            assign(profile, path, "unreviewed-alternative")
            self.rejected(profile)
        profile = fixture()
        profile["signal_boundary"]["omitted_effects"].remove("electrical-crossover")
        self.rejected(profile)
        for microphones in ([], list(reversed(FIXTURE["microphones"])),
                            [FIXTURE["microphones"][0]] * 2, FIXTURE["microphones"] * 2):
            profile = fixture()
            profile["microphones"] = copy.deepcopy(microphones)
            self.rejected(profile)

    def test_profile_identifiers_are_bounded_ascii_names(self):
        for identifier in ("a", "a" * 63, "rotary-test-1"):
            profile = fixture()
            profile["profile_id"] = identifier
            self.accepted(profile)
        for identifier in ("", "a" * 64, "A-profile", "1-profile", "test_id", "café", "a\n", "a\x00"):
            profile = fixture()
            profile["profile_id"] = identifier
            self.rejected(profile)

    def test_text_bounds_control_characters_and_unicode_are_explicit(self):
        path = ("speed_of_sound", "evidence", "reason")
        for reason in ("x" * 1024, "Calibración Δ 🎵 - still a proposal"):
            profile = fixture()
            assign(profile, path, reason)
            self.accepted(profile)
        for reason in ("x" * 1025, "\ud800", "\udfff", "", " \t ",
                       "valid\n", "A\x00B", "\x00", "A\x1fB"):
            profile = fixture()
            assign(profile, path, reason)
            self.rejected(profile)

    def test_resource_guards_reject_depth_collection_and_value_expansion(self):
        nested = 0
        for _ in range(18):
            nested = [nested]
        cases = ((nested, "nesting"), ([0] * 65, "oversized collection"),
                 ([[list(range(4)) for _ in range(64)] for _ in range(32)], "value-count"))
        for payload, message in cases:
            profile = fixture()
            profile["unexpected"] = payload
            self.rejected(profile, message)

    def test_cycles_and_non_json_python_values_reject_without_mutation(self):
        profile = fixture()
        profile["unexpected"] = profile
        self.rejected(profile, "cyclic")
        for value in (b"bytes", (1, 2), {1, 2}, object()):
            profile = fixture()
            profile["unexpected"] = value
            self.rejected(profile, "unsupported value type")
        profile = fixture()
        profile[1] = "non-string key"
        self.rejected(profile, "object names must be strings")

    def test_duplicate_json_members_reject_even_when_values_match(self):
        text = RAW.decode("utf-8")
        cases = (
            '{"schema_version":1,' + text.lstrip()[1:],
            text.replace('"unit": "m/s"', '"unit": "m/s", "unit": "m/s"', 1),
            text.replace('"schema_version": 1', '"schema_version": 1, "schema_versi\\u006fn": 1', 1),
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            for data in cases:
                path.write_text(data, encoding="utf-8")
                with self.assertRaisesRegex(admission.RotaryProfileError, "duplicate object key"):
                    admission.load_profile(path)

    def test_malformed_bytes_and_nonfinite_json_never_escape_as_unhandled_errors(self):
        text = RAW.decode("utf-8")
        cases = [b"", b"\xff", b"\xef\xbb\xbf" + RAW, b"{", b"{} trailing", b"[]", b"null",
                 b"[" * 1200 + b"0" + b"]" * 1200, b"\x00" + RAW]
        for token in ("NaN", "Infinity", "-Infinity", "1e99999", "9" * 6000, "true", "null"):
            cases.append(text.replace('"value": 343.0', '"value": ' + token, 1).encode("utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "invalid.json"
            for index, data in enumerate(cases):
                with self.subTest(case=index):
                    path.write_bytes(data)
                    with self.assertRaises(admission.RotaryProfileError):
                        admission.load_profile(path)

    def test_byte_limit_and_growth_after_metadata_check_are_bounded(self):
        limit = 128 * 1024
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bounded.json"
            exact = RAW + b" " * (limit - len(RAW))
            path.write_bytes(exact)
            self.assertEqual(admission.load_profile(path), FIXTURE)
            path.write_bytes(exact + b" ")
            with self.assertRaises(admission.RotaryProfileError):
                admission.load_profile(path)
            # A file can grow after fstat. The actual bounded read remains the guard.
            with mock.patch.object(admission.os, "fstat", return_value=SimpleNamespace(st_mode=stat.S_IFREG, st_size=len(RAW))):
                with self.assertRaisesRegex(admission.RotaryProfileError, "oversized file"):
                    admission.load_profile(path)

    def test_nonregular_descriptors_and_invalid_paths_reject_cleanly(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "regular.json"
            path.write_bytes(RAW)
            for mode in (stat.S_IFIFO, stat.S_IFDIR, stat.S_IFSOCK, stat.S_IFCHR):
                with mock.patch.object(admission.os, "fstat", return_value=SimpleNamespace(st_mode=mode, st_size=0)):
                    with self.assertRaisesRegex(admission.RotaryProfileError, "regular file"):
                        admission.load_profile(path)
            for invalid in (Path(temporary) / "missing", Path(temporary), "bad\x00path", None, 7, b"bytes"):
                with self.assertRaises(admission.RotaryProfileError):
                    admission.load_profile(invalid)

    def test_cli_success_reports_identity_and_creates_no_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "research Δ space.json"
            path.write_bytes(RAW)
            (root / "keep.txt").write_text("retained", encoding="utf-8")
            before = directory_fingerprint(root)
            result = self.run_cli(["--input", str(path), "--normalized"], root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "admitted")
            self.assertEqual(report["physical_status"], "unmeasured")
            self.assertEqual(report["source_file_sha256"], hashlib.sha256(RAW).hexdigest())
            self.assertEqual(report["normalized"], admission.normalized_profile(FIXTURE))
            self.assertEqual(directory_fingerprint(root), before)

    def test_cli_errors_are_json_nonzero_and_preserve_all_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "profile.json"
            (root / "existing-result.json").write_text("must remain", encoding="utf-8")
            for data in (b"{", b"\xff", RAW + b"x", b"{" + b'"x":0,' * 2 + b'"x":0}'):
                path.write_bytes(data)
                before = directory_fingerprint(root)
                result = self.run_cli(["--input", str(path)], root)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stderr, "")
                report = json.loads(result.stdout)
                self.assertEqual(report["status"], "rejected")
                self.assertTrue(report["error"])
                self.assertEqual(directory_fingerprint(root), before)

    def test_cli_argument_errors_and_explicit_help_have_declared_exits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for args in ([], ["--input"], ["--unknown"], ["--input", "missing.json"],
                         ["--input", str(PROFILE_PATH), "--output", "forbidden.json"]):
                result = self.run_cli(args, root)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["status"], "rejected")
                self.assertEqual(result.stderr, "")
                self.assertEqual(list(root.iterdir()), [])
            result = self.run_cli(["--help"], root)
            self.assertEqual(result.returncode, 0)
            self.assertIn("--input", result.stdout)
            self.assertEqual(result.stderr, "")

    def test_schema_references_are_local_and_object_shapes_are_closed(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        objects = 0
        for path in object_paths(schema):
            item = node_at(schema, path)
            if "$ref" in item:
                self.assertTrue(item["$ref"].startswith("#/"))
                target = schema
                for part in item["$ref"][2:].split("/"):
                    target = target[part.replace("~1", "/").replace("~0", "~")]
                self.assertIsInstance(target, dict)
            if item.get("type") == "object":
                objects += 1
                self.assertIs(item.get("additionalProperties"), False)
                self.assertEqual(set(item["required"]), set(item["properties"]))
        self.assertGreater(objects, 20)


def schema_audit_cases():
    yield "canonical synthetic fixture", fixture(), True, True
    # The initially published patterns admitted NUL via \S and a final newline
    # before $. Check every reason/acquisition path and the identifier itself.
    paths = [path + ("evidence", "reason") for path in quantity_paths()]
    for unknown in FIXTURE["unknowns"]:
        paths.extend((("unknowns", unknown, "evidence", "reason"),
                      ("unknowns", unknown, "required_acquisition")))
    for path in paths:
        for value in ("valid words\n", "A\x00B", "\x00", "   ", "x" * 1025):
            profile = fixture()
            assign(profile, path, value)
            yield f"text {path!r} {value[:12]!r}", profile, False, False
        profile = fixture()
        assign(profile, path, "Synthetic Δ evidence - no measurement")
        yield f"Unicode proposal {path!r}", profile, True, True
    for value in ("a\n", "A-profile", "a" * 64, "a\x00"):
        profile = fixture()
        profile["profile_id"] = value
        yield f"identifier {value[:12]!r}", profile, False, False
    for path in quantity_paths():
        profile = fixture()
        node_at(profile, path)["unit"] = "wrong-unit"
        yield f"unit {path!r}", profile, False, False
        profile = fixture()
        node_at(profile, path)["evidence"]["evidence_class"] = "measured"
        yield f"invented measurement {path!r}", profile, False, False
    for path in object_paths(FIXTURE):
        profile = fixture()
        node_at(profile, path)["unexpected"] = 0
        yield f"closed object {path!r}", profile, False, False
    # Explicitly retain the schema's documented semantic/lexical limitations.
    profile = fixture()
    profile["schema_version"] = 1.0
    yield "JSON Schema integral float versus exact metadata integer", profile, True, False
    profile = fixture()
    profile["rotors"]["horn"]["motion"]["slow_speed"]["value"] = 40.0
    yield "cross-field target ordering", profile, True, False
    profile = geometry_case()
    profile["microphones"][0]["position"]["value"] = [0.5, 0.0, 0.0]
    yield "full-orbit intersection", profile, True, False
    profile = geometry_case()
    profile["rotors"]["horn"]["initial_state"]["speed"]["value"] = 200.0
    yield "initial rim speed", profile, True, False


def run_schema_audit():
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("Optional --schema-audit requires an installed jsonschema; not run.", file=sys.stderr)
        return 2
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    failures = []
    count = 0
    for name, profile, expected_schema, expected_semantic in schema_audit_cases():
        count += 1
        actual_schema = validator.is_valid(profile)
        try:
            admission.validate_profile(profile)
            actual_semantic = True
        except admission.RotaryProfileError:
            actual_semantic = False
        if (actual_schema, actual_semantic) != (expected_schema, expected_semantic):
            failures.append({"case": name, "schema": actual_schema, "semantic": actual_semantic,
                             "expected_schema": expected_schema, "expected_semantic": expected_semantic})
    print(json.dumps({"status": "failed" if failures else "passed", "cases": count,
                      "jsonschema_version": importlib.metadata.version("jsonschema"),
                      "schema_sha256": hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest(),
                      "failures": failures}, sort_keys=True, allow_nan=False))
    return 1 if failures else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--schema-audit"]:
        sys.exit(run_schema_audit())
    unittest.main()
