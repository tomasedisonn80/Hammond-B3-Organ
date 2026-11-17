#!/usr/bin/env python3
"""Bind an admitted workflow template to root's exact published source; never run it."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

TEMPLATE_SHA256 = "d236ef46a4d0069e7865abd47bbef02f99c25337c7e28d853ac373b9951d2c54"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", required=True, help="Full published source commit, not a branch")
parser.add_argument("--tree", required=True, help="Full independently verified source tree")
parser.add_argument("--output", type=Path, required=True, help="NEW scratch workflow file")
args = parser.parse_args()
for value in (args.source, args.tree):
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise SystemExit("Source and tree must be complete lowercase 40-digit Git IDs")
template_path = Path(__file__).with_name("workflow.template.yml")
original = template_path.read_bytes()
if hashlib.sha256(original).hexdigest() != TEMPLATE_SHA256:
    raise SystemExit("Admitted workflow template identity differs")
repository = subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                     cwd=template_path.parent, text=True).strip()
actual = subprocess.check_output(["git", "show", "-s", "--format=%H%n%T%n%P", args.source],
                                 cwd=repository, text=True).splitlines()
if actual[:2] != [args.source, args.tree]:
    raise SystemExit("Local immutable source commit/tree does not match the supplied identities")
source_marker, tree_marker, short_marker = (
    b"__COMBINED_SOURCE_SHA__", b"__COMBINED_SOURCE_TREE__", b"__COMBINED_SOURCE_SHORT__")
if [original.count(x) for x in (source_marker, tree_marker, short_marker)] != [2, 1, 1]:
    raise SystemExit("Unexpected placeholder inventory")
bound = original.replace(source_marker, args.source.encode()).replace(tree_marker, args.tree.encode())
bound = bound.replace(short_marker, args.source[:7].encode())
if b"__COMBINED_SOURCE_" in bound:
    raise SystemExit("Unbound source placeholder remains")
restored = bound.replace(args.source.encode(), source_marker).replace(args.tree.encode(), tree_marker)
branch = b"investigate/windows-combined-candidate-"
restored = restored.replace(branch + args.source[:7].encode(), branch + short_marker)
if restored != original:
    raise SystemExit("Binding changed bytes outside the four admitted substitutions")
with args.output.open("xb") as stream:
    stream.write(bound)
print(json.dumps({"source_commit": args.source, "source_tree": args.tree,
                  "source_parents": actual[2].split() if len(actual) > 2 else [],
                  "source_identity_check": "Local immutable Git objects; root must also verify remote publication",
                  "workflow_template_sha256": TEMPLATE_SHA256,
                  "workflow_path": str(args.output.resolve()), "workflow_bytes": len(bound),
                  "workflow_sha256": hashlib.sha256(bound).hexdigest(),
                  "trigger_branch": "investigate/windows-combined-candidate-" + args.source[:7],
                  "executed": False}, indent=2, sort_keys=True))
