from pathlib import Path
import subprocess, time, json, hashlib, datetime, os, sys, platform
root=Path("/workspace/scratch/ade21b726509/Hammond-B3-Organ")
reports=root/"docs/development/2026-11-15-execution-continuation/reports"
package=root.parent/"contact-reference-relocated-v2/share/hammond-b3-organ/contact-reference"
neutral=root.parent/"contact-reference-neutral-v2"
output=reports/"contact-study-v1-qualified.json"
receipt=reports/"contact-study-v1-qualified-process.json"
review=reports/"A30-study-review.json"
expected="eb4d374cc46ed1c16448ab3b1c2f03c5714a27c20bfdd0c3dba6e005d8f8066e"
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if output.exists() or receipt.exists(): raise SystemExit("fresh qualified experiment paths required")
if not review.is_file(): raise SystemExit("independent review receipt required")
if h(package/"tools/contact_switching_study.py")!=expected or h(root/"tools/contact_switching_study.py")!=expected: raise SystemExit("runner source mismatch")
command=[sys.executable,"-B",str(package/"tools/contact_switching_study.py"),"--fixtures",str(package/"data/contact-switching/reference-v1"),"--output",str(output)]
started=datetime.datetime.now(datetime.timezone.utc).isoformat();begin=time.monotonic();timed_out=False
with (root.parent/"wave6-qualified-study.stdout").open("wb") as so,(root.parent/"wave6-qualified-study.stderr").open("wb") as se:
    child=subprocess.Popen(command,cwd=neutral,stdout=so,stderr=se)
    while True:
        pid,status,usage=os.wait4(child.pid,os.WNOHANG)
        if pid==child.pid: break
        if time.monotonic()-begin>305:
            child.kill();pid,status,usage=os.wait4(child.pid,0);timed_out=True;break
        time.sleep(0.05)
    child.returncode=os.waitstatus_to_exitcode(status)
elapsed=time.monotonic()-begin
peak=int(usage.ru_maxrss)*(1024 if platform.system()=="Linux" else 1)
report=json.loads(output.read_text()) if output.is_file() else None
passed=(not timed_out and child.returncode==0 and elapsed<=300 and 0<peak<=268435456 and report is not None and report["status"]=="passed")
record={"schema_version":1,"status":"passed" if passed else "incomplete_or_failed","command":command,"cwd":str(neutral),"source_package_manifest":"contact-package-v2.json","independent_review_sha256":h(review),"started_at_utc":started,"finished_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"external_process_wall_seconds":elapsed,"wall_limit_seconds":300,"external_child_peak_resident_bytes":peak,"peak_limit_bytes":268435456,"peak_measurement":"os.wait4(exact_child_pid) terminal ru_maxrss; Linux KiB converted to bytes; no aggregate earlier-child maximum","exit_code":child.returncode,"timed_out":timed_out,"report_exists":output.is_file(),"report_bytes":output.stat().st_size if output.is_file() else None,"report_sha256":h(output) if output.is_file() else None,"runner_sha256":expected,"meaning":"Final admitted runtime code executed from the moved installed48-file package in a neutral working directory. External wall includes Python startup and report publication; exact-child terminal RSS includes final encoding/publication. Overall pass also requires complete internal numerical and resource gates."}
receipt.write_text(json.dumps(record,indent=2)+"\n");print(json.dumps(record))
raise SystemExit(0 if passed else 2)
