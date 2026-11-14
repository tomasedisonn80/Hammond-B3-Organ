#!/usr/bin/env python3
"""Read-only verification of retained A46 payload, pixels and native records.

This separate reader does not import the producer's validation implementation,
launch another app, alter captured files, or require the live build tree.
"""

import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image


REPO = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent
GALLERY = REPO / "examples/demos/standalone-interface-preview-v2"
EXPECTED = [
    ("play-reference-1672x941", 1672, 941, "play", "dimensional", 66),
    ("play-default-1280x900", 1280, 900, "play", "dimensional", 66),
    ("play-minimum-960x700", 960, 700, "play", "dimensional", 66),
    ("service-reference-1672x941", 1672, 941, "service", "dimensional", 66),
    ("service-minimum-960x700", 960, 700, "service", "dimensional", 66),
    ("rotary-reference-1672x941", 1672, 941, "rotary", "dimensional", 66),
    ("rotary-minimum-960x700", 960, 700, "rotary", "dimensional", 66),
    ("flat-minimum-960x700", 960, 700, "play", "flat", 68),
]
EXPECTED_CONTROLS = {
    "manual_drawbars": [[[1, 2, 3, 4, 5, 6, 7, 8, 0], [8, 6, 5, 4, 3, 4, 2, 5, 3]],
                        [[7, 6, 5, 4, 3, 4, 2, 4, 2], [0, 0, 8, 0, 0, 0, 0, 0, 0]]],
    "selected_banks": [1, 0], "fixed_registrations": [1, 0], "preset_selections": [1, 10],
    "route_enabled": [True, True], "expression": 0.75, "pedal_drawbars": [8, 0],
    "percussion": {"enabled": True, "harmonic": 0, "volume": 0, "decay": 0},
}


