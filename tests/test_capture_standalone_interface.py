#!/usr/bin/env python3
"""Validate retained native frames and reject synthetic painted-state mutations.

The eight positive fixtures are actual v3 application diagnostics. Mutations
exist only in copied Python dictionaries; no native process or image is edited.
All three final painted records are changed together so the new checks cannot
pass merely because the existing painted-record equality guard rejects them.
"""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
GALLERY = ROOT / "examples/demos/standalone-interface-preview-v3"
SPEC = importlib.util.spec_from_file_location("interface_capture", ROOT / "tools/capture_standalone_interface.py")
CAPTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAPTURE)
CASES = (
    ("play-reference-1672x941", 1672, 941, "play", "dimensional", 66),
    ("play-default-1280x900", 1280, 900, "play", "dimensional", 66),
    ("play-minimum-960x700", 960, 700, "play", "dimensional", 66),
    ("service-reference-1672x941", 1672, 941, "service", "dimensional", 66),
    ("service-minimum-960x700", 960, 700, "service", "dimensional", 66),
    ("rotary-reference-1672x941", 1672, 941, "rotary", "dimensional", 66),
    ("rotary-minimum-960x700", 960, 700, "rotary", "dimensional", 66),
    ("flat-minimum-960x700", 960, 700, "play", "flat", 68),
)
HELD = {"upper": 2, "lower": 1, "pedals": 1}
POINTER = {"sdl_captured": False, "ui_captured": False, "attempts": 0,
           "successes": 0, "losses": 0, "release_calls": 0}
MISSING = object()


class InterfaceCaptureValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.diagnostics = {
            case[0]: json.loads((GALLERY / "diagnostics" / f"{case[0]}.json").read_text(encoding="utf-8"))
            for case in CASES
        }

    def altered_painted(self, field, value):
        data = deepcopy(self.diagnostics[CASES[0][0]])
        for name in ("screenshot", "before_shutdown", "last_painted"):
            frame = data["presentation"][name]
            if value is MISSING:
                del frame[field]
            else:
                frame[field] = deepcopy(value)
        return data

    def reject(self, field, value, message):
        data = self.altered_painted(field, value)
        # The independently observed replay endpoint remains valid throughout.
        self.assertEqual(data["replay"]["before_shutdown"]["manual_notes"], [[60, 64], [67]])
        self.assertEqual(data["replay"]["before_shutdown"]["pedal_ids"], [3])
        with self.assertRaisesRegex(ValueError, message):
            CAPTURE.validate(data, *CASES[0][1:])

    def test_all_eight_retained_native_diagnostics_pass(self):
        for name, *arguments in CASES:
            with self.subTest(case=name):
                result = CAPTURE.validate(self.diagnostics[name], *arguments)
                self.assertIs(result["passed"], True)
                self.assertEqual(result["actual_painted_view"]["held_targets"], HELD)
                self.assertEqual(result["actual_painted_view"]["pointer_capture"], POINTER)

    def backend_record(self, available, backend, state):
        # Contract variants are copied diagnostics, not newly observed captures.
        data = deepcopy(self.diagnostics[CASES[0][0]])
        data["midi"].update(backend_available=available, backend=backend,
                            state_before_shutdown=state, state_after_shutdown=state)
        return data

    def test_consistent_compiled_backend_facts_choose_the_exact_inert_state(self):
        for available, backend, state in ((False, "unavailable", "unavailable"),
                                          (True, "ALSA", "closed"),
                                          (True, "CoreMIDI", "closed"),
                                          (True, "WinMM", "closed")):
            with self.subTest(available=available, backend=backend):
                data = self.backend_record(available, backend, state)
                result = CAPTURE.validate(data, *CASES[0][1:])
                self.assertIs(result["passed"], True)
                self.assertIs(result["midi_backend_available"], available)
                self.assertEqual(result["midi_backend"], backend)
                self.assertEqual(result["midi_state"], state)

    def test_missing_malformed_or_contradictory_backend_facts_are_rejected(self):
        invalid = (
            ("backend_available", MISSING), ("backend_available", None),
            ("backend_available", 0), ("backend_available", 1),
            ("backend_available", "false"), ("backend_available", "true"),
            ("backend_available", []), ("backend_available", {}),
            ("backend", MISSING), ("backend", None), ("backend", True),
            ("backend", 0), ("backend", []), ("backend", {}),
            ("backend", ""), ("backend", "JACK"), ("backend", "alsa"),
        )
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            for field, value in (*invalid, ("backend", "unavailable" if available else "ALSA")):
                with self.subTest(available=available, field=field, value=value):
                    data = self.backend_record(available, backend, state)
                    if value is MISSING:
                        del data["midi"][field]
                    else:
                        data["midi"][field] = value
                    with self.assertRaisesRegex(ValueError, "compiled MIDI backend facts"):
                        CAPTURE.validate(data, *CASES[0][1:])

    def test_both_midi_states_must_match_the_compiled_backend(self):
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            wrong_states = (MISSING, None, False, 0, [], {}, "open", "faulted", "closing", "",
                            "unavailable" if available else "closed")
            for fields in (("state_before_shutdown",), ("state_after_shutdown",),
                           ("state_before_shutdown", "state_after_shutdown")):
                for value in wrong_states:
                    with self.subTest(available=available, fields=fields, value=value):
                        data = self.backend_record(available, backend, state)
                        for field in fields:
                            if value is MISSING:
                                del data["midi"][field]
                            else:
                                data["midi"][field] = value
                        with self.assertRaisesRegex(ValueError, "state differs from the declared compiled backend"):
                            CAPTURE.validate(data, *CASES[0][1:])

    def test_neither_backend_mode_allows_port_or_device_activity(self):
        mutations = (("source", "native"), ("source", "synthetic-replay"),
                     ("generation", 1), ("generation", False), ("generation", 0.0),
                     ("opened_port_index", 1), ("opened_port_index", False), ("opened_port_index", 0.0),
                     ("requested_port", "controller"), ("port_name", "controller"),
                     ("active_before_shutdown", True), ("active_before_shutdown", 0))
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            for field, value in mutations:
                with self.subTest(available=available, field=field, value=value):
                    data = self.backend_record(available, backend, state)
                    data["midi"][field] = value
                    with self.assertRaisesRegex(ValueError, "opened/enumerated a native MIDI device"):
                        CAPTURE.validate(data, *CASES[0][1:])
            data = self.backend_record(available, backend, state)
            data["midi_replay"] = {}
            with self.subTest(available=available, field="midi_replay"):
                with self.assertRaisesRegex(ValueError, "opened/enumerated a native MIDI device"):
                    CAPTURE.validate(data, *CASES[0][1:])

    def test_device_and_discovery_facts_must_be_complete_typed_and_inert(self):
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            for group in ("device", "discovery"):
                original = self.diagnostics[CASES[0][0]]["midi"][group]
                for field, expected in original.items():
                    wrong_values = (MISSING, True, 0, None) if type(expected) is bool else (MISSING, 1, -1, False, 0.0, "0", None)
                    for value in wrong_values:
                        with self.subTest(available=available, group=group, field=field, value=value):
                            data = self.backend_record(available, backend, state)
                            if value is MISSING:
                                del data["midi"][group][field]
                            else:
                                data["midi"][group][field] = value
                            with self.assertRaisesRegex(ValueError, "opened/enumerated a native MIDI device"):
                                CAPTURE.validate(data, *CASES[0][1:])
                for value in (MISSING, None, {}, [], {**original, "other": 0}):
                    with self.subTest(available=available, group=group, value=value):
                        data = self.backend_record(available, backend, state)
                        if value is MISSING:
                            del data["midi"][group]
                        else:
                            data["midi"][group] = value
                        with self.assertRaisesRegex(ValueError, "opened/enumerated a native MIDI device"):
                            CAPTURE.validate(data, *CASES[0][1:])

    def test_midi_shutdown_remains_strict_in_both_backend_modes(self):
        for available, backend, state in ((True, "ALSA", "closed"), (False, "unavailable", "unavailable")):
            for field, expected in (("quiescent_after_shutdown", True), ("diagnostics_stable_after_shutdown", True),
                                    ("active_after_shutdown", False), ("shutdown_failed", False), ("startup_failed", False)):
                for value in (not expected, int(expected), None):
                    with self.subTest(available=available, field=field, value=value):
                        data = self.backend_record(available, backend, state)
                        data["midi"][field] = value
                        with self.assertRaisesRegex(ValueError, "MIDI shutdown was not clean and quiescent"):
                            CAPTURE.validate(data, *CASES[0][1:])

    def test_wrong_painted_hold_counts_are_rejected_despite_valid_endpoint(self):
        for division, count in HELD.items():
            for value in (count - 1, count + 1, -1):
                with self.subTest(division=division, value=value):
                    self.reject("held_targets", {**HELD, division: value}, "actual painted held targets")

    def test_painted_hold_counts_require_integers_without_boolean_coercion(self):
        for division, count in HELD.items():
            for value in (True, float(count), str(count), None):
                with self.subTest(division=division, value=value):
                    self.reject("held_targets", {**HELD, division: value}, "actual painted held targets")

    def test_missing_or_extra_painted_holds_are_rejected(self):
        for value in (MISSING, None, {}, [2, 1, 1], {"upper": 2, "lower": 1}, {**HELD, "other": 0}):
            with self.subTest(value=value):
                self.reject("held_targets", value, "actual painted held targets")

    def test_pointer_capture_activity_is_rejected_for_keyboard_only_replay(self):
        for field in POINTER:
            value = True if field in ("sdl_captured", "ui_captured") else 1
            with self.subTest(field=field):
                self.reject("pointer_capture", {**POINTER, field: value}, "unexpected pointer capture")

    def test_pointer_flags_and_counters_preserve_boolean_and_integer_types(self):
        for field in ("sdl_captured", "ui_captured"):
            for value in (0, "false", None):
                with self.subTest(field=field, value=value):
                    self.reject("pointer_capture", {**POINTER, field: value}, "unexpected pointer capture")
        for field in ("attempts", "successes", "losses", "release_calls"):
            for value in (False, 0.0, "0", None):
                with self.subTest(field=field, value=value):
                    self.reject("pointer_capture", {**POINTER, field: value}, "unexpected pointer capture")

    def test_missing_or_extra_capture_facts_are_rejected(self):
        missing_counter = {key: value for key, value in POINTER.items() if key != "release_calls"}
        for value in (MISSING, None, {}, missing_counter, {**POINTER, "other": 0}):
            with self.subTest(value=value):
                self.reject("pointer_capture", value, "unexpected pointer capture")


if __name__ == "__main__":
    unittest.main()
