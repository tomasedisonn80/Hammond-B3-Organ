#!/usr/bin/env python3
"""Read retained visual provenance; write only A50 evidence, never run native code."""

import gzip
import hashlib
import itertools
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit

import fitz
from PIL import Image


REPO = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent
PUBLISHED = "cdbb2beaa28bf136f9a8db6213819129514e2ae9"
CAPTURE_COMMIT = "8673713a484c40e26ac7810c7c4cbc22fa874426"
GALLERY = REPO / "examples/demos/standalone-interface-preview-v2"
OLD = REPO / "examples/demos/standalone-interface-preview-v1"
BUILD = REPO.parent / "build-native"
failures = []
edges = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha(data)}


def read(path):
    return json.loads(path.read_text())


def check(condition, name):
    if not condition:
        failures.append(name)


def blob(revision, path):
    return subprocess.check_output(["git", "-C", str(REPO), "show", f"{revision}:{path}"])


def edge(owner, target, expected):
    actual = identity(target)
    expected = {k: v for k, v in expected.items() if k in ("sha256", "bytes")}
    good = all(actual[k] == v for k, v in expected.items())
    edges.append({"owner": owner, "target": str(target.relative_to(REPO)),
                  "expected": expected, "actual": actual, "matches": good})
    return good


def write(name, value):
    (REPORTS / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    start = datetime.now(timezone.utc).isoformat()
    head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    protected = read(REPORTS / "a12-boundary-inventory.json")
    assets = []
    for path, group, size, git_blob, digest in protected["files"]:
        if group not in ("retained_assets", "source_provenance"):
            continue
        actual = identity(REPO / path)
        published = blob(PUBLISHED, path)
        baseline = blob(protected["baseline_commit"], path)
        good = actual == {"bytes": size, "sha256": digest} and published == baseline == (REPO / path).read_bytes()
        check(good, f"A12/published asset: {path}")
        assets.append({"path": path, "group": group, **actual, "matches_a12_and_published": good})

    ref = read(REPO / "docs/design/atlas-reference.json")
    source = read(REPO / "docs/research/source-manifest.json")
    art = read(REPO / "assets/standalone/reference/manifest.json")
    jpeg = REPO / ref["image"]
    pdf = REPO / ref["source"]
    check(identity(pdf) == {"bytes": source["bytes"], "sha256": source["sha256"]}, "source PDF manifest")
    check(sha(pdf.read_bytes()) == ref["source_sha256"] == art["source"]["pdf_sha256"], "PDF reference ancestry")
    document = fitz.open(pdf)
    image_objects = {str(page): [row[0] for row in document.get_page_images(page - 1)] for page in (1, 409)}
    embedded = document.extract_image(ref["pdf_image_object"])["image"]
    check(len(document) == 500 and image_objects == {"1": [3], "409": [3]}, "500 pages and shared image object")
    check(embedded == jpeg.read_bytes(), "embedded original JPEG byte equality")
    with Image.open(jpeg) as image:
        image.load()
        decoded = image.convert("RGB")
    check(sha(decoded.tobytes()) == art["source"]["decoded_rgb_sha256"], "decoded source RGB")

    provenance = read(GALLERY / "provenance.json")
    before = read(REPORTS / "a46-source-before.json")
    after = read(REPORTS / "a46-source-after.json")
    qualification = read(REPORTS / "a46-source-qualification.json")
    final = read(REPORTS / "a46-final-result.json")
    exe = Path(provenance["executable"]["path"])
    exe_data = exe.read_bytes()
    check(identity(exe) == provenance["executable"]["before"] == provenance["executable"]["after"], "current and captured executable")
    generated = BUILD / "apps/standalone/generated/ReferenceArtData.h"
    generated_text = generated.read_text()
    check(identity(generated) == provenance["build"]["files"][str(generated.relative_to(BUILD))], "captured reference header")
    crops = []
    for item in art["assets"]:
        compressed = REPO / "assets/standalone/reference" / item["file"]
        expanded = gzip.decompress(compressed.read_bytes())
        x, y, width, height = item["source_rect"]
        pixels = decoded.crop((x, y, x + width, y + height)).tobytes()
        body = re.search(rf"{item['cpp_symbol']}Pixels\[\] = \{{(.*?)\}};", generated_text, re.S).group(1)
        cpp_bytes = bytes(int(x, 16) for x in re.findall(r"0x([0-9a-fA-F]{2})", body))
        check(identity(compressed) == {"bytes": item["bytes"], "sha256": item["sha256"]}, f"compressed crop {item['name']}")
        check(expanded == pixels == cpp_bytes and sha(expanded) == item["pixel_sha256"], f"exact crop/embedded array {item['name']}")
        check(expanded in exe_data, f"binary contains crop {item['name']}")
        crops.append({"name": item["name"], "source_rect": item["source_rect"],
                      "pixel_sha256": sha(expanded), "cpp_array_equal": cpp_bytes == expanded,
                      "present_in_exact_executable": expanded in exe_data})

    fonts_root = REPO / "assets/standalone/fonts"
    fonts = read(fonts_root / "source-manifest.json")
    atlases = read(fonts_root / "atlas-manifest.json")
    font_header = REPO / atlases["header"]["file"]
    header_text = font_header.read_text()
    check(identity(font_header) == {k: v for k, v in atlases["header"].items() if k != "file"}, "font header hash")
    check(sha((fonts_root / "source-manifest.json").read_bytes()) == atlases["source_manifest_sha256"], "font manifest edge")
    font_rows = []
    for font, atlas in zip(fonts["fonts"], atlases["atlases"]):
        check(identity(fonts_root / font["file"]) == {k: font[k] for k in ("bytes", "sha256")}, f"font source {font['file']}")
        body = re.search(rf"k{atlas['name']}AlphaRle\{{\{{(.*?)\}}\}};", header_text, re.S).group(1)
        rle = bytes(int(x) for x in re.findall(r"\d+", body))
        alpha = b"".join(bytes([rle[i + 1]]) * rle[i] for i in range(0, len(rle), 2))
        check(len(rle) == atlas["rle_bytes"] and sha(rle) == atlas["rle_sha256"], f"font RLE {atlas['name']}")
        check(len(alpha) == atlas["alpha_bytes"] and sha(alpha) == atlas["alpha_sha256"], f"font alpha {atlas['name']}")
        check(rle in exe_data, f"binary contains font RLE {atlas['name']}")
        font_rows.append({"name": atlas["name"], "source_sha256": font["sha256"],
                          "rle_sha256": sha(rle), "alpha_sha256": sha(alpha), "present_in_exact_executable": rle in exe_data})
    notice = fonts_root / fonts["license"]["file"]
    check(sha(notice.read_bytes()) == fonts["license"]["sha256"], "complete font notice identity")
    check(all(line in header_text for line in notice.read_text().splitlines() if line.strip()), "font notice retained in header")
    refresh = read(REPORTS / "a44-package-refresh.json")
    for mode, package in refresh["packages"].items():
        check(package["payload"]["share/hammond-b3-organ/standalone/LICENSE-DejaVu.txt"] == identity(notice), f"installed font notice {mode}")
        check(package["payload"]["share/hammond-b3-organ/standalone/THIRD_PARTY_NOTICES.md"] == identity(REPO / "THIRD_PARTY_NOTICES.md"), f"installed combined notices {mode}")

    a44_source = read(REPORTS / "a44-midi-on-source-after-build.json")
    production = provenance["source"]["files"]
    product_mismatches = []
    for path, expected in production.items():
        if identity(REPO / path) != expected or sha(blob(CAPTURE_COMMIT, path)) != expected["sha256"] or sha(blob(PUBLISHED, path)) != expected["sha256"]:
            product_mismatches.append(path)
    check(not product_mismatches and len(production) == 98, "98 observed product inputs")
    check(production == before["production_files"] == after["production_files"], "capture source snapshots")
    check({p: v["sha256"] for p, v in production.items()} == a44_source["production_sha256"], "A44 98-file source map")
    check(len(qualification["source_sha256"]) == 10 and all(production[p]["sha256"] == h for p, h in qualification["source_sha256"].items()), "ten-file admission subset")
    check(len(provenance["build"]["files"]) == 13 and provenance["build"]["files"] == before["build_files"] == after["build_files"], "13 selected captured build inputs")
    for scope in ("source", "build"):
        canonical = sha(json.dumps(provenance[scope]["files"], sort_keys=True, separators=(",", ":")).encode())
        check(canonical == provenance[scope]["inventory_sha256_before"] == provenance[scope]["inventory_sha256_after"], f"{scope} inventory digest")
    check(provenance["source"]["git_before"] == provenance["source"]["git_after"], "capture git snapshot")
    check(read(GALLERY / "inputs/source-qualification.json") == qualification, "copied qualification content")

    gallery_rows = []
    for base in (OLD, GALLERY):
        manifest = read(base / "manifest.json")
        mismatch = [p for p, expected in manifest["files"].items() if identity(base / p) != expected]
        all_files = sorted(p for p in base.rglob("*") if p.is_file())
        check(not mismatch and len(manifest["files"]) == 39, f"{base.name} manifest")
        check(sum(x["bytes"] for x in manifest["files"].values()) == manifest["total_bytes_excluding_manifest"], f"{base.name} total bytes")
        if base == OLD:
            check(all(p.read_bytes() == blob(PUBLISHED, str(p.relative_to(REPO))) for p in all_files), "all 41 v1 files equal publication")
        else:
            check({str(p.relative_to(base)): identity(p) for p in all_files} == final["gallery_files"], "v2 final 41-file map")
        gallery_rows.append({"gallery": str(base.relative_to(REPO)), "manifest": identity(base / "manifest.json"),
                             "provenance": identity(base / "provenance.json"), "payload_count": len(manifest["files"]),
                             "all_files": len(all_files), "mismatches": mismatch})
    images = []
    for case in provenance["cases"]:
        image_record = case["image"]
        png = GALLERY / image_record["path"]
        with Image.open(png) as decoded_png:
            decoded_png.load()
            pixels_hash = sha(decoded_png.tobytes())
            check(decoded_png.size == (case["width"], case["height"]) and decoded_png.mode == "RGBA", f"PNG extent/mode {case['name']}")
        check(identity(png) == image_record["png"] and pixels_hash == image_record["decoded_sha256"], f"PNG bytes/pixels {case['name']}")
        diag_path = GALLERY / case["diagnostics"]["path"]
        check(identity(diag_path) == {k: v for k, v in case["diagnostics"].items() if k != "path"}, f"diagnostic bytes {case['name']}")
        diag = read(diag_path)
        painted = diag["presentation"]["screenshot"]
        check(painted == diag["presentation"]["last_painted"] == diag["presentation"]["before_shutdown"] == case["validation"]["actual_painted_view"], f"paint record {case['name']}")
        check((painted["workspace"], painted["presentation"], painted["window_width"], painted["window_height"]) == (case["workspace"], case["presentation"], case["width"], case["height"]), f"case paint selection {case['name']}")
        check(case["command"][0] == str(exe) and case["exit_code"] == 0 and case["status"] == "passed", f"retained execution {case['name']}")
        check(diag["audio"]["driver"] == diag["runtime"]["video_driver"] == "dummy" and diag["runtime"]["renderer"] == "software" and diag["midi"]["source"] == "none", f"execution scope {case['name']}")
        check(diag["controls"] == diag["replay"]["desired_controls_before_shutdown"] == diag["replay"]["before_shutdown"]["controls"], f"applied replay controls {case['name']}")
        images.append({"name": case["name"], "width": case["width"], "height": case["height"], **identity(png), "decoded_sha256": pixels_hash, "diagnostic_sha256": identity(diag_path)["sha256"]})

    for owner, mapping in [("a46-source-before.json", before["a44_reports"]),
                           ("a46-source-qualification.json", qualification["supporting_reports"]),
                           ("v2/inputs/source-qualification.json", qualification["supporting_reports"]),
                           ("a45-closing-check.json", {k: {"sha256": v} for k, v in read(REPORTS / "a45-closing-check.json")["followup_report_sha256"].items()})]:
        for name, expected in mapping.items():
            edge(owner, REPORTS / name, expected)
    for name, expected in final["artifact_inventory_excluding_result_and_gallery"].items():
        edge("a46-final-result.json", REPO / name, expected)
    for owner in ("a43-native-sanitizer-ci.json", "root-a43-static-recheck.json"):
        record = read(REPORTS / owner)
        for key in ("a41_frozen_discovery", "a41_original_limit_outcome", "a41_workflow_freeze_release"):
            item = record[key]
            path = REPO / item["path"] if item["path"].startswith("docs/") else REPORTS / item["path"]
            edge(f"{owner}/{key}", path, {"sha256": item["sha256"]})
    for item in read(REPORTS / "a41-result.json")["direct_diagnostics"]:
        edge("a41-result.json/direct_diagnostics", REPO / item["log"], {"bytes": item["log_bytes"], "sha256": item["log_sha256"]})
    for item in refresh["commands"]:
        edge("a44-package-refresh.json/commands", REPORTS / item["log"], item["identity"])
    mismatch_edges = [x for x in edges if not x["matches"]]
    expected_target = str((REPORTS / "a44-final-package-result.json").relative_to(REPO))
    check(len(mismatch_edges) == 3 and all(x["target"] == expected_target and x["expected"]["sha256"] == "738ac4970c5cb225e9b3fda8933f6145eebb557e0c2d5ecb46de08a8b9095047" for x in mismatch_edges), "only documented A46/A44 edge mismatch")

    a44_final_path = REPORTS / "a44-final-package-result.json"
    a44_final = read(a44_final_path)
    candidate = dict(a44_final)
    renames = {"runtime_packages": "packages", "build_install_drift_during_runtime": "build_install_drift"}
    for key, old_key in renames.items():
        candidate[old_key] = candidate.pop(key)
    candidate_bytes = (json.dumps(candidate, indent=2, sort_keys=True) + "\n").encode()
    check(len(candidate_bytes) == 3486 and sha(candidate_bytes) == mismatch_edges[0]["expected"]["sha256"], "exact earlier record reconstruction")
    recovered_path = REPORTS / "a50-reconstructed-a44-at-capture.json"
    recovered_path.write_bytes(candidate_bytes)
    restored = dict(candidate)
    for current, old in renames.items():
        restored[current] = restored.pop(old)
    check(restored == a44_final and a44_final_path.read_bytes() == blob(PUBLISHED, expected_target), "all values equal published A44 under exact two-key mapping")
    serialization_matches = []
    for indent, sort_keys, ensure_ascii, separators, newline in itertools.product(
            (None, 0, 1, 2, 4), (False, True), (False, True), (None, (",", ":"), (", ", ": "), (",", ": ")), ("", "\n", "\r\n")):
        encoded = (json.dumps(a44_final, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii, separators=separators) + newline).encode()
        if sha(encoded) == sha(candidate_bytes):
            serialization_matches.append([indent, sort_keys, ensure_ascii, separators, newline])
    reconcile = {"schema": "a50-a46-a44-report-edge-reconciliation-v1", "kind": "additive independently derived reconciliation; original capture records unchanged",
                 "published_commit": PUBLISHED, "published_final": {"path": expected_target, **identity(a44_final_path)},
                 "earlier_pin": mismatch_edges[0]["expected"], "original_archive_found": False,
                 "reconstruction": {"path": str(recovered_path.relative_to(REPO)), **identity(recovered_path),
                                    "method": "Rename exactly the two top-level keys below in the published final JSON; json.dumps(indent=2, sort_keys=True), default ensure_ascii=True, UTF-8 plus LF.",
                                    "final_to_earlier_key_renames": renames, "all_values_identical_under_renames": restored == a44_final,
                                    "status": "Reconstructed bytes match the original pin exactly; not an independently archived original."},
                 "ordinary_serialization_variants_of_unrenamed_final_matching_pin": serialization_matches,
                 "affected_edges": mismatch_edges, "semantic_checks": {
                     "midi_on_binary_matches_v2": a44_final["final_packages"]["midi-on"]["executable"] == provenance["executable"]["before"],
                     "98_product_map_matches": a44_source["production_sha256"] == {p: x["sha256"] for p, x in production.items()},
                     "final_guide_and_payload_records_consistent": all(
                         list(package["only_payload_change"]) == ["share/hammond-b3-organ/standalone/MIDI_UI_RUNBOOK.md"]
                         and package["only_payload_change"]["share/hammond-b3-organ/standalone/MIDI_UI_RUNBOOK.md"]["final"]["sha256"] == a44_final["final_guide_sha256"]
                         and package["payload_count"] == a44_final["final_packages"][mode]["payload_files"]
                         and package["payload"]["bin/hammond_standalone"] == a44_final["final_packages"][mode]["executable"]
                         for mode, package in refresh["packages"].items())},
                 "limits": "This establishes exact JSON ancestry under two key renames. It does not prove when or who changed that report, independently archive the earlier file, rebuild the binary, or regenerate any capture."}
    check(all(reconcile["semantic_checks"].values()), "A44 final package semantic edges")
    write("a50-a46-a44-edge-reconciliation.json", reconcile)

    docs = [REPO / "README.md", GALLERY / "README.md", REPO / "docs/reviews/INTERFACE_FINAL_GALLERY.md",
            REPO / "docs/research/INTERFACE_ATLAS_REVIEW.md", REPO / "docs/REFERENCE_ART_ASSETS.md", REPO / "docs/STANDALONE_FONTS.md"]
    docs += [REPO / "docs/development/2026-11-14-interface-continuation" / name for name in (
        "session41-native-sanitizers.md", "session43-native-leak-ci.md", "session44-final-package.md", "session45-documentation-freshness.md", "session46-final-native-gallery.md")]
    missing, link_count = [], 0
    for doc in docs:
        for raw in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", doc.read_text()):
            target = raw.split(' "', 1)[0]
            if urlsplit(target).scheme or target.startswith("#"):
                continue
            path = doc.parent / unquote(target.split("#", 1)[0])
            link_count += 1
            if not path.exists():
                missing.append({"document": str(doc.relative_to(REPO)), "target": target})
    check(not missing, "targeted local document links")
    report = {"schema": "a50-final-visual-provenance-audit-v1", "assignment": 50, "worker": "/root/w09_a50_provenance_assets",
              "started_at_utc": start, "finished_at_utc": datetime.now(timezone.utc).isoformat(), "observed_head": head,
              "published_commit_compared": PUBLISHED, "capture_product_commit": CAPTURE_COMMIT,
              "status": "verified_with_documented_report_edge_reconciliation" if not failures else "failed",
              "evidence_method": "Read-only hashes, PDF embedded-stream inspection, in-memory crop/RLE decoding, source inspection and retained diagnostic/report inspection. Writes only A50 outputs.",
              "new_native_invocations": 0, "new_builds": 0, "new_images": 0,
              "a12_visual_boundary": assets, "pdf": {"pages": len(document), "page_image_objects": image_objects, "sha256": sha(pdf.read_bytes()), "embedded_original_jpeg_matches": embedded == jpeg.read_bytes()},
              "reference_crops": crops, "font_atlases": font_rows, "generated_reference_header": identity(generated), "font_header": identity(font_header),
              "executable": identity(exe), "source_scopes": {"admitted": 10, "observed_product": 98, "selected_build": 13,
                  "source_inventory_sha256": provenance["source"]["inventory_sha256_before"], "build_inventory_sha256": provenance["build"]["inventory_sha256_before"],
                  "production_mismatches": product_mismatches, "build_boundary": provenance["build"]["boundary"]},
              "galleries": gallery_rows, "v2_pngs": images, "report_edges_checked": len(edges), "report_edge_mismatches": mismatch_edges,
              "reconciliation": {"path": str((REPORTS / "a50-a46-a44-edge-reconciliation.json").relative_to(REPO)), **identity(REPORTS / "a50-a46-a44-edge-reconciliation.json")},
              "targeted_document_links": {"documents": len(docs), "local_links_checked": link_count, "missing": missing},
              "failures": failures, "limits": ["No independent full source-to-binary or complete dependency attestation.",
                  "Original BMPs were removed by the producer after its verification; A50 independently verified retained PNGs only.",
                  "No new full-PDF reading, visual-fidelity comparison, native run, physical-device test or rights conclusion.",
                  "The original atlas/source asset/notice records remain the authority for their stated provenance and unresolved permissions."]}
    write("a50-provenance-audit.json", report)
    print(json.dumps({"status": report["status"], "assets": len(assets), "product_files": len(production), "pngs": len(images), "report_edges": len(edges), "reconciled_edges": len(mismatch_edges), "local_links": link_count, "failures": failures}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
