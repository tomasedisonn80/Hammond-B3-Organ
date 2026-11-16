#!/usr/bin/env python3
"""Scoped T1 source/preservation audit; not an independent raster acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refusing to overwrite retained evidence")
    repo = Path(__file__).resolve().parents[4]
    painter_path = repo / "apps/standalone/InstrumentView.cpp"
    before_path = repo.parent / "baseline-lower/InstrumentView.cpp"
    before = before_path.read_bytes()
    candidate = painter_path.read_bytes()
    assert sha(before) == "45b710a9c207f456701732f55ec1086487d63bdb9a8b6ed995f4de12cd5bdb10"
    source = candidate.decode("utf-8")
    start = source.index("[[nodiscard]] float reference_footage_round(")
    end = source.index("void reference_drawbar(", start)
    helper = source[start:end]
    new_call = """    if (mixture) {
        centered(drawing, label, geometry.label_bounds, 11.0F * scale.f,
                 kUiIvory, TextFace::Sans, 2.0F * scale.sx);
    } else {
        reference_manual_footage(drawing, label, geometry.label_bounds, scale);
    }
"""
    old_call = """    centered(drawing, label, geometry.label_bounds, (mixture ? 11.0F : 19.0F) * scale.f,
             kUiIvory, mixture ? TextFace::Sans : TextFace::Serif, 2.0F * scale.sx);
"""
    assert source.count(new_call) == 1
    restored = (source[:start] + source[end:]).replace(new_call, old_call)
    assert restored.encode("utf-8") == before
    assert "volatile float rounded = value;" in helper
    for forbidden in ("std::string(", "std::vector", "SDL_", "new ", "delete ", "malloc", "fopen"):
        assert forbidden not in helper, forbidden
    declarations = re.search(
        r"kUiFootageLabels\s*\{(.*?)\};", (repo / "apps/standalone/UiModel.h").read_text(), re.S
    ).group(1)
    labels = re.findall(r'"([^"]+)"', declarations)
    assert labels == ["16'", "5 1/3'", "8'", "4'", "2 2/3'", "2'", "1 3/5'", "1 1/3'", "1'"]
    recognized = re.findall(r'label == "([^"]+)"', helper)
    assert len(recognized) == 9 and set(recognized) == set(labels)
    counts = [{"label": label, "text_calls": 5 if " " in label else 1,
               "nonempty_glyph_copies": len(label.replace(" ", ""))} for label in labels]
    assert 2 * sum(x["text_calls"] for x in counts) == 50
    assert 2 * sum(x["nonempty_glyph_copies"] for x in counts) == 62
    reference = "3520c96adcdcf4ce4bcb860082354bf0050a89c3"
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", reference, "--", "src", "include", "plugins", "apps/standalone"],
        cwd=repo, text=True).splitlines()
    unchanged = []
    for name in names:
        if not name.endswith((".cpp", ".h", ".hpp")) or name == "apps/standalone/InstrumentView.cpp":
            continue
        original = subprocess.check_output(["git", "show", reference + ":" + name], cwd=repo)
        current = (repo / name).read_bytes()
        assert current == original, name
        unchanged.append({"path": name, "sha256": sha(current)})
    bindings = {}
    for name in (
        "docs/design/FOOTAGE_TYPOGRAPHY_CONTRACT.md",
        "docs/reviews/FOOTAGE_TYPOGRAPHY_ADMISSION.md",
        "apps/standalone/native_tests/test_standalone_footage_typography_raster.cpp",
        "docs/development/2026-11-16-conversion-material/reports/typography-before-identity.json",
        "apps/standalone/Drawing.cpp", "apps/standalone/Drawing.h", "apps/standalone/FontData.h",
        "apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h",
    ):
        data = (repo / name).read_bytes()
        bindings[name] = {"bytes": len(data), "sha256": sha(data)}
    result = {
        "schema": "a28-typography-source-audit-v1", "status": "passed",
        "scope": "source scope/reversibility and finite current-string inventory; no raster, native-device or performance admission",
        "cwd": str(repo), "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        "reference_commit": reference,
        "before": {"bytes": len(before), "sha256": sha(before)},
        "candidate": {"bytes": len(candidate), "sha256": sha(candidate)},
        "helper_bytes": len(helper.encode()), "helper_sha256": sha(helper.encode()),
        "remove_two_private_helpers_and_restore_only_callsite_reproduces_before_bytes": True,
        "label_inventory": counts, "manual_labels": 18, "text_calls": 50, "nonempty_glyph_copies": 62,
        "fixed_array_capacities": {"string_views": 5, "nominal_sizes": 5, "baseline_offsets": 5, "sizes": 5, "advances": 5},
        "unchanged_cpp_header_count": len(unchanged),
        "unchanged_cpp_header_manifest_sha256": sha(json.dumps(unchanged, sort_keys=True, separators=(",", ":")).encode()),
        "bindings": bindings,
        "limits": ["No claim of SDL internal allocation behavior or frame deadline.",
                   "Future material-fixture expectation transitions have separate owners and evidence.",
                   "Original fallback and pedal paths are retained; live audio/model state unchanged by this exact source delta."]
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "passed", "candidate_sha256": sha(candidate),
                      "unchanged_cpp_headers": len(unchanged), "text_calls": 50, "glyphs": 62}))


if __name__ == "__main__":
    main()
