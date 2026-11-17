"""Reproduce the root-owned documentary merge from three immutable Git trees.

This records a navigation resolution, not implementation/test execution.
Run only in the authorized console checkout while resolving the named merge.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

OURS = "1acb04ee4408bedd889909c05afd1c48661a9b81"
INCOMING = "d216279911a69a364426bef9d5e0b7b5221bd024"
BASE = "893441fe87859b9dbad81a5d81a453f7c96030f8"
ROOT = Path(__file__).resolve().parents[4]


def read(tree, name):
    return subprocess.check_output(["git", "show", tree + ":" + name], cwd=ROOT).decode()


def bounded(text, start, end):
    assert text.count(start) == text.count(end) == 1
    a = text.index(start)
    b = text.index(end, a) + len(end)
    return a, b, text[a:b]


def replace_marker(name, marker):
    ours, incoming = read(OURS, name), read(INCOMING, name)
    start, end = "<!-- " + marker + ":start -->", "<!-- " + marker + ":end -->"
    _, _, block = bounded(ours, start, end)
    a, b, prior = bounded(incoming, start, end)
    aliases = [x for x in re.findall(r'<a id="[^"]+"></a>', prior) if x not in block]
    title = re.search(r"^## (.+)$", prior, re.M).group(1)
    slug = re.sub(r"[^\w\s-]", "", title.lower()).replace(" ", "-")
    alias = '<a id="' + slug + '"></a>'
    if alias not in block and title not in block:
        aliases.append(alias)
    if aliases:
        block = block.replace(start, start + "\n" + "\n".join(aliases), 1)
    if name == "README.md":
        runtime = re.search(r"The runtime[\s\S]*?labels remain intact\.\n", prior).group(0)
        hero = prior[prior.index("![Actual combined native Play"):prior.index("**LibraryModel")]
        point = "**LibraryModel and the UiModel recall helper are delivered foundations.**"
        assert block.count(point) == 1
        block = block.replace(point, runtime + "\n" + hero + point, 1)
    if name == "docs/STATUS.md":
        setup = """### Current workspace and setup

This console continuation owns `/workspace/scratch/21cce69f7784/Hammond-B3-Organ`
and its single coordinated `../build-native`. The heading owner's separate
checkout, build and dependencies remain read-only here. Recover the
[console handoff](CONSOLE_COMPLETION_HANDOFF.md),
[source-verified setup](CONSOLE_SETUP_AND_HANDOFF.md),
[checkpoint](development/2026-11-16-console-completion/CHECKPOINT.md) and
[root queue](development/2026-11-16-console-completion/ROOT_NEXT_QUEUE.md).
Normal clean-checkout desktop commands and recorded dummy-SDL observations have
different scopes; reproduce only the configuration needed for the assigned work.

