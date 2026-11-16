#!/usr/bin/env python3
"""Bounded adversarial checks of version selection/retention, guards and limits."""
from __future__ import annotations

import argparse
import ast
import copy
from fractions import Fraction
import importlib.util
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace

from PIL import Image


ROOT = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


M = module("lower_v2_check", ROOT / "tools/compare_lower_rack_material.py")
OLD = module("lower_v1_snapshot", REPORTS / "A17-comparator-v1.py")
checks = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def refuses(name, function):
    try:
        function()
    except (ValueError, KeyError):
        checks.append(name)
    else:
        raise AssertionError(name + " unexpectedly accepted")


def functions(path):
    return {node.name: ast.dump(node, include_attributes=False)
            for node in ast.parse(path.read_text()).body if isinstance(node, ast.FunctionDef)}


def without_artifacts(result):
    return {key: value for key, value in result.items() if key != "failure_artifacts"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new JSON receipt; existing files are refused")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists")
    inputs = SimpleNamespace(repo=ROOT,
        before_percussion=ROOT.parent / "baseline/test_standalone_percussion_raster",
        after_percussion=ROOT.parent / "build-native/apps/standalone/test_standalone_percussion_raster",
        before_lower=ROOT.parent / "baseline/test_standalone_lower_rack_material_raster",
        after_lower=ROOT.parent / "build-native/apps/standalone/test_standalone_lower_rack_material_raster",
        before_painter=ROOT.parent / "baseline/InstrumentView.cpp",
        reference=ROOT / "docs/design/atlas-cover-reference.jpg",
        baseline_receipt=REPORTS / "lower-before-identity.json", build_dir=ROOT.parent / "build-native")
    identities = M.identities(inputs)
    mask = M.declare_mask()
    bindings, original = M.v2_bindings(ROOT, identities, mask)
    check("exact_independent_admission_and_immutable_v1_evidence", bindings["original_status"] == "failed")
    old_functions, new_functions = functions(REPORTS / "A17-comparator-v1.py"), functions(ROOT / "tools/compare_lower_rack_material.py")
    changed = [name for name in old_functions if old_functions[name] != new_functions[name]]
    check("only_original_compare_case_and_main_changed", changed == ["compare_case", "main"])
    check("all_original_35_threshold_code_unchanged", old_functions["reference_screens"] == new_functions["reference_screens"])
    check("default_compare_protocol_remains_v1", inspect.signature(M.compare_case).parameters["protocol"].default == M.PROTOCOL)
    check("exactly_three_admitted_rectangles_change", {name for name in M.PATCHES if M.PATCHES[name] != M.V2_PATCHES[name]} ==
          {"right", "right_top", "right_bottom"})
    for name in ("right", "right_top", "right_bottom"):
        old, new = M.PATCHES[name], M.V2_PATCHES[name]
        check(name + "_only_excludes_x1094_column", new == (old[0] + 1, old[1], old[2] - 1, old[3]))
    refuses("unknown_compare_protocol_refused_before_pixels", lambda: M.compare_case({}, None, None, {}, Path("."), protocol="v3"))

    # Each exact limit is checked both on its boundary and an arbitrarily small
    # amount beyond it. This catches widened limits and floating-rounding ties.
    constant = Image.new("RGB", (1672, 941), (50, 51, 52))
    stats = M.image_statistics_v2(constant)
    mutations = []
    for patch in M.PRIMARY:
        mutations.append((patch + "_mean_Yprime", (patch, "Yprime", None), "mean", Fraction(5, 2)))
        for channel, label in enumerate("RGB"):
            mutations.append((patch + "_mean_" + label, (patch, "RGB", channel), "mean", Fraction(3)))
    for patch in ("left", "right"):
        mutations.extend(((patch + "_residual_rms", (patch, "Yprime", None), "residual", Fraction(1, 2)),
                          (patch + "_slope_x", (patch, "Yprime", None), "slope_x", Fraction(3, 50)),
                          (patch + "_slope_y", (patch, "Yprime", None), "slope_y", Fraction(1, 40))))
    mutations.append(("right_minus_left", None, "right_minus_left", Fraction(7, 4)))
    rows = M.reference_screens_v2(stats, stats)["screens"]
    check("all_35_screen_names_and_limits_retained", [(row["name"], Fraction(str(row["maximum_error"]))) for row in rows] ==
          [(name, limit) for name, _, _, limit in mutations])
    for name, destination, field, limit in mutations:
        for beyond in (False, True):
            candidate = copy.deepcopy(stats)
            target = candidate if destination is None else candidate["patches"][destination[0]][destination[1]]
            if destination is not None and destination[2] is not None:
                target = target[destination[2]]
            if field == "residual":
                variance = limit * limit + (Fraction(1, 10**20) if beyond else 0)
                target["residual_variance_exact"], target["residual_rms"] = str(variance), float(variance)**.5
            else:
                value = Fraction(target[field + "_exact"]) + limit + (Fraction(1, 10**20) if beyond else 0)
                target[field + "_exact"], target[field] = str(value), float(value)
            result = M.reference_screens_v2(stats, candidate)
            check(name + ("_just_beyond_refused" if beyond else "_exact_boundary_accepted"),
                  (not result["passed"] and [row["name"] for row in result["failed_inequalities"]] == [name])
                  if beyond else result["passed"])
    bad_stats = copy.deepcopy(stats)
    bad_stats["patches"]["right"]["xywh"] = list(M.PATCHES["right"])
    refuses("v1_rectangle_cannot_be_labeled_v2", lambda: M.reference_screens_v2(stats, bad_stats))
    refuses("v1_reference_statistics_refused_for_v2", lambda: M.reference_screens_v2(M.image_statistics(constant), stats))

    # Guard corruptions include points outside the original three samples,
    # alpha-only changes, and equal-but-wrong source colors on both sides.
    guard_image = Image.new("RGBA", (1672, 941), (0, 0, 0, 255))
    guard_image.paste((36, 34, 30, 255), (1094, 311, 1095, 461))
    guard_image.paste((165, 228, 223, 255), (855, 492, 857, 500))
    guarded = M.v2_foreground_guards(guard_image, guard_image)
    check("complete_150_border_plus_16_focus_source_colors", guarded["passed"] and guarded["pixels"] == 166 and
          [row["before_source_color_pixels"] for row in guarded["guards"]] == [150, 16])
    check("middle_bottom_witness_remains_descriptive_contaminated", guarded["descriptive_annotation"]["source_focus_pixels"] == 16 and
          not guarded["descriptive_annotation"]["pure_material_sample"] and not guarded["descriptive_annotation"]["acceptance_patch"])
    for name, point, pixel, sides in (
        ("border_first_rgb", (1094, 311), (37, 34, 30, 255), ("after",)),
        ("border_outside_old_patches_alpha", (1094, 315), (36, 34, 30, 254), ("after",)),
        ("border_last_before", (1094, 460), (36, 35, 30, 255), ("before",)),
        ("border_equal_wrong_source_color", (1094, 312), (37, 34, 30, 255), ("before", "after")),
        ("focus_first_rgb", (855, 492), (166, 228, 223, 255), ("after",)),
        ("focus_last_alpha", (856, 499), (165, 228, 223, 254), ("after",)),
        ("focus_before", (856, 492), (165, 229, 223, 255), ("before",)),
        ("focus_equal_wrong_source_color", (855, 499), (166, 228, 223, 255), ("before", "after")),
    ):
        images = {"before": guard_image.copy(), "after": guard_image.copy()}
        for side in sides:
            images[side].putpixel(point, pixel)
        result = M.v2_foreground_guards(images["before"], images["after"])
        check(name + "_refused", not result["passed"] and sum(not row["passed"] for row in result["guards"]) == 1)
        if len(sides) == 2:
            check(name + "_refused_despite_exact_pair_equality", sum(row["different_pixels"] for row in result["guards"]) == 0)
    refuses("guard_resized_frame_refused", lambda: M.v2_foreground_guards(Image.new("RGBA", (1671, 941)), guard_image))
    refuses("guard_non_rgba_frame_refused", lambda: M.v2_foreground_guards(guard_image.convert("RGB"), guard_image))

    changed_identity = copy.deepcopy(identities)
    changed_identity["current_source_sha256"]["apps/standalone/InstrumentView.cpp"] = "0" * 64
    refuses("changed_painter_refused", lambda: M.v2_bindings(ROOT, changed_identity, mask))
    changed_identity = copy.deepcopy(identities)
    changed_identity["binaries"]["after_lower"]["sha256"] = "0" * 64
    refuses("changed_candidate_executable_refused", lambda: M.v2_bindings(ROOT, changed_identity, mask))
    changed_mask = copy.deepcopy(mask)
    changed_mask["cases"][1]["allowance_box"][2] += 1
    refuses("expanded_allowance_refused", lambda: M.v2_bindings(ROOT, identities, changed_mask))
    reproduced = copy.deepcopy(original)
    for case in reproduced["cases"]:
        case["v1_passed"] = case["passed"]
    check("retained_v1_reproduction_stays_failed", M.reproduce_v1_results(reproduced, original)["status"] == "failed")
    canonical_copy = next(case for case in reproduced["cases"] if (case["suite"], case["case"]) == ("lower", 28))
    canonical_copy["v1_passed"] = True
    refuses("fake_v1_pass_refused", lambda: M.reproduce_v1_results(reproduced, original))
    canonical_copy["v1_passed"] = False
    canonical_copy["after_reference_screens"]["screens"][0]["maximum_error"] = 3
    refuses("altered_retained_v1_threshold_refused", lambda: M.reproduce_v1_results(reproduced, original))

    with tempfile.TemporaryDirectory(prefix="A24-checker-selfcheck-") as temporary:
        temporary = Path(temporary)
        tampered = temporary / "retained-v1.json"
        tampered.write_text(json.dumps({**original, "status": "passed"}))
        saved = M.V1_REPORT
        try:
            M.V1_REPORT = str(tampered)
            refuses("tampered_retained_report_hash_refused", lambda: M.v2_bindings(ROOT, identities, mask))
        finally:
            M.V1_REPORT = saved
        cli = [sys.executable, "-B", str(ROOT / "tools/compare_lower_rack_material.py")]
        for name in ("before_percussion", "after_percussion", "before_lower", "after_lower", "before_painter"):
            cli += ["--" + name.replace("_", "-"), str(getattr(inputs, name))]
        destination = temporary / "never-created"
        invalid = subprocess.run([*cli, "--output-dir", str(destination), "--protocol", "lower-rack-material-v3"], capture_output=True, timeout=15)
        check("cli_unknown_version_refused_without_artifacts", invalid.returncode == 2 and b"invalid choice" in invalid.stderr and not destination.exists())
        destination.mkdir()
        refused = subprocess.run([*cli, "--output-dir", str(destination)], capture_output=True, timeout=15)
        check("cli_existing_output_refused_without_overwrite", refused.returncode == 2 and not list(destination.iterdir()))

        # A single real canonical pair verifies unchanged implicit/explicit v1
        # behavior against the frozen checker. The later A24 full run performs
        # all 98 cases; these two captures are only checker regression evidence.
        spec = next(case for case in mask["cases"] if (case["suite"], case["case"]) == ("lower", 28))
        before, after = M.frame(inputs.before_lower, 28, 45), M.frame(inputs.after_lower, 28, 45)
        with Image.open(inputs.reference) as image:
            reference, reference_v2 = M.image_statistics(image), M.image_statistics_v2(image)
        results = {}
        for name, comparator, keywords in (
            ("frozen_v1", OLD.compare_case, {}), ("implicit_v1", M.compare_case, {}),
            ("explicit_v1", M.compare_case, {"protocol": M.PROTOCOL}),
            ("explicit_v2", M.compare_case, {"protocol": M.V2_PROTOCOL, "reference_v2": reference_v2}),
        ):
            output = temporary / name
            output.mkdir()
            results[name] = comparator(spec, before, after, reference, output, **keywords)
        for name in ("implicit_v1", "explicit_v1"):
            check(name + "_exact_frozen_case_facts_and_failure", M.canonical_json(without_artifacts(results[name])) ==
                  M.canonical_json(without_artifacts(results["frozen_v1"])) and not results[name]["passed"])
            check(name + "_exact_five_failure_images", {key: value["sha256"] for key, value in results[name]["failure_artifacts"].items()} ==
                  {key: value["sha256"] for key, value in results["frozen_v1"]["failure_artifacts"].items()})
        versioned = results["explicit_v2"]
        check("explicit_v2_pass_keeps_v1_failed", versioned["passed"] and versioned["v1_passed"] is False and
              versioned["after_reference_screens"]["passed_inequalities"] == 33 and
              versioned["v2"]["after_reference_screens"]["passed_inequalities"] == 35)
        check("corrected_before_recomputed_six_of_35", versioned["v2"]["before_reference_screens"]["passed_inequalities"] == 6 and
              versioned["before_reference_screens"]["passed_inequalities"] == 7)
        check("canonical_v2_source_guards_pass", versioned["v2"]["foreground"]["passed"] and versioned["v2"]["foreground"]["pixels"] == 166)
        check("all_ten_original_patch_records_and_35_rows_retained", all(
            versioned[side + suffix] == results["frozen_v1"][side + suffix]
            for side in ("before", "after") for suffix in ("_statistics", "_reference_screens")))
        refuses("explicit_v2_missing_new_reference_refused", lambda: M.compare_case(spec, before, after, reference, temporary, protocol=M.V2_PROTOCOL))

    check("all_sources_executables_and_build_inputs_stable", M.identities(inputs) == identities)
    repeated, _ = M.v2_bindings(ROOT, identities, mask)
    check("admission_and_original_failure_evidence_stable", repeated == bindings)
    receipt = {"status": "passed", "scope": "Comparator adversarial checks plus one canonical regression pair; not full material/visual acceptance.",
               "checks": checks, "count": len(checks), "identities": identities, "v2_bindings": bindings,
               "selfcheck": M.file_identity(Path(__file__)), "unchanged_original_functions": len(old_functions) - 2,
               "canonical_case": {"v1_status": "failed", "v1_before_inequalities": 7, "v1_after_inequalities": 33,
                                  "v2_before_inequalities": 6, "v2_after_inequalities": 35, "guarded_pixels": 166},
               "temporary_images": "Deleted after hash comparison; original A17 evidence remains intact."}
    M.write_new(args.output, receipt)
    print(json.dumps({"status": "passed", "checks": len(checks), "output": str(args.output)}))


if __name__ == "__main__":
    main()
