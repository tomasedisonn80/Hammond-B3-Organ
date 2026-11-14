#!/usr/bin/env python3
"""Read-only documentation/provenance audit; prints JSON, runs no native tests."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

from PIL import Image


ROOT = Path(__file__).resolve().parents[4]
COMMIT = "0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b"
TREE = "f8144b771cda1264a8788f8297f5bfec999f4a08"
EXE = "01fe78a55b7a9bc72228dafe175f5a8eb48481c063f217606474d4dff682320f"
GALLERY = ROOT / "examples/demos/standalone-interface-preview-v4"
DOCUMENTS = [ROOT / "README.md", ROOT / "docs/INTERFACE_RUNBOOK.md"]
REPO_URL = "https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/main/"
errors = []


def require(condition, description):
    if not condition:
        errors.append(description)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": digest(data)}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def heading_ids(path):
    ids = set()
    repeats = {}
    for line in path.read_text().splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if match:
            value = re.sub(r"[^\w\- ]", "", match[1].lower()).replace(" ", "-")
            count = repeats.get(value, 0)
            repeats[value] = count + 1
            ids.add(value if count == 0 else f"{value}-{count}")
    return ids


links = []
external = []
document_identities = {}
for document in DOCUMENTS:
    name = str(document.relative_to(ROOT))
    content = document.read_text()
    document_identities[name] = identity(document)
    for marker, target in re.findall(r"(!?)\[[^\]]*\]\(([^)\s]+)\)", content):
        if target.startswith(REPO_URL):
            destination = target[len(REPO_URL):]
            base = ROOT
        elif urlsplit(target).scheme:
            external.append({"document": name, "url": target})
            continue
        else:
            destination = target
            base = document.parent
        parsed = urlsplit(destination)
        path = (base / unquote(parsed.path)).resolve() if parsed.path else document
        exists = path.exists()
        anchor_ok = not parsed.fragment or (
            exists and path.suffix == ".md" and unquote(parsed.fragment) in heading_ids(path)
        )
        require(exists, f"Missing link from {name}: {target}")
        require(anchor_ok, f"Missing heading from {name}: {target}")
        links.append({"document": name, "target": target, "image": bool(marker),
                      "exists": exists, "anchor_valid": anchor_ok})
    for value in (COMMIT, TREE, EXE):
        require(value in content, f"{name} omits capture identity {value}")
    require("1:1 equality" in content, f"{name} omits explicit reference-equality limit")

qualification = json.loads((GALLERY / "inputs/source-qualification.json").read_text())
provenance = json.loads((GALLERY / "provenance.json").read_text())
manifest = json.loads((GALLERY / "manifest.json").read_text())
require(qualification["published_commit"] == COMMIT, "Qualification commit differs")
require(qualification["published_tree"] == TREE, "Qualification tree differs")
require(git("rev-parse", COMMIT + "^{tree}").decode().strip() == TREE, "Git tree differs")
require(qualification["binary_sha256"] == EXE, "Qualified executable differs")
require(provenance["executable"]["before"]["sha256"] == EXE, "Capture executable differs")
require(provenance["executable"]["after"] == provenance["executable"]["before"],
        "Capture executable changed")
require(provenance["all_recorded_inputs_unchanged"], "Capture records changed inputs")

source_matches = []
for name, expected in qualification["source_sha256"].items():
    published = digest(git("show", f"{COMMIT}:{name}"))
    current = digest((ROOT / name).read_bytes())
    require(published == expected == current, f"Qualified source mismatch: {name}")
    source_matches.append(name)
require(len(source_matches) == qualification["source_file_count"], "Source count differs")

payload_matches = []
for name, expected in manifest["files"].items():
    require(identity(GALLERY / name) == expected, f"Gallery payload mismatch: {name}")
    payload_matches.append(name)

images = []
for case in provenance["cases"]:
    frame = case["image"]
    path = GALLERY / frame["path"]
    with Image.open(path) as opened:
        rgba = opened.convert("RGBA")
        size = list(rgba.size)
        decoded = digest(rgba.tobytes())
    require(identity(path) == frame["png"], f"PNG byte identity differs: {path.name}")
    require(size == [case["width"], case["height"]], f"PNG dimensions differ: {path.name}")
    require(decoded == frame["decoded_sha256"], f"Decoded PNG identity differs: {path.name}")
    painted = case["validation"]["actual_painted_view"]
    require(painted["held_targets"] == {"upper": 2, "lower": 1, "pedals": 1},
            f"Documented painted target counts differ: {path.name}")
    require(painted["inspection"]["controls_pending"] is False,
            f"Documented acknowledged endpoint differs: {path.name}")
    images.append({"path": str(path.relative_to(ROOT)), "size": size,
                   **identity(path), "decoded_rgba_sha256": decoded})
require(len(images) == 8, "Gallery does not have eight recorded images")

readme = DOCUMENTS[0].read_text()
ui_section = readme.split("## Native interface and UI/UX design", 1)[1].split("## External MIDI", 1)[0]
embedded = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", ui_section)
require(len(embedded) == 3 and all("standalone-interface-preview-v4/images/" in p for p in embedded),
        "Current UI embeds do not all identify v4")
baseline_readme = git("show", f"{COMMIT}:README.md").decode()
checkpoint_pattern = r"(?m)^\*\*Current checkpoint:\*\*.*$"
checkpoint_now = re.search(checkpoint_pattern, readme).group()
checkpoint_before = re.search(checkpoint_pattern, baseline_readme).group()
require(checkpoint_now == checkpoint_before, "Concurrent waveform checkpoint changed")

prior = {}
for version in (1, 2, 3):
    directory = f"examples/demos/standalone-interface-preview-v{version}"
    records = git("ls-tree", "-r", "-z", COMMIT, "--", directory).split(b"\0")
    names = []
    for record in filter(None, records):
        metadata, name_bytes = record.split(b"\t", 1)
        name = name_bytes.decode()
        expected = metadata.split()[2].decode()
        data = (ROOT / name).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == expected, f"Historical gallery changed: {name}")
        names.append(name)
    current_names = sorted(str(p.relative_to(ROOT)) for p in (ROOT / directory).rglob("*") if p.is_file())
    require(current_names == sorted(names), f"Historical gallery file set differs: {directory}")
    prior[f"v{version}"] = {"files_compared_to_published_blobs": len(names), "unchanged": current_names == sorted(names)}

reference_manifest = json.loads((ROOT / "docs/design/atlas-reference.json").read_text())
reference = ROOT / reference_manifest["image"]
require(identity(reference)["sha256"] == reference_manifest["sha256"], "Original reference changed")
diff_check = subprocess.run(["git", "diff", "--check", "--", "README.md", "docs/INTERFACE_RUNBOOK.md"],
                            cwd=ROOT, text=True, capture_output=True)
require(diff_check.returncode == 0, "Documentation diff has whitespace errors")
report = {
    "schema": "a47-readme-current-ui-check-v1", "assignment": "A47",
    "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    "command": f"python3 {Path(__file__).relative_to(ROOT)}",
    "cwd": str(ROOT), "python": sys.version.split()[0],
    "scope": "Read-only link/image/source provenance checks for two edited documents; no build, native run, project test or acceptance rerun.",
    "script": identity(Path(__file__)), "published_product_commit": COMMIT,
    "published_product_tree": TREE, "capture_executable_sha256": EXE,
    "documents": document_identities, "resolved_links": links,
    "resolved_link_count": len(links), "unique_resolved_target_count": len({item["target"] for item in links}),
    "external_links_not_requested": external,
    "gallery_payloads_matched": len(payload_matches), "qualified_sources_matched": len(source_matches),
    "gallery_provenance": identity(GALLERY / "provenance.json"),
    "gallery_manifest": identity(GALLERY / "manifest.json"),
    "gallery_readme": identity(GALLERY / "README.md"), "images": images,
    "readme_current_ui_embeds": embedded, "waveform_top_checkpoint_unchanged": checkpoint_now == checkpoint_before,
    "prior_galleries": prior, "original_reference": identity(reference),
    "direct_visual_inspection": [reference_manifest["image"], *embedded],
    "visual_inspection_boundary": "A47 directly opened the original reference and the three README images; no crop, retouching, resampling or new fidelity measurement.",
    "diff_check": {"exit_code": diff_check.returncode, "stdout": diff_check.stdout, "stderr": diff_check.stderr},
    "errors": errors, "status": "passed" if not errors else "failed",
}
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(0 if not errors else 1)
