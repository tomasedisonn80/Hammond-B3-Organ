#!/usr/bin/env python3
"""Run the fixed synthetic contact-switching-validation-v1 experiment.

The complete 36-fixture/four-factor matrix has no subset, tolerance, gain,
alignment, or budget overrides. Results qualify the stated finite reference
and 64 continuous probes only; neither physical fidelity nor a live Engine.
"""

from __future__ import annotations

import time

_SCRIPT_STARTED = time.perf_counter()

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import stat
import struct
import subprocess
import sys
import tempfile

import contact_switching_io as admitted_io
import contact_switching_oracle as oracle
import fractional_contact_reference as candidate


STUDY_ID = "contact-switching-validation-v1"
FACTORS = (32, 64, 128, 256)
RATES = (44100, 48000, 96000)
FREQUENCIES = tuple(j / 256 for j in range(257)) + (1.5, 2.0)
CAPS = {"elapsed_seconds": 300, "peak_resident_bytes": 256 * 1024 * 1024,
        "fir_products": 180_000_000, "oracle_integrand_evaluations": 10_000_000,
        "report_bytes": 32 * 1024 * 1024, "invocation_work": 20_000_000}
FROZEN = {
    "docs/FRACTIONAL_CONTACT_REFERENCE.md": "3c05da4c3f35fcdc53fac05f1592ddc97e444f5038d9c147afae71f46e8deecd",
    "docs/CONTACT_SWITCHING_VALIDATION.md": "5ccbba4d08a2272bef4f7d553446a7ca9582e289fba80f9bcfa223a2d6efb2b5",
    "manifest.json": "b80db78bb8477b683bfd2cc1013a0b600c45e8f20b7fc08f75c5efe6e10a22ec",
    "probes.json": "fdcdf6430c008cd28367d3c02f125af2a37ac55ebbe875361fba2549295e7026",
}
SOURCE_FILES = (
    "tools/fractional_contact_reference.py", "tools/contact_switching_io.py",
    "tools/contact_switching_reference.py", "tools/contact_switching_oracle.py",
    "tools/contact_switching_study.py", "tools/make_contact_switching_fixtures.py",
)
LIMITS = {
    "oracle_refinement": {"peak_B": 1e-9, "nrmse": 1e-7},
    "high_rate_convergence": {"peak_B": 6e-5, "nrmse": 3e-5},
    "independent_reference": {"peak_B": 2e-5, "nrmse": 1e-5},
}


class Incomplete(RuntimeError):
    """A retained experiment cannot receive a complete numerical/resource grade."""


@dataclass(frozen=True)
class Fixture:
    name: str
    raw: dict
    document: admitted_io.InputDocument
    path: oracle.OracleTrajectory
    indices: tuple[int, ...]


