"""Retain already-requested read-only CI evidence; never execute app/tests or retry CI."""
import gzip
import hashlib
import json
import pathlib
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent
SOURCE = "523c1979334b0fbb624ce120128a0b8ada078383"
RUN = 44043394005


def digest(data):
    return hashlib.sha256(data).hexdigest()


for pending in sorted(BASE.glob("pending-job-*.json")):
    envelope_bytes = pending.read_bytes()
    envelope = json.loads(envelope_bytes)
    job = envelope["job"]
    job_id = job["id"]
    assert envelope["source_sha"] == job["head_sha"] == SOURCE
    assert job["run_id"] == RUN and job["run_attempt"] == 1
    assert job["status"] == "completed"
    raw = envelope["decoded_log"].encode("utf-8")
    compressed = gzip.compress(raw, mtime=0)
    log_path = BASE / f"job-{job_id}.log.gz"
    connector_path = BASE / f"job-{job_id}.connector.json.gz"
    review_path = BASE / f"job-{job_id}-review.json"
    assert not log_path.exists() and not connector_path.exists() and not review_path.exists()
    log_path.write_bytes(compressed)
    connector_path.write_bytes(gzip.compress(envelope_bytes, mtime=0))
    review = {
        "source_sha": SOURCE,
        "job": job,
        "observed_utc": envelope["observed_utc"],
        "status": "TERMINAL_RAW_LOG_RETAINED_PENDING_ARTIFACT_REVIEW",
        "log": {
            "path": log_path.name,
            "decoded_utf8_bytes": len(raw),
            "decoded_sha256": digest(raw),
            "compressed_bytes": len(compressed),
            "compressed_sha256": digest(compressed),
            "retention": "Lossless gzip of complete decoded connector UTF-8 stream; no clipping or line normalization",
        },
    }
    review_path.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n")
    pending.unlink()
    print(json.dumps({"job_log_retained": job_id, "conclusion": job["conclusion"], "log": review["log"]}))

for pending in sorted(BASE.glob("pending-artifact-*.json")):
    item = json.loads(pending.read_text())
    metadata = item["metadata"]
    assert metadata["workflow_run"]["head_sha"] == SOURCE and metadata["workflow_run"]["id"] == RUN
    url = item["response"]["value"]["structuredContent"]["file_uri"]["download_url"]
    destination = BASE / f"artifact-{metadata['id']}.zip"
    assert not destination.exists()
    with urllib.request.urlopen(url, timeout=30) as response:
        archive = response.read(5000001)
    assert len(archive) == metadata["size_in_bytes"] < 5000000
    assert "sha256:" + digest(archive) == metadata["digest"]
    destination.write_bytes(archive)
    pending.unlink()
    print(json.dumps({"artifact_retained": metadata["id"], "bytes": len(archive), "sha256": digest(archive)}))

for pending in sorted(BASE.glob("pending-observation-*.json")):
    destination = BASE / (pending.name.removeprefix("pending-") + ".gz")
    assert not destination.exists()
    destination.write_bytes(gzip.compress(pending.read_bytes(), mtime=0))
    pending.unlink()
