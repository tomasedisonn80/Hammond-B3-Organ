from pathlib import Path
import hashlib,json,os,py_compile,shutil,subprocess,sys,time
repo=Path('/workspace/scratch/a472c29da8b3/Hammond-B3-Organ');base=Path('/tmp/hammond-preset-a32')
source=base/'final-source';build=base/'final-build'
paths=['tools/compile_fixed_registrations.py','tools/compile_chapel_presets.py','cmake/CompileFixedRegistrations.cmake','data/chapel-presets.schema.json','data/registrations/atlas-chapel-nominal-v1.json','data/registrations/review-a-chapel.csv','data/registrations/review-b-chapel.csv']
source.mkdir(exist_ok=True)
for rel in paths:
 dst=source/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(repo/rel,dst)
(source/'CMakeLists.txt').write_text('cmake_minimum_required(VERSION 3.22)\nproject(PresetDataBoundary NONE)\nset(Python3_EXECUTABLE "'+sys.executable+'")\nset(HAMMOND_GENERATED_INCLUDE_DIR "${CMAKE_BINARY_DIR}/generated")\nadd_custom_target(hammond_core COMMAND "${CMAKE_COMMAND}" -E touch "${CMAKE_BINARY_DIR}/consumer-ran")\ninclude(cmake/CompileFixedRegistrations.cmake)\n')
cmake='/workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake';records=[]
header=build/'generated/hammond/generated/FixedRegistrationData.h';consumer=build/'consumer-ran'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,args=None,expected=0):
 command=args or [cmake,'--build',str(build),'--target','hammond_core']
 p=subprocess.run(command,capture_output=True,text=True,timeout=30)
 log=base/(name+'.txt');log.write_text(p.stdout+p.stderr)
 records.append({'case':name,'command':command,'exit':p.returncode,'log':log.name,'sha256':sha(log)})
 assert (p.returncode==0)==(expected==0),(name,p.returncode,p.stdout,p.stderr)
 return p
run('final-configure',[cmake,'-S',str(source),'-B',str(build),'-G','Unix Makefiles'])
run('final-clean');raw=header.read_bytes();header_sha=sha(header);assert header_sha=='66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6'
stamp=header.stat().st_mtime_ns;run('final-no-change');assert header.stat().st_mtime_ns==stamp
original={rel:(source/rel).read_bytes() for rel in paths}
def dirty():
 os.utime(header,ns=(1_600_000_000_000_000_000,1_600_000_000_000_000_000));consumer.unlink(missing_ok=True)
def rejected(name):
 dirty();run(name,expected=1);assert not consumer.exists();assert header.read_bytes()==raw
 assert not list(header.parent.glob('.chapel-catalog-*.tmp'))
def restored(name):
 run(name);assert consumer.exists() and header.read_bytes()==raw
for index,rel in enumerate(paths[4:]):
 p=source/rel;p.write_bytes(original[rel]+b'\n');rejected(f'input-{index}-mutated');p.write_bytes(original[rel]);restored(f'input-{index}-restored')
 p.unlink();rejected(f'input-{index}-missing');p.write_bytes(original[rel]);restored(f'input-{index}-recreated')
review_a=source/paths[5];review_b=source/paths[6];review_b.unlink();os.link(review_a,review_b)
rejected('review-hardlink-alias');review_b.unlink();review_b.write_bytes(original[paths[6]]);restored('review-distinct-restored')
for index,rel in enumerate(paths[:2]+paths[3:]):
 p=source/rel
 if rel.endswith('.py') or rel.endswith('.json') and 'schema' in rel:
  p.write_bytes(original[rel]+(b'\n# dependency-only change\n' if rel.endswith('.py') else b'\n'))
 else:
  p.write_bytes(original[rel])
 dirty();before=header.stat().st_mtime_ns;process=run(f'dependency-{index}')
 assert header.stat().st_mtime_ns!=before and header.read_bytes()==raw
 assert 'Admitting both chapel readings' in process.stdout
 p.write_bytes(original[rel])
# Repeat the demonstrated same-size/same-second dependency edit with an old cache.
helper=source/'tools/compile_chapel_presets.py';second=int(time.time())-120
old_ns=second*1_000_000_000+250_000_000;new_ns=second*1_000_000_000+750_000_000
helper.write_bytes(original['tools/compile_chapel_presets.py']);os.utime(helper,ns=(old_ns,old_ns))
cache=source/'tools/__pycache__'/f'compile_chapel_presets.{sys.implementation.cache_tag}.pyc';cache.parent.mkdir(exist_ok=True)
py_compile.compile(str(helper),cfile=str(cache),doraise=True,optimize=0,invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
cache_sha=sha(cache);changed=original['tools/compile_chapel_presets.py'].replace(b'"427866244",',b'"427866243",',1)
helper.write_bytes(changed);os.utime(helper,ns=(new_ns,new_ns));rejected('fixed-stale-cache-rejected');assert sha(cache)==cache_sha
helper.write_bytes(original['tools/compile_chapel_presets.py']);restored('fixed-source-restored')
assert header.read_bytes()==raw
reference=Path('/tmp/hammond-preset-a31/build/generated/hammond/generated/FixedRegistrationData.h')
assert reference.read_bytes()==raw
inputs={rel:{'sha256':hashlib.sha256(original[rel]).hexdigest(),'bytes':len(original[rel])} for rel in paths}
manifest=base/'source-inputs.json';manifest.write_text(json.dumps(inputs,sort_keys=True,indent=2)+'\n')
result={'scope':'Isolated actual CMake custom-command and dependency boundary; no C++ consumer compilation','context_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'source_inputs':inputs,'input_manifest_sha256':sha(manifest),'cmake':subprocess.check_output([cmake,'--version'],text=True).splitlines()[0],'python':sys.version.split()[0],'generator':'Unix Makefiles','records':records,'commands':len(records),'expected_rejections':sum(x['exit']!=0 for x in records),'header_sha256':header_sha,'header_bytes':len(raw),'a31_header_equal':True,'a31_header_sha256':sha(reference),'consumer_blocked_on_every_rejection':True,'old_header_preserved_on_every_rejection':True,'temporary_outputs_clean':True,'valid_output_unchanged':True,'original_repository_inputs_unchanged':all((repo/rel).read_bytes()==original[rel] for rel in paths)}
(base/'boundary-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('records','source_inputs')},indent=2))