"""
        point = "### Next implementation and open exits"
        assert block.count(point) == 1
        block = block.replace(point, setup + point, 1)
    if name == "docs/NEXT_STEPS.md":
        extra = prior[prior.index("### 2. Continue the requested whole-interface reference work"):prior.index(end)]
        block = block.replace(end, "### Continuing visual and audio requirements\n\nThe following dependency detail is retained from the concurrent heading owner's\ndelivery. It applies alongside the native-library sequence above and grants no\nwrite authority over another owner's workspace.\n\n" + extra + end, 1)
    merged = incoming[:a] + block + incoming[b:]
    if name == "docs/STATUS.md":
        extra = prior[prior.index("| Local observation |"):prior.index("### Actual interface evidence")]
        marker_end = "<!-- heading-title-status-current:end -->"
        assert merged.count(marker_end) == 1
        merged = merged.replace(marker_end, "### Retained heading-owner local observations\n\nThese are the incoming owner's original source-bound observations; no new\nexecution is attributed to this documentary merge.\n\n" + extra + marker_end, 1)
    return merged


merged = {}
for name, marker in {
    "README.md": "console-completion-summary",
    "docs/PLAN.md": "console-plan-current",
    "docs/STATUS.md": "console-status-current",
    "docs/NEXT_STEPS.md": "console-next-current",
}.items():
    merged[name] = replace_marker(name, marker)

name = "AGENTS.md"
ours, incoming = read(OURS, name), read(INCOMING, name)
own = ours[ours.index("## Current console continuation"):ours.index("## Published heading/header recovery record")]
incoming_start = incoming.index("## Current integrated recovery")
incoming_end = incoming.index("## Retained owner entries")
record = incoming[incoming_start:incoming_end]
record = record.replace("## Current integrated recovery — 17 November 2026", "<a id=\"current-integrated-recovery--17-november-2026\"></a>\n## Retained heading-owner recovery — 17 November 2026", 1)
scope = "The following is the incoming heading owner's delivered recovery record. Its\nreferences to this continuation, current workspace and root apply to that owner\nonly. They grant no write authority in another checkout and do not supersede\nthe current console ownership above. Its accepted work and duties remain intact.\n\n"
record = record.replace("## Retained heading-owner recovery — 17 November 2026\n\n", "## Retained heading-owner recovery — 17 November 2026\n\n" + scope, 1)
merged[name] = incoming[:incoming_start] + own + record + incoming[incoming_end:]

name = "docs/PROJECT_GUIDE.md"
ours, incoming = read(OURS, name), read(INCOMING, name)
own = ours[ours.index("## Current console continuation"):ours.index("## Retained heading/title/header record")]
incoming_start = incoming.index("## Current integrated delivery")
incoming_end = incoming.index("## Find the right entry point")
record = incoming[incoming_start:incoming_end]
record = record.replace("## Current integrated delivery — 17 November 2026", '<a id="current-integrated-delivery--17-november-2026"></a>\n## Retained heading-owner integrated delivery — 17 November 2026', 1)
record = record.replace("## Retained heading-owner integrated delivery — 17 November 2026\n\n", "## Retained heading-owner integrated delivery — 17 November 2026\n\nThis incoming heading-owner record preserves its own setup, accepted workers and\nsource-specific evidence. Its current-workspace routing belongs to that separate\nowner; use the console entry above and the table below for this checkout.\n\n", 1)
merged[name] = incoming[:incoming_start] + own + record + incoming[incoming_end:]

name = "docs/DEVELOPMENT_LOG.md"
ours, incoming, base = read(OURS, name), read(INCOMING, name), read(BASE, name)
header = "# Development log\n\n"
assert all(t.startswith(header) for t in (ours, incoming, base))
assert ours[len(header):].endswith(base[len(header):])
added = ours[len(header):len(ours) - len(base[len(header):])]
assert added and added not in incoming
merged[name] = header + added + incoming[len(header):]

plan = merged["docs/PLAN.md"].splitlines(keepends=True)
for i, line in enumerate(plan):
    if line.startswith("| **Console continuation**"):
        plan[i] = "| **Console continuation**, base `9d60dbf462a90fe422fd4e69757fe202264acb7c` | Current root-owned console foundation/P1 and preserving integration in `/workspace/scratch/21cce69f7784/Hammond-B3-Organ`, coordinated `../build-native`; [handoff](CONSOLE_COMPLETION_HANDOFF.md), [setup](CONSOLE_SETUP_AND_HANDOFF.md), [checkpoint](development/2026-11-16-console-completion/CHECKPOINT.md), [ledger](development/2026-11-16-console-completion/assignments.json). This root accepts and publishes only its authorized work; other workspaces remain read-only. All sixty console workers are accepted separately from the heading owner's records. |\n"
    elif line.startswith("| **Heading/title/header continuation**"):
        plan[i] = "| **Heading/title/header continuation**, base `113c29b7b14c8fde0859bc405ef8e4141a131ea6` | Published heading-owner combined-source delivery from `/workspace/scratch/5a28c3564dbf/Hammond-B3-Organ`; [session](development/2026-11-16-heading-title-continuation/README.md), [checkpoint](development/2026-11-16-heading-title-continuation/CHECKPOINT.md), [ledger](development/2026-11-16-heading-title-continuation/assignments.json). Its sixty accepted workers/ten waves are complete. That root coordinates its own checkout/build, acceptance and publication; its workspace remains read-only here. Preserve its published source/evidence and all original failures. Existing manual/rim/cap/browser/contact/scanner owners remain separate. |\n"
merged["docs/PLAN.md"] = "".join(plan)

guide = merged["docs/PROJECT_GUIDE.md"].splitlines(keepends=True)
routes = {
    "| What should happen next?": "| What should happen next? | [NEXT_STEPS](NEXT_STEPS.md), the [console checkpoint](development/2026-11-16-console-completion/CHECKPOINT.md) and [root queue](development/2026-11-16-console-completion/ROOT_NEXT_QUEUE.md): recover the actual source/result, then admit Save availability and fresh post-Start proof before native browser/main wiring. The [heading checkpoint](development/2026-11-16-heading-title-continuation/CHECKPOINT.md) retains that separate owner's evidence and duties. |\n",
    "| How does a future agent recover this workspace?": "| How does a future agent recover this workspace? | Read all [AGENTS](../AGENTS.md), [PLAN](PLAN.md), the [console handoff](CONSOLE_COMPLETION_HANDOFF.md), [setup](CONSOLE_SETUP_AND_HANDOFF.md), [checkpoint](development/2026-11-16-console-completion/CHECKPOINT.md), [root queue](development/2026-11-16-console-completion/ROOT_NEXT_QUEUE.md) and [ledger](development/2026-11-16-console-completion/assignments.json). Recover the separate [heading handoff](HEADING_TITLE_HEADER_HANDOFF.md) and [heading ledger](development/2026-11-16-heading-title-continuation/assignments.json) before overlap. Inspect fresh local/remote state and exclusive paths. |\n",
    "| How are this session’s actual records checked?": "| How are this session’s actual records checked? | The console [checker](development/2026-11-16-console-completion/check_session.py) and [executed strict result](development/2026-11-16-console-completion/reports/final-worker-strict.json) verify this session's 60 accepted notes/ten waves. The separate heading [checker](development/2026-11-16-heading-title-continuation/check_session.py) and [strict result](development/2026-11-16-heading-title-continuation/reports/helper-worker-strict.json) apply only to that owner's ledger. Neither checker proves external dispatch, execution, publication or product acceptance. |\n",
}
for prefix, replacement in routes.items():
    matched = [i for i, line in enumerate(guide) if line.startswith(prefix)]
    assert len(matched) == 1, prefix
    guide[matched[0]] = replacement
merged["docs/PROJECT_GUIDE.md"] = "".join(guide)

readme = merged["README.md"]
old = """The [current integration checkpoint](docs/development/2026-11-16-heading-title-continuation/CHECKPOINT.md)
and [heading ledger](docs/development/2026-11-16-heading-title-continuation/assignments.json) record this delivery and its
sixty accepted workers. The independent [console checkpoint](docs/development/2026-11-16-console-completion/CHECKPOINT.md)
and [console ledger](docs/development/2026-11-16-console-completion/assignments.json) retain that owner's work and closure. The [product handoff](docs/PRODUCT_HANDOFF.md)
"""
new = """The [current console checkpoint](docs/development/2026-11-16-console-completion/CHECKPOINT.md)
and [console ledger](docs/development/2026-11-16-console-completion/assignments.json) record this delivery and its
sixty accepted workers. The separate [heading-owner checkpoint](docs/development/2026-11-16-heading-title-continuation/CHECKPOINT.md)
and [heading ledger](docs/development/2026-11-16-heading-title-continuation/assignments.json) retain that owner's work and closure. The [product handoff](docs/PRODUCT_HANDOFF.md)
"""
assert readme.count(old) == 1
readme = readme.replace(old, new, 1)
readme = readme.replace("[current integration checkpoint](docs/development/2026-11-16-heading-title-continuation/CHECKPOINT.md)", "[heading-owner integration checkpoint](docs/development/2026-11-16-heading-title-continuation/CHECKPOINT.md)")
readme = readme.replace("[Current reconciled source and recovery](docs/development/2026-11-16-heading-title-continuation/CHECKPOINT.md)", "[Heading-owner reconciled source and recovery](docs/development/2026-11-16-heading-title-continuation/CHECKPOINT.md)")
readme = readme.replace("Independent P1 and copied LibraryModel/recall work, incoming source and actual owner-local records. This ledger is separate from the sixty-worker heading continuation.", "Current console P1 and copied LibraryModel/recall work, preserving integration, setup and actual owner-local records. Its sixty-worker ledger is separate from the heading continuation.")
readme = readme.replace("[current checkpoint](docs/development/2026-11-16-heading-title-continuation/CHECKPOINT.md)", "[owner checkpoint](docs/development/2026-11-16-heading-title-continuation/CHECKPOINT.md)")
readme = readme.replace("Current combined-source integration and publication, exact setup, sixty accepted workers, retained T2/T3/H1/runtime evidence and concrete next work.", "Published heading-owner combined-source integration, exact setup, sixty accepted workers, retained T2/T3/H1/runtime evidence and that owner's concrete next work.")
merged["README.md"] = readme

point = "## Record closure, original evidence and future delivery"
alias = '<a id="validate-this-sessions-actual-records"></a>'
assert merged["docs/NEXT_STEPS.md"].count(point) == 1
assert alias not in merged["docs/NEXT_STEPS.md"]
merged["docs/NEXT_STEPS.md"] = merged["docs/NEXT_STEPS.md"].replace(point, alias + "\n" + point, 1)

for name, content in merged.items():
    assert not re.search(r"^(<<<<<<<|=======|>>>>>>>)", content, re.M), name
    (ROOT / name).write_text(content)
print(json.dumps({"resolved": [{"path": n, "bytes": len(t.encode()), "sha256": hashlib.sha256(t.encode()).hexdigest()} for n, t in merged.items()]}, indent=2))
