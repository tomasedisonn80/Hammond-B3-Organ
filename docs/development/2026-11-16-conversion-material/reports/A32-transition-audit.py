#!/usr/bin/env python3
"""Bounded source audit for the separately versioned T1 material fixtures.

This verifies the declared assertion transition, not runtime acceptance.
Run from any directory; it refuses to overwrite its evidence output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"Expected one occurrence of {old[:80]!r}")
    return text.replace(old, new, 1)


def section(text: str, first: str, following: str) -> str:
    start = text.index(first)
    return text[start:text.index(following, start)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[4]
    reports = Path(__file__).resolve().parent
    initial = json.loads((reports / "A32-transition-initial-bindings.json").read_text())
    reference_commit = "3520c96adcdcf4ce4bcb860082354bf0050a89c3"
    method_start = "    // Expected T1 layout is declared independently by musical-label index.\n"
    method_end = "    Frame focus(UiRect bounds, float sx, float sy) {\n"
    check_start = "void footage_ink(Target& target, const Frame& actual, std::size_t index, UiRect box,\n"
    check_end = "void opaque_probe(const Case& test, const Frame& frame, UiRect canonical_probe) {\n"
    old_call = (
        "        literal_ink(target, frame, footage[index], canonical(test, center - 23, 467, 46, 23),\n"
        "                    19 * font_scale, TextFace::Serif, 2 * sx);\n"
    )
    new_call = "        footage_ink(target, frame, index, canonical(test, center - 23, 467, 46, 23), sx, sy);\n"
    helpers = []
    records = []
    for binding in initial["changes"]:
        path = repo / binding["path"]
        archive = repo / binding["archive"]
        before_bytes = archive.read_bytes()
        before = before_bytes.decode()
        current_bytes = path.read_bytes()
        current = current_bytes.decode()
        committed = subprocess.run(
            ["git", "show", f"{reference_commit}:{binding['path']}"],
            cwd=repo, check=True, capture_output=True,
        ).stdout
        assert sha(before_bytes) == binding["before_sha256"]
        assert before_bytes == committed, "original archive must equal the genuine committed source"
        method = section(current, method_start, method_end)
        check = section(current, check_start, check_end)
        helpers.append((method, check))
        restored = once(current, '#include "FontData.h"\n', "")
        restored = once(restored, method, "")
        restored = once(restored, check, "")
        restored = once(restored, new_call, old_call)
        restored = once(
            restored,
            f'constexpr std::string_view protocol = "{binding["protocol_after"]}";\n',
            f'constexpr std::string_view protocol = "{binding["protocol_before"]}";\n',
        )
        comment = (
            f'// Versioned T1 footage-assertion transition; original {binding["protocol_before"]}\n'
            "// source/results remain archived. Cases, material support and frame generation\n"
            "// are unchanged; only the admitted footage glyph expectation is replaced.\n"
            "// Historical material comparators require their original protocol/binaries.\n"
        )
        restored = once(restored, comment, binding["original_comment"])
        assert restored.encode() == before_bytes, "undeclared source delta"
        original_ink = section(before, "void literal_ink(", "void opaque_probe(")
        original_samples = original_ink[original_ink.index("    const auto& t = actual.coordinates;"):]
        new_samples = check[check.index("    const auto& t = actual.coordinates;"):]
        assert original_samples == new_samples, "glyph sampling and contrast criteria changed"
        assert "reference_manual_footage" not in method
        assert "reference_footage_round" not in method
        assert "complete == footage[index]" in method
        assert "static_cast<unsigned char>(character)" in method
        assert "std::min(sx, sy)" in method
        assert "f32(0.5F * sx)" in method
        assert "f32(box.x + f32(f32(box.width - extent) / 2.0F))" in method
        assert "f32(box.y + f32(baselines[part] * sy))" in method
        assert "f32(requested_baseline - f32(f32(38.0F * sizes[part]) / 40.0F))" in method
        assert "f32(cursor + drawing_.text_width(words[index][part], sizes[part], TextFace::Serif))" in method
        assert "if (count == 5 && (part == 0 || part == 3)) cursor = f32(cursor + gap);" in method
        records.append({
            "path": binding["path"],
            "original_archive": binding["archive"],
            "original_sha256": sha(before_bytes),
            "current_sha256": sha(current_bytes),
            "reversed_sha256": sha(restored.encode()),
            "archive_equals_genuine_committed_source": True,
            "remove_exact_declared_delta_restores_original_bytes": True,
            "literal_ink_sampling_body_unchanged": True,
            "expected_helper_sha256": sha(method.encode()),
            "expected_sampler_sha256": sha(check.encode()),
            "old_protocol": binding["protocol_before"],
            "new_protocol": binding["protocol_after"],
        })
    assert helpers[0] == helpers[1], "Upper/Lower admitted expectation differs"
    unchanged = [
        "cases/inventory", "existing literal_ink", "value/heading expectations", "material probes",
        "all model/layout/session serialization", "state restoration", "focus", "caller clips",
        "frame generation", "thresholds", "f32 helper", "repetition checks", "CLI/stream structure",
    ]
    output = {
        "schema": "a32-material-fixture-transition-source-audit-v1",
        "status": "passed", "reference_commit": reference_commit,
        "records": records, "upper_lower_expectation_helpers_byte_identical": True,
        "unchanged_outside_declared_delta": unchanged,
        "scope": "Exact source reversibility, original-byte archival and unchanged strong-ink criteria; native execution is separate root evidence.",
        "audit_source_sha256": sha(Path(__file__).read_bytes()),
    }
    with args.output.open("x") as stream:
        json.dump(output, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"status": "passed", "source_files": len(records), "output": str(args.output)}))


if __name__ == "__main__":
    main()
