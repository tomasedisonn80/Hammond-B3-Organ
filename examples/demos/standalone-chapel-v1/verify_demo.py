#!/usr/bin/env python3
"""Verify retained chapel-demo bytes, musical endpoints and rendered pixels.

This checks the recorded bundle, not a new app/device execution or authenticity.
Python 3.10+ and Pillow are authoring/verification prerequisites only.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parent
STATE = b"""B3CONTROLS3
expression 0.5
percussion enabled 0 harmonic second volume normal decay slow
pedal drawbars 0 0
manual upper selected B route_enabled 1
bank A 0 0 0 0 0 0 0 0 0
bank B 0 0 5 3 2 0 0 0 0
manual lower selected B route_enabled 1
bank A 0 0 0 0 0 0 0 0 0
bank B 4 2 7 8 6 6 2 4 4
end
"""
CONTROLS = {
    "manual_drawbars": [[[0]*9, [0,0,5,3,2,0,0,0,0]],
                        [[0]*9, [4,2,7,8,6,6,2,4,4]]],
    "selected_banks": [1,1], "route_enabled": [True,True], "expression": 0.5,
    "pedal_drawbars": [0,0],
    "percussion": {"enabled": False, "harmonic": 0, "volume": 0, "decay": 0},
}
EVENTS = ["100 key_down F1 none 0", "110 key_up F1 none", "200 key_down A none 0",
          "450 key_down F2 none 0", "460 key_up F2 none", "650 key_down D none 0",
          "900 key_down F1 none 0", "910 key_up F1 none"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON field {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"non-JSON number {value}")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def held(item):
    return tuple(tuple(notes) for notes in item["manual_notes"]), tuple(item["pedal_ids"])


def main():
    manifest = read_json(ROOT/"manifest.json")
    require(manifest["schema_version"] == 1, "manifest schema")
    names = [entry["path"] for entry in manifest["files"]]
    require(len(names) == len(set(names)) == 9, "manifest coverage")
    require(set(path.name for path in ROOT.iterdir()) == set(names)|{"manifest.json"},
            "unexpected or missing artifact entry")
    total_bytes = (ROOT/"manifest.json").stat().st_size
    for entry in manifest["files"]:
        path = ROOT/entry["path"]
        require(path.parent == ROOT and not path.is_symlink() and path.is_file(), "ordinary artifact leaf")
        data = path.read_bytes()
        require(len(data) == entry["bytes"] and sha(data) == entry["sha256"], f"byte identity: {path.name}")
        total_bytes += len(data)
    require(total_bytes < 1_000_000, "bundle size bound")
    require((ROOT/"chapel-pair.b3controls").read_bytes() == STATE, "literal complete control state")
    lines = (ROOT/"held-manuals.b3ui").read_text(encoding="ascii").splitlines()
    require(lines[:2] == ["B3UIREPLAY1", "duration_ms 1400"], "replay header")
    require([line for line in lines[2:] if line and not line.startswith("#")] == EVENTS,
            "literal eight-action replay")
    provenance = read_json(ROOT/"provenance.json")
    require(provenance["source"]["published_commit"] == "0085e338388f2c7516a7d455f11692b94e9451f4", "source commit")
    require(provenance["source"]["git_tree"] == "19c763503f67e1f054d2d27b6ec3d8fca2e36474", "source tree")
    require(provenance["binary"]["sha256"] == "def97cef70b3eafcd108170a985c61215b878c918debde6ff2fb236a2a9c3416", "binary identity")
    require(len(provenance["runs"]) == 2, "two actual captures")
    summaries = []
    for name, size in [("reference",(1280,900)), ("minimum",(960,700))]:
        records = [run for run in provenance["runs"] if run["name"] == name]
        require(len(records) == 1, "unique capture record")
        record = records[0]
        require(record["returncode"] == record["stdout_bytes"] == record["stderr_bytes"] == 0,
                f"successful silent process: {name}")
        data = read_json(ROOT/(name+".json"))
        require(sha((ROOT/(name+".json")).read_bytes()) == record["diagnostics"]["sha256"], "original diagnostics bytes")
        require(data["schema_version"] == 1 and data["controls"] == CONTROLS, "complete controls")
        require(data["profile"] == {"id":"nominal-unmeasured-v1", "authoring_sha256":"49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83"}, "profile metadata")
        require(data["errors"] == {"count":0,"last":""}, "app errors")
        runtime, audio, session, replay = (data[k] for k in ("runtime","audio","session","replay"))
        require(runtime["video_driver"] == "dummy" and runtime["renderer"] == "software", "render backend")
        require(runtime["sdl_version"] == "2.32.10", "SDL version")
        require([runtime[k] for k in ("window_width","window_height","drawable_width","drawable_height")] == [*size,*size], "actual dimensions")
        require(runtime["screenshot_written"] and runtime["screenshot_while_held"] and runtime["rendered_images"] > 0, "held capture")
        require(audio["driver"] == "dummy" and audio["sample_rate"] == 48000 and audio["buffer_frames"] == 512, "audio configuration")
        require(audio["channels"] == 2 and audio["sample_format"] == audio["native_float32_format"], "native stereo format")
        require(audio["buffer_bytes"] == 4096 and audio["open_before_shutdown"] and audio["running_before_shutdown"], "active device")
        require(audio["callback_count"] > 0 and audio["rendered_frames"] == audio["callback_count"]*512, "callback work")
        require(all(audio[key] == 0 for key in ("render_failures","format_failures","nonfinite_failures","nonfinite_samples","overrange_failures","overrange_samples")), "audio fault")
        require(audio["last_render_status"] == audio["last_lifecycle_status"] == "ok", "audio status")
        require(session["snapshot_available"] and session["prepared"] and not session["running_after_shutdown"] and not session["held_after_shutdown"], "joined empty shutdown")
        require(session["sample_rate"] == 48000 and session["frame_clock"] == audio["rendered_frames"], "frame clock")
        require(all(session[key] == 0 for key in ("recovery_count","queue_overflows","rejected_commands","fault_flags")), "session fault")
        require(0 < session["maximum_observed_peak"] <= 1, "positive bounded nominal output")
        require(all(replay[key] for key in ("completed","delivered","passed","final_acknowledged")), "completed acknowledged replay")
        require(replay["duration_ms"] == 1400 and replay["scheduled_events"] == replay["pushed_events"] == 8, "event delivery")
        require(replay["accepted_note_on_commands"] == 2 and replay["accepted_note_off_commands"] == 0, "scripted note command counts")
        require(replay["device_starts"] == 1 and not replay["observations_truncated"], "complete observation scope")
        require(session["discarded_commands"] <= replay["device_starts"], "bounded automatic shutdown cleanup")
        endpoint = replay["before_shutdown"]
        require(endpoint["controls"] == CONTROLS and held(endpoint) == (((60,),(64,)),()), "actual two-manual held endpoint")
        require(endpoint["resolved_sequence"] == endpoint["last_applied_sequence"] == replay["last_submitted_sequence"], "final script prefix acknowledged")
        allowed = {(((),()),()):0, (((60,),()),()):1, (((60,),(64,)),()):2}
        previous_stage = previous_sequence = 0
        for item in [*replay["observations"], endpoint]:
            require(item["controls"] == CONTROLS, "observed controls")
            require(held(item) in allowed and allowed[held(item)] >= previous_stage, "original note ownership")
            require(item["resolved_sequence"] == item["last_applied_sequence"] >= previous_sequence, "coherent monotonic sequence")
            require(item["last_applied_sequence"] <= item.get("last_submitted_sequence", replay["last_submitted_sequence"]) <= replay["last_submitted_sequence"], "submitted prefix")
            previous_stage, previous_sequence = allowed[held(item)], item["last_applied_sequence"]
        require(sha((ROOT/(name+".png")).read_bytes()) == record["png"]["sha256"], "PNG bytes")
        with Image.open(ROOT/(name+".png")) as image:
            image.load()
            require(image.format == "PNG" and image.size == size and image.mode == "RGBA", "PNG decoded shape")
            require(sha(image.tobytes()) == record["png"]["decoded_pixel_sha256"], "full decoded pixels")
            colors = {}
            for key, sample in record["pixel_samples"].items():
                colors[key] = list(image.getpixel(tuple(sample["xy"])))
                require(colors[key] == sample["rgba"], "retained literal pixel")
            require(colors["upper_c4"] != colors["upper_d4"] == colors["upper_e4"], "pictured Upper C4")
            require(colors["lower_e4"] != colors["lower_c4"] == colors["lower_d4"], "pictured Lower E4")
        summaries.append({"case":name,"callbacks":audio["callback_count"],"frames":audio["rendered_frames"],
                          "images":runtime["rendered_images"],"script_sequence":replay["last_submitted_sequence"]})
    print(json.dumps({"status":"passed","files":10,"bytes":total_bytes,"captures":summaries,
                      "scope":"retained software-demo evidence; no new execution or physical qualification"},indent=2))


if __name__ == "__main__":
    main()
