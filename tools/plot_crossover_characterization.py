#!/usr/bin/env python3
"""Plot retained same-Hz crossover observations; this is not an acceptance gate.

Requires the existing optional Matplotlib authoring dependency. No native
process is launched, no response sweep is repeated, and no audio is generated.
The six plotted frequencies are the retained nominal-load checkpoints; lines
join those samples and do not assert an interpolated continuous error bound.
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path
import re
import sys

import crossover_reference as reference


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "docs/development/2026-11-15-product-continuation/reports/crossover-response-acceptance.json"
RATES = (44100, 48000, 96000, 192000)
FREQUENCIES = (400.0, 800.0, 1600.0, 5000.0, 10000.0, 20000.0)
PORTS = ("treble_gain", "bass_gain", "input_admittance")
METRICS = ("magnitude_error_db", "phase_error_degrees", "normalized_complex_error")
FIGURE_ID = "leslie-crossover-same-hz-nominal-characterization-v1"
LOADS = ((16.0, 16.0), (1.0, 1.0), (1024.0, 1024.0),
         (1.0, 1024.0), (1024.0, 1.0), (8.0, 32.0))
SOURCE_PATHS = {
    "tools/crossover_probe.cpp", "tools/crossover_reference.py",
    "tests/test_crossover_acceptance.py", "include/hammond/LeslieCrossover.h",
    "src/LeslieCrossover.cpp", "data/crossover/leslie-122-ideal-v1.json",
}
REPORT_FIELDS = {
    "schema_version", "acceptance_id", "passed", "tests_run", "failures", "errors",
    "platform", "python", "binary_sha256", "source_sha256", "provenance_boundary",
    "subprocesses", "response_port_comparisons", "sine_port_comparisons",
    "maximum_warped_response_error", "maximum_warped_sine_error",
    "maximum_response_residual", "maximum_independent_sine_tail_gain_bound",
    "maximum_half_window_gain_difference", "limits", "same_hz_status",
    "physical_measurement_claim", "engine_integration", "response_groups", "sine_groups",
}
RESPONSE_LIMIT = 2.0e-10
SINE_LIMIT = 2.0e-8
MAX_REPORT_BYTES = 1024 * 1024


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_members(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON member: {key}")
        result[key] = value
    return result


def reject_number(value: str) -> None:
    raise ValueError(f"nonfinite JSON number: {value}")


def fields(value: object, expected: set[str], where: str) -> None:
    require(type(value) is dict and set(value) == expected, f"{where}: fields differ")


def number(value: object, where: str, lower: float = 0.0,
           upper: float = sys.float_info.max) -> None:
    require(type(value) in (int, float) and lower <= value <= upper,
            f"{where}: expected finite number in [{lower}, {upper}]")


def count(value: object, expected: int, where: str) -> None:
    require(type(value) is int and value == expected, f"{where}: expected integer {expected}")


def sha256(value: object, where: str) -> None:
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
            f"{where}: expected lowercase SHA-256 identity")


def validate_report(report: object) -> None:
    """Admit a complete v1 record, without asserting source-to-binary attestation.

    These are the frozen producer's counts, limits and experiment families.
    Internal consistency and matching input hashes cannot authenticate invented
    numerical observations; the original execution record remains necessary.
    """
    fields(report, REPORT_FIELDS, "acceptance report")
    count(report["schema_version"], 1, "schema_version")
    require(report["acceptance_id"] ==
            "leslie-crossover-native-nodal-acceptance-v1", "unsupported acceptance report")
    require(report["passed"] is True, "report does not retain a successful numerical gate")
    for name, expected in (("tests_run", 3), ("failures", 0), ("errors", 0)):
        count(report[name], expected, name)
    require(report["engine_integration"] is False and
            report["physical_measurement_claim"] is False,
            "report does not preserve the independent research boundary")
    require(report["same_hz_status"] ==
            "characterized only; no audible acceptance threshold or physical fidelity claim",
            "same-Hz boundary differs")
    require(report["provenance_boundary"] ==
            "Observed immutable inputs, not an independent compiler/source-to-binary attestation",
            "provenance boundary differs")
    for name in ("platform", "python"):
        require(type(report[name]) is str and 0 < len(report[name]) <= 512,
                f"{name}: expected bounded nonempty text")
    sha256(report["binary_sha256"], "binary_sha256")
    sources = report["source_sha256"]
    fields(sources, SOURCE_PATHS, "source_sha256")
    for name, expected in sources.items():
        sha256(expected, name)
        require(digest(ROOT / name) == expected,
                f"source differs from retained acceptance: {name}")
    fields(report["limits"], {"warped_response", "settled_sine"}, "limits")
    for name, expected in (("warped_response", RESPONSE_LIMIT), ("settled_sine", SINE_LIMIT)):
        number(report["limits"][name], f"limits.{name}", expected, expected)
    for name, limit in (("maximum_warped_response_error", RESPONSE_LIMIT),
                        ("maximum_warped_sine_error", SINE_LIMIT),
                        ("maximum_response_residual", 1.0e-12),
                        ("maximum_independent_sine_tail_gain_bound", SINE_LIMIT / 100.0),
                        ("maximum_half_window_gain_difference", SINE_LIMIT)):
        number(report[name], name, upper=limit)

    groups = report["response_groups"]
    expected_groups = {(rate, *loads) for rate in RATES for loads in LOADS}
    require(type(groups) is list and len(groups) == len(expected_groups),
            "response_groups: expected 24 rate/load groups")
    seen = set()
    response_comparisons = 0
    maximum_response = 0.0
    for group in groups:
        fields(group, {"sample_rate_hz", "treble_ohms", "bass_ohms", "frequencies",
                       "maximum_warped_normalized_errors", "same_hz_10_to_20000_maximum_absolute_errors",
                       "nominal_same_hz_points"}, "response group")
        rate = group["sample_rate_hz"]
        require(type(rate) is int and rate in RATES, "unsupported response sample rate")
        for name in ("treble_ohms", "bass_ohms"):
            number(group[name], name, 1.0, 1024.0)
        key = (rate, group["treble_ohms"], group["bass_ohms"])
        require(key in expected_groups and key not in seen, "duplicate or unsupported response load group")
        seen.add(key)
        frequencies = set(reference.default_frequency_grid()) | set(FREQUENCIES) | {
            0.0, 1.0e-8, rate * 0.499999, math.nextafter(rate / 2.0, 0.0)}
        count(group["frequencies"], len(frequencies), "response frequencies")
        response_comparisons += len(frequencies) * len(PORTS)
        maxima = group["maximum_warped_normalized_errors"]
        fields(maxima, set(PORTS), "warped response maxima")
        for port in PORTS:
            number(maxima[port], f"warped response {port}", upper=RESPONSE_LIMIT)
        maximum_response = max(maximum_response, *maxima.values())
        same_hz = group["same_hz_10_to_20000_maximum_absolute_errors"]
        fields(same_hz, set(PORTS), "same-Hz maxima")
        for port in PORTS:
            fields(same_hz[port], set(METRICS), f"same-Hz maxima {port}")
            for metric in METRICS:
                upper = 180.0 if metric == "phase_error_degrees" else sys.float_info.max
                number(same_hz[port][metric], f"same-Hz maximum {metric}", upper=upper)
        rows = group["nominal_same_hz_points"]
        expected_points = len(FREQUENCIES) if key[1:] == (16.0, 16.0) else 0
        require(type(rows) is list and len(rows) == expected_points, "nominal point count differs")
        for frequency, row in zip(FREQUENCIES, rows):
            fields(row, {"frequency_hz", "same_hz_errors"}, "nominal point")
            number(row["frequency_hz"], "nominal frequency", frequency, frequency)
            fields(row["same_hz_errors"], set(PORTS), "nominal ports")
            for port in PORTS:
                values = row["same_hz_errors"][port]
                fields(values, set(METRICS), f"nominal {port}")
                for metric in METRICS:
                    lower = 0.0 if metric == "normalized_complex_error" else -sys.float_info.max
                    number(values[metric], f"nominal {metric}", lower)
                    require(abs(values[metric]) <= same_hz[port][metric],
                            "nominal metric exceeds retained same-Hz maximum")
    require(seen == expected_groups, "missing response rate/load group")
    count(report["response_port_comparisons"], response_comparisons, "response_port_comparisons")
    require(report["maximum_warped_response_error"] == maximum_response, "response summary maximum differs")

    sines = report["sine_groups"]
    expected_sines = {(rate, *loads, frequency) for rate in RATES for loads in LOADS
                      for frequency in (400.125, 800.0, 1600.375, 0.43 * rate)}
    require(type(sines) is list and len(sines) == len(expected_sines), "sine_groups: expected 96 experiments")
    seen = set()
    summaries = {"maximum_warped_sine_error": ("maximum_warped_normalized_error", SINE_LIMIT),
                 "maximum_independent_sine_tail_gain_bound": ("independent_all_fit_tail_bound", SINE_LIMIT / 100.0),
                 "maximum_half_window_gain_difference": ("half_window_max_difference", SINE_LIMIT)}
    for group in sines:
        fields(group, {"sample_rate_hz", "treble_ohms", "bass_ohms", "frequency_hz", "warmup_frames",
                       "independent_largest_pole_modulus", *(name for name, _ in summaries.values())}, "sine group")
        rate = group["sample_rate_hz"]
        require(type(rate) is int and rate in RATES, "unsupported sine sample rate")
        for name in ("treble_ohms", "bass_ohms"):
            number(group[name], name, 1.0, 1024.0)
        number(group["frequency_hz"], "sine frequency", 0.0, rate / 2.0)
        key = (rate, group["treble_ohms"], group["bass_ohms"], group["frequency_hz"])
        require(key in expected_sines and key not in seen, "duplicate or unsupported sine experiment")
        seen.add(key)
        require(type(group["warmup_frames"]) is int and 0 <= group["warmup_frames"] <= 2_000_000,
                "sine warmup_frames: expected bounded integer")
        number(group["independent_largest_pole_modulus"], "sine pole modulus", 0.0, 1.0)
        require(0.0 < group["independent_largest_pole_modulus"] < 1.0, "sine pole must strictly decay")
        for name, limit in summaries.values():
            number(group[name], name, upper=limit)
    require(seen == expected_sines, "missing sine experiment")
    for summary, (name, _) in summaries.items():
        require(report[summary] == max(group[name] for group in sines), f"{summary}: summary differs")
    count(report["sine_port_comparisons"], len(sines) * 3 * len(PORTS), "sine_port_comparisons")
    # v1 runs one process per response/sine group plus 33 refusal experiments.
    count(report["subprocesses"], len(groups) + len(sines) + 33, "subprocesses")


def observations(path: Path) -> tuple[dict, dict]:
    require(path.is_file(), "acceptance report must be a regular file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_REPORT_BYTES + 1)
    require(len(raw) <= MAX_REPORT_BYTES, "acceptance report must be no larger than 1 MiB")
    report = json.loads(raw, object_pairs_hook=unique_members, parse_constant=reject_number)
    validate_report(report)
    sources = report["source_sha256"]
    network = reference.load_network()
    analog = {frequency: reference.nodal_response(network, frequency)
              for frequency in FREQUENCIES}
    selected = {}
    for group in report["response_groups"]:
        if (group["treble_ohms"], group["bass_ohms"]) != (16.0, 16.0):
            continue
        rate = group["sample_rate_hz"]
        require(type(rate) is int and rate in RATES and rate not in selected,
                "duplicate or unsupported nominal sample rate")
        rows = group["nominal_same_hz_points"]
        require(tuple(row["frequency_hz"] for row in rows) == FREQUENCIES,
                "retained nominal frequencies differ")
        selected[rate] = []
        for row in rows:
            frequency = row["frequency_hz"]
            require(set(row["same_hz_errors"]) == set(PORTS), "retained ports differ")
            ports = {}
            for name in PORTS:
                values = row["same_hz_errors"][name]
                require(set(values) == set(METRICS), "retained metrics differ")
                require(all(type(v) in (int, float) and math.isfinite(v)
                            for v in values.values()), "invalid retained metric")
                require(values["normalized_complex_error"] >= 0,
                        "negative normalized complex error")
                require(-180.0 <= values["phase_error_degrees"] <= 180.0,
                        "retained phase is not a principal difference")
                expected = getattr(analog[frequency], name)
                absolute = values["normalized_complex_error"] * max(1.0, abs(expected))
                ratio = cmath.rect(10.0 ** (values["magnitude_error_db"] / 20.0),
                                   math.radians(values["phase_error_degrees"]))
                reconstructed = expected * ratio
                require(abs(abs(reconstructed - expected) - absolute) <=
                        2.0e-12 * max(1.0, abs(expected)),
                        "retained magnitude/phase and complex error disagree")
                ports[name] = {**values, "absolute_complex_error": absolute,
                               "analog_magnitude": abs(expected),
                               "digital_magnitude": abs(reconstructed)}
            selected[rate].append({"frequency_hz": frequency, "ports": ports})
    require(set(selected) == set(RATES), "missing nominal sample rate")
    metadata = {"figure_id": FIGURE_ID,
                "acceptance_report_sha256": hashlib.sha256(raw).hexdigest(),
                "binary_sha256": report["binary_sha256"],
                "source_sha256": sources, "plotter_sha256": digest(Path(__file__)),
                "loads_ohm": {"treble": 16.0, "bass": 16.0},
                "points_per_rate": len(FREQUENCIES),
                "boundary": "Retained same-Hz electrical observations; no audible or physical acceptance",
                "observations": selected}
    return selected, metadata


def plot(selected: dict, metadata: dict, output: Path) -> None:
    # Import only after input admission. Headless authoring creates no UI and
    # adds no dependency to the native model, ordinary CTest or installed tools.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, FixedFormatter

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": "#f8fafc", "axes.facecolor": "white"})
    fig, axes = plt.subplots(2, 2, figsize=(12.0, 8.2))
    panels = (("bass_gain", "magnitude_error_db", "Bass: relative magnitude change", "Digital / analog (dB)"),
              ("treble_gain", "phase_error_degrees", "Treble: phase difference", "Digital minus analog (degrees)"),
              ("bass_gain", "absolute_complex_error", "Bass: absolute complex error", "|H digital − H analog| (V/V)"),
              ("treble_gain", "absolute_complex_error", "Treble: absolute complex error", "|H digital − H analog| (V/V)"))
    colors = ("#b45309", "#2563eb", "#15803d", "#7e22ce")
    for ax, (port, metric, title, ylabel) in zip(axes.flat, panels):
        for rate, color in zip(RATES, colors):
            y = [row["ports"][port][metric] for row in selected[rate]]
            ax.plot(FREQUENCIES, y, marker="o", markersize=4, linewidth=1.7,
                    color=color, label=f"{rate / 1000:g} kHz")
        ax.set_xscale("log")
        ax.set_xlim(340, 24000)
        ax.xaxis.set_major_locator(FixedLocator(FREQUENCIES))
        ax.xaxis.set_major_formatter(FixedFormatter(("0.4", "0.8", "1.6", "5", "10", "20")))
        if metric == "absolute_complex_error":
            ax.set_yscale("log")
        else:
            ax.axhline(0, color="#64748b", linewidth=.8, alpha=.6)
        ax.set_title(title, loc="left", weight="bold", pad=10)
        ax.set_xlabel("Same electrical frequency (kHz)")
        ax.set_ylabel(ylabel)
        ax.grid(True, which="major", color="#cbd5e1", linewidth=.6, alpha=.8)
        ax.tick_params(axis="both", which="major", labelsize=9)
    fig.suptitle("Ideal Leslie crossover: same-Hz differences remain", x=.055, y=.975,
                 ha="left", fontsize=18, weight="bold", color="#0f172a")
    fig.text(.055, .935,
             "16 Ω resistors • endpoint trapezoidal v1 • six retained checkpoints per rate",
             fontsize=11, color="#475569")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.53, .913),
               ncol=4, frameon=False)
    fig.subplots_adjust(left=.10, right=.975, top=.835, bottom=.13, hspace=.45, wspace=.29)
    fig.text(.055, .067,
             "At 20 kHz the analog bass gain is already −60.225 dB. Relative dB and absolute port error answer different questions.",
             fontsize=9.3, color="#334155")
    fig.text(.055, .039,
             "Markers are observed samples; joining lines are guides. No audible threshold, hardware match, or Engine connection is asserted.",
             fontsize=9.1, color="#475569")
    metadata["matplotlib_version"] = matplotlib.__version__
    fig.savefig(output, dpi=150, format="png",
                metadata={"Title": FIGURE_ID,
                          "Description": json.dumps(metadata, sort_keys=True, separators=(",", ":"), allow_nan=False)})
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance-report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--output", type=Path, required=True, help="new PNG file")
    args = parser.parse_args()
    try:
        require(args.output.suffix.lower() == ".png", "output must be a PNG file")
        require(not args.output.exists() and not args.output.is_symlink(), "output already exists")
        require(args.output.parent.is_dir(), "output parent directory does not exist")
        selected, metadata = observations(args.acceptance_report)
        plot(selected, metadata, args.output)
        print(json.dumps({"figure_id": FIGURE_ID, "output": str(args.output),
                          "output_sha256": digest(args.output),
                          "acceptance_report_sha256": metadata["acceptance_report_sha256"],
                          "rates": list(RATES), "retained_points": len(RATES) * len(FREQUENCIES),
                          "native_processes_launched": 0, "audible_acceptance": "not declared"},
                         sort_keys=True, allow_nan=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError, ArithmeticError, RecursionError) as error:
        print(f"plot_crossover_characterization: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