def read(path):
    return json.loads(path.read_text())


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main():
    provenance = read(GALLERY / "provenance.json")
    manifest = read(GALLERY / "manifest.json")
    assert provenance["status"] == manifest["status"] == "passed"
    assert provenance["all_recorded_inputs_unchanged"]
    assert len(manifest["files"]) == 39 and len(provenance["cases"]) == 8
    for name, expected in manifest["files"].items():
        assert identity(GALLERY / name) == expected, name
    assert manifest["total_bytes_excluding_manifest"] == sum(x["bytes"] for x in manifest["files"].values())
    assert len(list(GALLERY.rglob("*.png"))) == 8 and not list(GALLERY.rglob("*.bmp"))
    assert provenance["source"]["changed_paths"] == provenance["build"]["changed_paths"] == []
    assert len(provenance["source"]["files"]) == 98 and len(provenance["build"]["files"]) == 13
    assert provenance["executable"]["before"] == provenance["executable"]["after"]
    assert provenance["executable"]["after"]["sha256"] == "bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2"
    assert provenance["inputs"]["before"] == provenance["inputs"]["after"]
    assert provenance["tool"]["before"] == provenance["tool"]["after"]
    images = []
    for expected, case in zip(EXPECTED, provenance["cases"]):
        name, width, height, workspace, presentation, events = expected
        assert case["name"] == name and case["status"] == "passed" and case["exit_code"] == 0
        item = case["image"]
        with Image.open(GALLERY / item["path"]) as decoded:
            decoded.load()
            assert decoded.format == "PNG" and decoded.size == (width, height) and decoded.mode == "RGBA"
            pixel_digest = hashlib.sha256(decoded.tobytes()).hexdigest()
            assert pixel_digest == item["decoded_sha256"] and decoded.mode == item["decoded_mode"]
        assert identity(GALLERY / item["path"]) == item["png"]
        assert item["lossless_bmp_to_png"] and item["native_bmp_removed_after_verification"]
        diag = read(GALLERY / case["diagnostics"]["path"])
        assert diag["application"] == "hammond_standalone" and diag["schema_version"] == 3
        assert diag["errors"] == {"count": 0, "last": ""}
        assert diag["runtime"]["video_driver"] == diag["audio"]["driver"] == "dummy"
        assert diag["runtime"]["renderer"] == "software" and diag["runtime"]["sdl_version"] == "2.32.10"
        assert [diag["runtime"][k] for k in ("window_width", "window_height", "drawable_width", "drawable_height")] == [width, height, width, height]
        replay = diag["replay"]
        assert all(replay[k] for k in ("completed", "delivered", "passed", "final_acknowledged", "snapshot_available_before_shutdown"))
        assert replay["duration_ms"] == 1800 and replay["scheduled_events"] == replay["pushed_events"] == events
        assert replay["accepted_note_on_commands"] == 4 and replay["accepted_note_off_commands"] == 0
        assert replay["controls_pending_before_shutdown"] is False and replay["save_pending_before_shutdown"] is False
        assert replay["before_shutdown"]["manual_notes"] == [[60, 64], [67]] and replay["before_shutdown"]["pedal_ids"] == [3]
        assert diag["controls"] == replay["desired_controls_before_shutdown"] == replay["before_shutdown"]["controls"] == EXPECTED_CONTROLS
        initial = json.loads(json.dumps(EXPECTED_CONTROLS))
        initial["manual_drawbars"][0][1][0] = 7
        assert any(o["controls"] == initial and o["manual_notes"] == [[60, 64], [67]] and o["pedal_ids"] == [3] for o in replay["observations"])
        painted = diag["presentation"]["screenshot"]
        assert painted == diag["presentation"]["last_painted"] == diag["presentation"]["before_shutdown"]
        assert (painted["workspace"], painted["presentation"], painted["overlay"]) == (workspace, presentation, "none")
        assert painted["elapsed_ms"] >= 1800 and painted["inspection"]["snapshot_state"] == "current"
        assert painted["inspection"]["snapshot_read_succeeded"] and painted["inspection"]["controls_pending"] is False
        assert diag["session"]["held_after_shutdown"] is False and diag["session"]["running_after_shutdown"] is False
        midi = diag["midi"]
        assert midi["source"] == "none" and midi["backend_available"] and midi["backend"] == "ALSA"
        assert midi["discovery"]["requests"] == 0 and midi["generation"] == 0 and midi["requested_port"] == midi["port_name"] == ""
        assert all(v == 0 for v in midi["device"].values())
        assert midi["state_before_shutdown"] == midi["state_after_shutdown"] == "closed"
        assert midi["quiescent_after_shutdown"] and midi["diagnostics_stable_after_shutdown"] and not midi["shutdown_failed"]
        assert (GALLERY / f"diagnostics/{name}.stdout.txt").stat().st_size == 0
        assert (GALLERY / f"diagnostics/{name}.stderr.txt").stat().st_size == 0
        images.append({"name": name, "width": width, "height": height, **item["png"],
                       "decoded_mode": "RGBA", "decoded_sha256": pixel_digest,
                       "ui_events": events, "callback_count": diag["audio"]["callback_count"],
                       "rendered_frames": diag["audio"]["rendered_frames"],
                       "rendered_images": diag["runtime"]["rendered_images"], "status": "passed"})
    old = REPO / "examples/demos/standalone-interface-preview-v1"
    old_manifest = read(old / "manifest.json")
    for name, expected in old_manifest["files"].items():
        assert identity(old / name) == expected
    old_files = [p for p in old.rglob("*") if p.is_file()]
    for path in old_files:
        published = subprocess.check_output(["git", "-C", str(REPO), "show", f"8673713:{path.relative_to(REPO)}"])
        assert path.read_bytes() == published
    result = {"schema": "a46-independent-gallery-verification-v1", "assignment": 46, "status": "passed",
              "capture_manifest_files_verified": 39, "decoded_pngs_verified": 8,
              "png_bytes_total": sum(x["bytes"] for x in images), "images": images,
              "gallery_provenance": identity(GALLERY / "provenance.json"),
              "gallery_manifest": identity(GALLERY / "manifest.json"),
              "v1_manifest_files_verified": len(old_manifest["files"]),
              "v1_all_files_equal_published_blobs": len(old_files),
              "retained_native_diagnostics_rechecked": 8, "new_native_invocations": 0,
              "scope": "Independent reader recomputed payload bytes and every decoded PNG identity, and read the retained actual native records. Producer-reported original BMP identity is retained; BMP was already removed after producer decoded equality verification. No claim of a second app execution or independent build follows."}
    (REPORTS / "a46-gallery-verification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "images"}, indent=2))


if __name__ == "__main__":
    main()
