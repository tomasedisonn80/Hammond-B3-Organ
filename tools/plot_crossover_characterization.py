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
import sys

import crossover_reference as reference


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "docs/development/2026-11-15-product-continuation/reports/crossover-response-acceptance.json"
RATES = (44100, 48000, 96000, 192000)
FREQUENCIES = (400.0, 800.0, 1600.0, 5000.0, 10000.0, 20000.0)
PORTS = ("treble_gain", "bass_gain", "input_admittance")
METRICS = ("magnitude_error_db", "phase_error_degrees", "normalized_complex_error")
FIGURE_ID = "leslie-crossover-same-hz-nominal-characterization-v1"


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


def observations(path: Path) -> tuple[dict, dict]:
    require(path.is_file() and path.stat().st_size <= 1024 * 1024,
            "acceptance report must be a regular file no larger than 1 MiB")
    raw = path.read_bytes()
    report = json.loads(raw, object_pairs_hook=unique_members, parse_constant=reject_number)
    require(report.get("schema_version") == 1 and report.get("acceptance_id") ==
            "leslie-crossover-native-nodal-acceptance-v1", "unsupported acceptance report")
    require(report.get("passed") is True and report.get("failures") == 0 and
            report.get("errors") == 0, "report does not retain a successful numerical gate")
    require(report.get("engine_integration") is False and
            report.get("physical_measurement_claim") is False,
            "report does not preserve the independent research boundary")
    require(report.get("same_hz_status") ==
            "characterized only; no audible acceptance threshold or physical fidelity claim",
            "same-Hz boundary differs")
    sources = report.get("source_sha256")
    require(isinstance(sources, dict) and "tools/crossover_reference.py" in sources and
            "data/crossover/leslie-122-ideal-v1.json" in sources, "missing source identities")
    for name, expected in sources.items():
        relative = Path(name)
        require(not relative.is_absolute() and ".." not in relative.parts,
                "source path escapes repository")
        require(isinstance(expected, str) and digest(ROOT / relative) == expected,
                f"source differs from retained acceptance: {name}")
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
    except (OSError, ValueError, KeyError, TypeError, ImportError, ArithmeticError) as error:
        print(f"plot_crossover_characterization: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
