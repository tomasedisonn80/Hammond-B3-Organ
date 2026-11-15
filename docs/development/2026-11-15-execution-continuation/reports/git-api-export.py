import base64, hashlib, json, subprocess, sys

def git(*args):
    return subprocess.check_output(["git", *args])

if sys.argv[1] == "manifest":
    entries=[]
    parts=git("diff", "--cached", "--raw", "--no-abbrev", "-z").split(b"\0")
    i=0
    while i < len(parts) and parts[i]:
        meta=parts[i].decode().split(); path=parts[i+1].decode(); i+=2
        oldmode,newmode,oldsha,newsha,status=meta
        if status.startswith(("R","C")): raise SystemExit("Export requires explicit non-rename paths")
        entries.append({"path":path,"mode":newmode if newmode!="000000" else "100644","type":"blob","sha":None if newsha=="0"*40 else newsha,"size":0 if newsha=="0"*40 else int(git("cat-file","-s",newsha))})
    print(json.dumps({"parent":git("rev-parse","HEAD").decode().strip(),"base_tree":git("rev-parse","HEAD^{tree}").decode().strip(),"tree":git("write-tree").decode().strip(),"entries":entries}))
elif sys.argv[1] == "chunk":
    sha=sys.argv[2]; start=int(sys.argv[3]); size=int(sys.argv[4])
    if len(sha)!=40 or any(c not in "0123456789abcdef" for c in sha): raise SystemExit("invalid object")
    b=git("cat-file","blob",sha)
    if hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()!=sha: raise SystemExit("object mismatch")
    print(base64.b64encode(b[start:start+size]).decode())
else: raise SystemExit("unknown operation")