@dataclass(frozen=True)
class Admission:
    root: Path
    fixture_root: Path
    fixtures: tuple[Fixture, ...]
    files: dict[str, dict]
    paths: tuple[Path, ...]
    fir_products: int


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read(path: Path, maximum: int = 256 * 1024) -> bytes:
    information = path.stat()
    if not stat.S_ISREG(information.st_mode) or information.st_size > maximum:
        raise ValueError(f"required bounded regular file: {path.name}")
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError(f"input grew beyond its byte cap: {path.name}")
    return data


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def _json(data: bytes):
    return json.loads(data.decode("utf-8"), object_pairs_hook=_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def admit_inputs(fixture_root: Path, *, root: Path | None = None) -> Admission:
    """Read and admit every fixed input before numerical render allocation."""
    root = Path(__file__).resolve().parent.parent if root is None else Path(root).resolve(strict=True)
    for module, name in ((candidate, "fractional_contact_reference.py"),
                         (oracle, "contact_switching_oracle.py"),
                         (admitted_io, "contact_switching_io.py")):
        if Path(module.__file__).resolve() != (root / "tools" / name).resolve(strict=True):
            raise ValueError("loaded numerical module differs from the identified source root")
    fixture_root = Path(fixture_root).resolve(strict=True)
    if not fixture_root.is_dir():
        raise ValueError("fixtures must name a directory")
    files, paths, content = {}, [], {}
    for name in SOURCE_FILES + tuple(k for k in FROZEN if k.startswith("docs/")):
        path = root / name
        data = _read(path)
        files[name] = {"sha256": _sha(data), "bytes": len(data)}
        paths.append(path)
        if name in FROZEN and files[name]["sha256"] != FROZEN[name]:
            raise ValueError(f"frozen contract differs: {name}")
    for name in ("manifest.json", "probes.json"):
        path = fixture_root / name
        data = _read(path)
        if _sha(data) != FROZEN[name]:
            raise ValueError(f"frozen {name} differs")
        files["fixtures/" + name] = {"sha256": _sha(data), "bytes": len(data)}
        paths.append(path)
        content[name] = _json(data)
    manifest, probes = content["manifest.json"], content["probes.json"]
    names = tuple(f"F{number:02d}-{rate}-v1.json" for number in range(12) for rate in RATES)
    if (manifest["protocol_id"] != STUDY_ID or manifest["fixture_count"] != 36
            or set(manifest["files"]) != set(names) or set(probes["fixtures"]) != set(names)
            or probes["fixture_manifest_sha256"] != FROZEN["manifest.json"]
            or probes["oracle_source_sha256"] != files["tools/contact_switching_oracle.py"]["sha256"]):
        raise ValueError("fixed fixture/probe/source identity mismatch")
    fixtures, products = [], 0
    for name in names:
        path = fixture_root / name
        data = _read(path)
        expected = manifest["files"][name]
        if len(data) != expected["bytes"] or _sha(data) != expected["sha256"]:
            raise ValueError(f"frozen fixture differs: {name}")
        document = admitted_io.parse_input(data)
        raw = _json(data)
        if raw["frames"] != 256 or document.fixture_id != name[:-5]:
            raise ValueError(f"fixed observation/fixture identity differs: {name}")
        path_state = oracle.trajectory(raw)
        indices = oracle.probe_indices(raw, path_state)
        frozen = probes["fixtures"][name]
        if (frozen["input_sha256"] != document.input_sha256
                or frozen["fixture_id"] != document.fixture_id
                or tuple(frozen["indices"]) != indices or len(indices) != 64 or len(set(indices)) != 64):
            raise ValueError(f"frozen oracle probes differ: {name}")
        for factor in FACTORS:
            if candidate.work_bound(document.case, factor) > CAPS["invocation_work"]:
                raise ValueError(f"per-render work cap exceeded: {name}, L{factor}")
            products += 289 * (32 * factor + 1)
        files["fixtures/" + name] = {"sha256": document.input_sha256, "bytes": len(data)}
        paths.append(path)
        fixtures.append(Fixture(name, raw, document, path_state, indices))
    if products != 159_847_056 or products > CAPS["fir_products"]:
        raise ValueError("fixed matrix FIR product admission failed")
    return Admission(root, fixture_root, tuple(fixtures), files, tuple(paths), products)


def preflight_output(admission: Admission, output: str | os.PathLike):
    """A study attempt gets a fresh path; never replace earlier experiments."""
    plans = tuple(admitted_io.preflight_paths(path, output) for path in admission.paths)
    if any(plan.output_signature is not None for plan in plans):
        raise ValueError("study output already exists; use a distinct report path")
    return plans


def _resident():
    try:
        import resource
        measured = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform.startswith("linux"):
            scale, units = 1024, "Linux KiB converted to bytes"
        elif sys.platform == "darwin":
            scale, units = 1, "macOS bytes"
        else:
            return None, "unavailable", "ru_maxrss units are not established on this platform"
        if not math.isfinite(measured) or measured <= 0:
            raise ValueError("invalid resident peak")
        return int(measured * scale), "resource.getrusage(RUSAGE_SELF).ru_maxrss; " + units, None
    except (ImportError, AttributeError, OSError, ValueError, OverflowError):
        return None, "unavailable", "process lifetime peak resident measurement unavailable"


def _guard(started: float) -> None:
    elapsed = time.perf_counter() - started
    peak, _, _ = _resident()
    if not math.isfinite(elapsed) or elapsed < 0 or elapsed > CAPS["elapsed_seconds"]:
        raise Incomplete("elapsed-time ceiling exceeded or clock invalid")
    if peak is not None and peak > CAPS["peak_resident_bytes"]:
        raise Incomplete("process lifetime peak resident ceiling exceeded")


def metrics(reference, measured, bound: float) -> dict:
    """Study-owned scaled statistics; no candidate metric helper is used."""
    if len(reference) != len(measured) or not reference:
        raise ValueError("metrics require equal nonempty arrays")
    if not math.isfinite(bound) or bound < 0:
        raise ValueError("invalid metric bound")
    if not all(math.isfinite(v) for v in (*reference, *measured)):
        raise ValueError("nonfinite comparison sample")
    errors = tuple(y - x for x, y in zip(reference, measured))
    count = len(errors)
    result = {"count": count, "max_absolute_error": max(map(abs, errors)),
              "rms_error": math.hypot(*errors) / math.sqrt(count),
              "reference_rms": math.hypot(*reference) / math.sqrt(count),
              "peak_B": None, "normalized_reference_rms": None,
              "normalized_rms_error": None, "nrmse": None}
    if bound == 0:
        result["status"] = ("zero_bound_exact" if all(v == 0 for v in (*reference, *measured))
                            else "zero_bound_violation")
        return result
    normalized_reference = tuple(v / bound for v in reference)
    normalized_error = tuple(v / bound for v in errors)
    reference_rms = math.hypot(*normalized_reference) / math.sqrt(count)
    error_rms = math.hypot(*normalized_error) / math.sqrt(count)
    result.update(peak_B=max(map(abs, normalized_error)), normalized_reference_rms=reference_rms,
                  normalized_rms_error=error_rms,
                  status="eligible" if reference_rms >= 1e-8 else "absolute_only",
                  nrmse=error_rms / reference_rms if reference_rms >= 1e-8 else None)
    return result


def grade(value: dict, limits: dict) -> dict:
    status = value["status"]
    if status.startswith("zero_bound_"):
        accepted = status == "zero_bound_exact"
        return {"accepted": accepted, "status": status, "limits": limits,
                "absolute_pass": accepted, "nrmse_pass": None}
    absolute = value["peak_B"] <= limits["peak_B"]
    normalized = value["nrmse"] <= limits["nrmse"] if status == "eligible" else None
    accepted = absolute and normalized is not False
    return {"accepted": accepted, "status": ("pass" if accepted else "fail")
            + ("_absolute_only" if normalized is None else ""), "limits": limits,
            "absolute_pass": absolute, "nrmse_pass": normalized}


def _q(value: Fraction) -> dict:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _candidate_facts(case, path):
    sources = {source.source_id: source for source in case.sources}
    rows, left_bits = [], [[False] * 9 for _ in case.keys]
    for edge in path.edges:
        key = case.keys[edge.key_index]
        source = sources[key.source_ids9[edge.contact_index]]
        value, slope = candidate.source_value_and_slope(source, case.sample_rate_hz, edge.u)
        multiplier = key.gains9[edge.contact_index] * (1 if edge.closed_after else -1)
        rows.append({"exact_u": _q(edge.u), "key_index": edge.key_index,
                     "contact_index": edge.contact_index, "closed_after": edge.closed_after,
                     "inside_observation": edge.u < case.frames,
                     "value_jump": multiplier * value, "slope_jump_per_second": multiplier * slope})
        if edge.u < case.frames:
            left_bits[edge.key_index][edge.contact_index] = edge.closed_after
    values, slopes = [], []
    for key, bits in zip(case.keys, left_bits):
        for contact, connected in enumerate(bits):
            if connected:
                value, slope = candidate.source_value_and_slope(
                    sources[key.source_ids9[contact]], case.sample_rate_hz, case.frames)
                values.append(key.gains9[contact] * value)
                slopes.append(key.gains9[contact] * slope)
    gates = [{"frame": 0, "value_jump": 0.0, "slope_jump_per_second": 0.0},
             {"frame": case.frames, "value_jump": -math.fsum(values),
              "slope_jump_per_second": -math.fsum(slopes)}]
    final = [{"key_id": key.key_id, "position_exact": _q(state.position),
              "target_exact": _q(state.target), "position": float(state.position),
              "target": float(state.target), "closed": list(state.closed9)}
             for key, state in zip(case.keys, path.final_keys)]
    return rows, gates, final


def facts_check(fixture: Fixture, rendered) -> dict:
    case, expected = fixture.document.case, fixture.path
    actual = rendered.trajectory
    edges, gates, final = _candidate_facts(case, actual)
    oracle_edges = list(oracle.edge_observations(fixture.raw, expected))
    oracle_gates = list(oracle.gate_jumps(fixture.raw, expected))
    topology = (len(actual.edges) == len(expected.edges)
                and all(tuple(a) == tuple(b) for a, b in zip(actual.edges, expected.edges)))
    finals = (len(actual.final_keys) == len(expected.final_keys)
              and all((a.position, a.target, a.closed9) == tuple(b)
                      for a, b in zip(actual.final_keys, expected.final_keys)))
    conversion = (len(actual.edges) == len(expected.edges) and all(
        abs(float(a.u) - float(b.u)) <= 32 * math.ulp(max(1.0, abs(float(b.u))))
        for a, b in zip(actual.edges, expected.edges)))
    bound = rendered.bound
    maximum_frequency = max(source.frequency_hz for source in case.sources)
    value_limit = 2e-12 * bound
    slope_limit = 2e-10 * bound * max(1.0, 2 * math.pi * maximum_frequency)
    differences = [(abs(a["value_jump"] - b["value_jump"]),
                    abs(a["slope_jump_per_second"] - b["slope_jump_per_second"]))
                   for a, b in zip(edges + gates, oracle_edges + oracle_gates)]
    max_value = max((v for v, _ in differences), default=0.0)
    max_slope = max((v for _, v in differences), default=0.0)
    jumps = topology and len(gates) == len(oracle_gates) and max_value <= value_limit and max_slope <= slope_limit
    sources = {source.source_id: source for source in case.sources}
    exact = sum((abs(Fraction.from_float(gain)) * Fraction.from_float(sources[source_id].amplitude)
                 for key in case.keys for gain, source_id in zip(key.gains9, key.source_ids9)), Fraction(0))
    outward = (bound == oracle.raw_bound(fixture.raw) and Fraction.from_float(bound) >= exact
               and (bound == 0 if exact == 0 else Fraction.from_float(math.nextafter(bound, -math.inf)) < exact))
    return {"accepted": topology and finals and conversion and jumps and outward,
            "edge_identity_order_exact": topology, "final_state_exact": finals,
            "root_conversion_32ulp": conversion, "outward_bound_exact": outward,
            "raw_bound_exact": _q(exact), "raw_bound": bound,
            "jump_check": {"accepted": jumps, "max_value_error": max_value,
                           "value_limit": value_limit, "max_slope_error": max_slope,
                           "slope_limit": slope_limit},
            "candidate_edges": edges, "oracle_edges": oracle_edges,
            "candidate_gate_jumps": gates, "oracle_gate_jumps": oracle_gates,
            "candidate_final_keys": final,
            "oracle_final_keys": [{"position_exact": _q(x.position), "target_exact": _q(x.target),
                                   "closed": list(x.closed)} for x in expected.final_keys]}


def range_check(rendered) -> dict:
    first, count = rendered.first_frame, len(rendered.samples)
    rows = []
    for step in (1, 7, 64, 289):
        joined = tuple(value for offset in range(0, count, step)
                       for value in candidate.read_samples(rendered, first + offset, min(step, count - offset)))
        rows.append({"range_size": step, "identical": joined == rendered.samples})
    boundaries = {first, first + count}
    for edge in rendered.trajectory.edges:
        for coordinate in (math.floor(edge.u) - 1, math.floor(edge.u), math.floor(edge.u) + 1):
            if first <= coordinate <= first + count:
                boundaries.add(coordinate)
    boundaries = sorted(boundaries)
    joined = tuple(value for left, right in zip(boundaries, boundaries[1:])
                   for value in candidate.read_samples(rendered, left, right - left))
    empty = (candidate.read_samples(rendered, first, 0) == ()
             and candidate.read_samples(rendered, first + count, 0) == ())
    return {"accepted": all(row["identical"] for row in rows) and joined == rendered.samples and empty,
            "fixed_ranges": rows, "irregular_boundaries": boundaries,
            "irregular_identical": joined == rendered.samples, "empty_endpoints": empty,
            "meaning": "Immutable complete-output export only; no streaming/filter-state claim"}


def residual_dft(low, high, frames: int) -> dict:
    residual = tuple(b - a for a, b in zip(low, high))
    count = len(residual)
    rows = []
    bands = [0.0, 0.0, 0.0]
    for index in range(count // 2 + 1):
        frequency = index / count
        real = math.fsum(v * math.cos(math.tau * index * j / count) for j, v in enumerate(residual))
        imaginary = -math.fsum(v * math.sin(math.tau * index * j / count) for j, v in enumerate(residual))
        multiplier = 1 if index == 0 or 2 * index == count else 2
        energy = multiplier * (real * real + imaginary * imaginary) / count
        band = 0 if frequency <= .30 else 1 if frequency <= .45 else 2
        bands[band] += energy
        rows.append({"bin": index, "cycles_per_host_frame": frequency, "one_sided_energy": energy})
    total = math.fsum(v * v for v in residual)
    tail = math.fsum(v * v for index, v in enumerate(residual) if index - 16 < 0 or index - 16 >= frames)
    return {"definition": "L256 minus L128; full stored output; unwindowed DFT",
            "sample_count": count, "first_frame": -16, "peak": max(map(abs, residual)),
            "rms": math.hypot(*residual) / math.sqrt(count), "time_domain_energy": total,
            "tail_energy": tail, "dft_energy": math.fsum(row["one_sided_energy"] for row in rows),
            "bands": [{"range": label, "energy": energy} for label, energy in
                      zip(("[0,.30]", "(.30,.45]", "(.45,.50]"), bands)], "bins": rows,
            "meaning": "Finite-window leakage is included; not a physical alias estimate"}


def response_summary(rows, frequency_key: str, magnitude_key: str) -> dict:
    passband = [row[magnitude_key] for row in rows if row[frequency_key] <= .30]
    stopband = [row[magnitude_key] for row in rows if row[frequency_key] >= .60]
    return {"dc_error": abs(rows[0][magnitude_key] - 1.0),
            "sampled_passband_ripple": max(passband) - min(passband),
            "sampled_passband_max_deviation": max(abs(v - 1.0) for v in passband),
            "sampled_stopband_maximum": max(stopband),
            "transition_rows": [row for row in rows if .30 < row[frequency_key] < .60],
            "scope": "Finite grid characterization; no audio-fidelity/stopband pass threshold"}


def filter_check(factor: int, metadata: dict) -> dict:
    normalizer, weights = candidate.filter_coefficients(factor)
    total, absolute = math.fsum(weights), math.fsum(abs(value) for value in weights)
    digest = hashlib.sha256(b"".join(struct.pack(">d", value if value else 0.0) for value in weights)).hexdigest()
    metadata_matches = (metadata["normalizer"] == normalizer and metadata["sum"] == total
                        and metadata["absolute_sum"] == absolute and metadata["dc_residual"] == abs(total - 1.0)
                        and metadata["coefficient_sha256"] == digest)
    accepted = (math.isfinite(normalizer) and normalizer > 0 and weights == weights[::-1]
                and weights[0] == weights[-1] == 0.0
                and all(math.isfinite(value) for value in weights)
                and abs(total - 1.0) <= 2e-14 and metadata_matches)
    return {"accepted": accepted, "exact_symmetry": weights == weights[::-1],
            "support_endpoints_zero": weights[0] == weights[-1] == 0.0,
            "finite_positive_normalizer": math.isfinite(normalizer) and normalizer > 0,
            "independently_recomputed_metadata_matches": metadata_matches,
            "dc_residual_limit": 2e-14}


def _git_identity(root: Path) -> dict:
    result = {}
    try:
        for key, command in (("head", ["rev-parse", "HEAD"]),
                             ("head_tree", ["rev-parse", "HEAD^{tree}"]),
                             ("working_tree_porcelain", ["status", "--porcelain=v1", "--untracked-files=all"])):
            value = subprocess.run(["git", "-C", str(root), *command], check=True,
                                   capture_output=True, text=True, timeout=5)
            result[key] = value.stdout.strip()
        result["meaning"] = "Repository observation only; numerical inputs are qualified by the explicit file hashes"
    except (OSError, subprocess.SubprocessError):
        result = {"head": None, "head_tree": None, "working_tree_porcelain": None,
                  "reason": "Git identity unavailable in this relocated package"}
    return result


def _hardware() -> dict:
    processor = platform.processor()
    if not processor and sys.platform.startswith("linux"):
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as stream:
                for line in stream:
                    if line.startswith("model name"):
                        processor = line.partition(":")[2].strip()
                        break
        except OSError:
            pass
    return {"processor": processor or None, "machine": platform.machine(),
            "logical_cpu_count": os.cpu_count(), "platform": platform.platform()}


def run_study(admission: Admission, *, started: float | None = None,
              command: list[str] | None = None) -> dict:
    """Execute the complete admitted matrix; retain incomplete rows explicitly."""
    started = time.perf_counter() if started is None else started
    budget = oracle.EvaluationBudget()
    report = {"schema_version": 1, "study_id": STUDY_ID, "model_id": candidate.MODEL_ID,
              "evidence_class": "synthetic", "status": "incomplete", "command": command or [],
              "started_utc": datetime.now(timezone.utc).isoformat(), "finished_utc": None,
              "python_version": platform.python_version(), "hardware": _hardware(),
              "repository": _git_identity(admission.root), "files": admission.files,
              "source_root_at_execution": str(admission.root),
              "fixture_root_at_execution": str(admission.fixture_root),
              "independence": {"oracle_id": oracle.ORACLE_ID, "author": "/root/w04_a19_continuous_oracle",
                               "reviewer": "/root/w04_a24_fixture_oracle_audit",
                               "review_report_sha256": "b79b736cdb4b2ac008e14e413d306e71eff4b779f567616562512caad88ba55e"},
              "matrix": {"fixtures": 36, "factors": list(FACTORS), "sample_rates_hz": list(RATES),
                         "frames": 256, "output_samples": 289, "oracle_probes": 64,
                         "fir_product_bound": admission.fir_products},
              "caps": dict(CAPS), "limits": LIMITS, "filters": {}, "continuous_response": None,
              "fixtures": [], "failed_cells": [], "incomplete_reason": None, "observations": {},
              "limitations": ["Synthetic fixed-load switched sines; no measured contact physics",
                              "64 continuous probes do not establish full-window atlas 1e-4 accuracy",
                              "Finite non-ideal kernel; no sufficient-bandwidth or pure-alias claim",
                              "Offline acausal output; no Engine/streaming/callback/causal-latency claim",
                              "Mathematical ideal output bound is not a certified floating-point headroom gate"]}
    products_done, renders_done = 0, 0
    try:
        _guard(started)
        for factor in FACTORS:
            metadata = candidate.filter_metadata(factor)
            check = filter_check(factor, metadata)
            report["filters"][str(factor)] = {**metadata, "check": check,
                "summary": response_summary(metadata["responses"], "cycles_per_host_frame", "renderer_magnitude")}
            if not check["accepted"]:
                report["failed_cells"].append({"fixture_id": None, "gate": "filter", "factor": factor})
            _guard(started)
        response = oracle.continuous_response(FREQUENCIES, .25, budget=budget)
        response["summary"] = response_summary(response["responses"], "frequency_cycles_per_frame", "magnitude")
        report["continuous_response"] = response
        _guard(started)
        for fixture in admission.fixtures:
            case = fixture.document.case
            row = {"fixture_id": fixture.document.fixture_id, "input_sha256": fixture.document.input_sha256,
                   "sample_rate_hz": case.sample_rate_hz, "frames": case.frames,
                   "first_frame": -16, "time_offset_seconds": -16 / case.sample_rate_hz,
                   "status": "incomplete", "targets": [dict(fixture.raw["targets"][i], input_ordinal=i)
                       for i in sorted(range(len(case.targets)), key=lambda i:
                           (case.targets[i].frame, case.targets[i].fraction, i))],
                   "oracle_probe_indices": list(fixture.indices), "factors": {}, "oracle": {},
                   "ceil_edge_same_kernel_v1": {}, "gates": {}, "comparisons": {}}
            report["fixtures"].append(row)
            renders = {}
            for factor in FACTORS:
                _guard(started)
                began = time.perf_counter()
                rendered = candidate.render(case, factor)
                renders[factor] = rendered
                renders_done += 1
                products_done += 289 * (32 * factor + 1)
                exported = range_check(rendered)
                consistent = (rendered.first_frame == -16 and len(rendered.samples) == 289
                              and rendered.samples[0] == rendered.samples[-1] == 0.0
                              and rendered.trajectory == renders[32].trajectory
                              and rendered.bound == oracle.raw_bound(fixture.raw)
                              and rendered.work == (289 * (32 * factor + 1)
                                  + (256 * factor + 1) * 9 * len(case.keys)
                                  + 18 * len(case.targets) + 32 * factor + 1)
                              and (rendered.bound != 0 or all(value == 0 for value in rendered.samples)))
                row["factors"][str(factor)] = {"samples": list(rendered.samples), "work": rendered.work,
                    "fir_product_bound": 289 * (32 * factor + 1),
                    "raw_bound": rendered.bound,
                    "output_bound": rendered.bound * report["filters"][str(factor)]["absolute_sum"],
                    "observed_peak": max(map(abs, rendered.samples)),
                    "elapsed_seconds": time.perf_counter() - began, "range_export": exported,
                    "complete_tails_and_identical_trajectory": consistent}
                if not exported["accepted"] or not consistent:
                    report["failed_cells"].append({"fixture_id": row["fixture_id"], "factor": factor,
                                                   "gate": "output_range_tails_trajectory"})
                _guard(started)
            bound = renders[256].bound
            facts = facts_check(fixture, renders[256])
            row["facts"] = facts
            row["gates"]["exact_trajectory_and_jumps"] = {"accepted": facts["accepted"]}
            values = {}
            for width in oracle.PANEL_WIDTHS:
                evaluation = oracle.evaluate(fixture.raw, fixture.path, fixture.indices, width, budget=budget)
                values[width] = evaluation.values
                row["oracle"][str(width)] = {"values": list(evaluation.values), "normalizer": evaluation.normalizer,
                                            "integrand_evaluations": evaluation.integrand_evaluations}
                _guard(started)
            coarse = metrics(values[.5], values[1.0], bound)
            refined = metrics(values[.25], values[.5], bound)
            row["comparisons"]["oracle_1_to_half"] = coarse
            row["comparisons"]["oracle_half_to_quarter"] = refined
            row["gates"]["oracle_refinement"] = grade(refined, LIMITS["oracle_refinement"])
            convergence = []
            for low, high in zip(FACTORS, FACTORS[1:]):
                value = metrics(renders[high].samples, renders[low].samples, bound)
                row["comparisons"][f"L{low}_to_L{high}"] = value
                convergence.append(value["normalized_rms_error"])
            row["observed_orders"] = [{"pair": label,
                "order": math.log2(a / b) if a is not None and b is not None and a > 0 and b > 0 else None,
                "rms_decreased": b < a if a is not None and b is not None else None}
                for label, a, b in zip(("32:64:128", "64:128:256"), convergence, convergence[1:])]
            row["gates"]["high_rate_convergence"] = grade(row["comparisons"]["L128_to_L256"], LIMITS["high_rate_convergence"])
            probes = tuple(renders[256].samples[n + 16] for n in fixture.indices)
            comparison = metrics(values[.25], probes, bound)
            row["comparisons"]["L256_vs_continuous_quarter"] = comparison
            independent = grade(comparison, LIMITS["independent_reference"])
            independent["prerequisites_accepted"] = (row["gates"]["oracle_refinement"]["accepted"]
                                                       and row["gates"]["high_rate_convergence"]["accepted"])
            independent["accepted"] = independent["accepted"] and independent["prerequisites_accepted"]
            if not independent["prerequisites_accepted"]:
                independent["status"] = "blocked_by_refinement_or_convergence"
            row["gates"]["independent_reference"] = independent
            ceil_values = {}
            for width in (.5, .25):
                evaluation = oracle.evaluate(fixture.raw, fixture.path, fixture.indices, width,
                                             ceil_edges=True, budget=budget)
                ceil_values[width] = evaluation.values
                row["ceil_edge_same_kernel_v1"][str(width)] = {
                    "values": list(evaluation.values), "normalizer": evaluation.normalizer,
                    "integrand_evaluations": evaluation.integrand_evaluations}
                _guard(started)
            ceil_refinement = metrics(ceil_values[.25], ceil_values[.5], bound)
            row["ceil_edge_same_kernel_v1"]["refinement"] = ceil_refinement
            row["gates"]["ceil_oracle_refinement"] = grade(ceil_refinement, LIMITS["oracle_refinement"])
            row["ceil_edge_same_kernel_v1"]["difference_from_fractional"] = metrics(values[.25], ceil_values[.25], bound)
            row["ceil_edge_same_kernel_v1"]["meaning"] = "Timing quantization characterization only; no error pass threshold, native Engine parity or pure-alias claim"
            row["residual_dft"] = residual_dft(renders[128].samples, renders[256].samples, case.frames)
            for name, gate in row["gates"].items():
                if not gate["accepted"]:
                    report["failed_cells"].append({"fixture_id": row["fixture_id"], "gate": name})
            row["status"] = "failed" if any(x["fixture_id"] == row["fixture_id"] for x in report["failed_cells"]) else "passed"
            _guard(started)
    except (Incomplete, oracle.OracleBudgetExceeded) as error:
        report["incomplete_reason"] = str(error)
    report["observations"].update(completed_fixture_count=sum(row["status"] != "incomplete" for row in report["fixtures"]),
                                  completed_render_count=renders_done, fir_products_charged=products_done,
                                  fir_products_meaning="Conservative full-support product bound; zero-routing and clipped-tail shortcuts are not subtracted; actual multiplication instructions are not instrumented",
                                  oracle_integrand_evaluations=budget.count, report_bytes=0)
    return report


def _finite(value):
    if value is None or type(value) in (bool, str, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("nonfinite study result")
        return value if value else 0.0
    if type(value) is list:
        return [_finite(x) for x in value]
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: _finite(item) for key, item in value.items()}
    raise ValueError("unsupported study result type")


def encode_report(report: dict, started: float) -> bytes:
    """Finish resource grading after the complete retained result is assembled."""
    original = report
    report = _finite(report)
    observations = report["observations"]
    peak, method, reason = _resident()
    observations.update(peak_resident_bytes=peak, peak_resident_measurement=method,
                        peak_resident_unavailable_reason=reason,
                        elapsed_seconds=time.perf_counter() - started,
                        elapsed_measurement="Monotonic earliest script initialization through final encoding; excludes Python startup and atomic publication; retain an external full-process timer",
                        resident_scope="Process-lifetime peak; includes setup, candidate, oracle and report construction")
    if peak is None:
        report["incomplete_reason"] = report["incomplete_reason"] or "peak resident measurement unavailable"
    elif peak > CAPS["peak_resident_bytes"]:
        report["incomplete_reason"] = report["incomplete_reason"] or "peak resident ceiling exceeded"
    for _ in range(12):
        elapsed = time.perf_counter() - started
        observations["elapsed_seconds"] = elapsed
        if elapsed > CAPS["elapsed_seconds"]:
            report["incomplete_reason"] = report["incomplete_reason"] or "elapsed-time ceiling exceeded"
        complete = observations["completed_fixture_count"] == 36 and observations["completed_render_count"] == 144
        if not complete:
            report["incomplete_reason"] = report["incomplete_reason"] or "declared matrix not complete"
        report["status"] = ("incomplete" if report["incomplete_reason"] else
                            "failed" if report["failed_cells"] else "passed")
        observations["resource_gate_status"] = "incomplete" if report["incomplete_reason"] else "passed"
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        payload = (json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
        if len(payload) > CAPS["report_bytes"]:
            raise Incomplete("retained report exceeds 32 MiB; no output published")
        latest_peak, _, _ = _resident()
        if latest_peak is not None and (peak is None or latest_peak > peak):
            peak = latest_peak
            observations["peak_resident_bytes"] = peak
            if peak > CAPS["peak_resident_bytes"]:
                report["incomplete_reason"] = report["incomplete_reason"] or "peak resident ceiling exceeded"
            continue  # Serialize the measured report-construction peak, too.
        if observations["report_bytes"] == len(payload):
            for name in ("status", "observations", "finished_utc", "incomplete_reason"):
                original[name] = report[name]
            return payload
        observations["report_bytes"] = len(payload)
    raise ValueError("study report byte count did not stabilize")


def atomic_publish(admission: Admission, plans, payload: bytes) -> None:
    if len(payload) > CAPS["report_bytes"]:
        raise ValueError("report exceeds byte ceiling")
    if preflight_output(admission, plans[0].output_argument) != plans:
        raise ValueError("protected input/output identities changed")
    for name, fact in admission.files.items():
        path = admission.fixture_root / name[9:] if name.startswith("fixtures/") else admission.root / name
        if _sha(_read(path)) != fact["sha256"]:
            raise ValueError(f"protected file changed during study: {name}")
    temporary = None
    try:
        descriptor, temporary = tempfile.mkstemp(prefix=".contact-study-", suffix=".tmp", dir=plans[0].output_path.parent)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        if preflight_output(admission, plans[0].output_argument) != plans:
            raise ValueError("protected input/output identities changed before publication")
        os.replace(temporary, plans[0].output_path)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


class _Once(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is not None:
            raise ValueError(f"duplicate option: {option_string}")
        setattr(namespace, self.dest, values)


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--fixtures", required=True, action=_Once, help="fixed v1 fixture directory")
    parser.add_argument("--output", required=True, action=_Once, help="new report path; parent must exist")
    try:
        args = parser.parse_args(argv)
        admission = admit_inputs(Path(args.fixtures))
        plans = preflight_output(admission, args.output)
        report = run_study(admission, started=_SCRIPT_STARTED,
                           command=[sys.executable, *sys.argv] if argv is None else [sys.executable, __file__, *argv])
        payload = encode_report(report, _SCRIPT_STARTED)
        status = report["status"]
        atomic_publish(admission, plans, payload)
        return {"passed": 0, "failed": 1, "incomplete": 2}[status]
    except (ValueError, OSError, OverflowError, MemoryError, Incomplete) as error:
        diagnostic = " ".join(str(error).split())[:700]
        print(f"contact switching study: {diagnostic}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
