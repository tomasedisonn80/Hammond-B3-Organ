#!/usr/bin/env python3
"""A25 audit: no checker mask imports, builds, source edits or 96-pair rerun.

Run from any cwd with Python/Pillow; stdout is a compact JSON receipt. The final
five small synthetic tests import the comparator only to test its rejection
behavior. Support and metric oracles above them are independent implementations.
"""
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import subprocess
import tempfile
from fractions import Fraction as Q
from PIL import Image, ImageChops, features, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).parent
RUN = REPORTS / 'A20-raster-run1'
digest = lambda b: hashlib.sha256(b).hexdigest()
packed = lambda obj: json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
F = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
report_raw = gzip.decompress((RUN / 'report.json.gz').read_bytes())
report = json.loads(report_raw)
mask = json.loads((RUN / 'mask.json').read_bytes())
compression = json.loads((RUN / 'compression.json').read_bytes())
assert len(report_raw) == compression['raw_bytes']
assert digest(report_raw) == compression['raw_sha256']
assert digest((RUN / 'report.json.gz').read_bytes()) == compression['compressed_sha256']
assert (RUN / 'report.json.gz').stat().st_size == compression['compressed_bytes']
assert digest((RUN / 'mask.json').read_bytes()) == report['mask']['sha256']
assert mask['identities'] == report['identities']
for name, expected in report['identities']['current_source_sha256'].items():
    assert digest((ROOT / name).read_bytes()) == expected, name
for item in report['identities']['binaries'].values():
    assert digest(Path(item['path']).read_bytes()) == item['sha256'], item['path']
assert digest((ROOT / 'tools/compare_upper_rack_material.py').read_bytes()) == report['identities']['tool']['sha256']

def panel(w, h):
    sx, sy = F(w/1672), F(h/941)
    x, y = F(72*sx), F(269*sy)
    pw, ph = F(F(600*sx)-x), F(F(508*sy)-y)
    dx, dy = F(4*sx), F(4*sy)
    return sx, sy, x, y, pw, ph, [F(x+dx), F(y+dy), F(pw-F(2*dx)), F(ph-F(2*dy))]

def center_box(b, s):
    x,y,w,h = b
    return [math.ceil(x*s-.5), math.ceil(y*s-.5), math.ceil((x+w)*s-.5), math.ceil((y+h)*s-.5)]

def sdl_box(x,y,w,h,s):
    a,b = math.trunc(F(x*s)),math.trunc(F(y*s))
    return [a,b,a+max(1,math.trunc(F(w*s))),b+max(1,math.trunc(F(h*s)))]

def mix(n):
    for shift, multiplier in ((16,0x7FEB352D),(15,0x846CA68B)):
        n = ((n ^ (n >> shift))*multiplier) % (1 << 32)
    return n ^ (n >> 16)

origins = [(78+mix(0xB3A08E11 ^ k)%516,275+mix(0xB3A08E11 ^ (k+1))%227) for k in range(0,8192,2)]
origin_sha = digest(b''.join(struct.pack('<HH', *p) for p in origins))
assert origin_sha == mask['new_origin_little_endian_uint16_sha256']
assert len(set(origins)) == 4041

def supports(w,h,s):
    sx,sy,x,y,pw,ph,inside = panel(w,h)
    rows,columns = math.floor(F(F(ph/sy)-16)),math.floor(F(F(pw/sx)-21))
    pitch = max(4,math.ceil(math.sqrt(rows*columns/(3*2048))))
    while len(range(1,rows,pitch))*len(range(1,columns,3*pitch)) > 2048:
        pitch += 1
    old = []
    for row in range(1,rows,pitch):
        for column in range(1,columns,3*pitch):
            n = (row*1973+column*9277) % (1 << 32)
            a = F(x+F(F(F(7+F(column))+F((n >> 5)%3))*sx))
            b = F(y+F(F(7+F(row))*sy))
            old += [sdl_box(a,b,sx,sy,s),sdl_box(F(a+F(3*sx)),F(b+sy),F(2*sx),sy,s)]
    new = [sdl_box(F(a*sx),F(b*sy),sx,sy,s) for a,b in origins]
    box = center_box(inside,s)
    assert all(box[0]<=a<=c<=box[2] and box[1]<=b<=d<=box[3] for a,b,c,d in old+new)
    return box,old,new,inside,rows,columns,pitch

# An independent frozen case inventory, before using the retained mask rows.
inventory = []
def old(w=1672,h=941,s=1,v=0,f=0,r=0,p=0,pr=0,ws=0,c=0):
    inventory.append(('percussion',len(inventory),w,h,s,[w,h,v,f,r,p,pr,ws,c]))
for v in range(16): old(v=v,f=v%4,r=v%4,p=v%2)
for s in (1.5,2): old(s=s,v=15,f=3,p=1)
for w,h in ((1400,820),(1920,1080)):
    for s in (1,1.5,2): old(w,h,s,9,1,1)
for w,h in ((1399,820),(1400,819)):
    for s in (1,1.5,2): old(w,h,s,6,2,2,1)
for w,h in ((960,700),(1280,900)):
    for s in (1,2): old(w,h,s,5,0,3)
for w,h in ((1672,941),(1920,1080)):
    for s in (1,1.5,2): old(w,h,s,10,3,0,1,1)
for ws in (1,2):
    for pr in (0,1):
        for s in (1,1.5,2): old(s=s,v=11,f=1,r=2,pr=pr,ws=ws)
for w,h in ((1400.25,820.75),(1672.5,941.25)): old(w,h,1.5,14,2)
for s in (1,1.5,2):
    for c in (1,2): old(s=s,v=13,p=1,c=c)
for h in (933.25,933.5):
    for s in (1,1.5,2): old(h=h,s=s,v=3,f=2,r=3,p=1)
upper_states = [(0,'B',False,False),(4,'A',True,True),(8,'D',False,True),
                (4,'Cancel',True,False),(8,'B',False,False),(0,'A',True,True),
                (8,'D',True,True),(0,'Cancel',False,False),(4,'B',True,False)]
for n in range(30):
    w,h = ((1672,941),(1400,820),(1920,1080))[n//3] if n<9 else ((8192,8192) if 24<=n<27 else (1672,941))
    s = (1,1.5,2)[n%3] if n<27 else 1
    state = upper_states[n] if n<9 else ((0,'B',False,False) if n==27 else (8,'D',True,True) if n==29 else (4,'B',False,True))
    inventory.append(('upper',n,w,h,s,state))
assert len(inventory) == len(mask['cases']) == len(report['cases']) == 96

def intersect(a,b):
    x,y = max(a[0],b[0]),max(a[1],b[1])
    return [x,y,max(x,min(a[2],b[2])),max(y,min(a[3],b[3]))]
area = lambda b: (b[2]-b[0])*(b[3]-b[1])
rows_digest = []
for expected,m,r in zip(inventory,mask['cases'],report['cases'],strict=True):
    suite,n,w,h,s,state = expected
    assert (suite,n) == (m['suite'],m['case']) == (r['suite'],r['case'])
    assert m['logical_size'] == [w,h] and m['scale'] == [s,s]
    box,old_boxes,new_boxes,inside,nrows,ncols,pitch = supports(w,h,s)
    L,T,R,B = box
    vw,vh = math.ceil(F(w*s)),math.ceil(F(h*s))
    clip,enabled,origin,resource = [0,0,0,0],False,[0,0],False
    if suite=='percussion':
        assert m['fixture'] == state
        active = state[6]==state[7]==0 and w>=1400 and h>=820
        c=state[8]
        if c:
            enabled,origin = True,[7,7]
            clip = [math.trunc(F(z*s)) for z in (180,138,275,77)] if c==1 else [math.floor(z*s) for z in (161,174,252,41)]
    else:
        assert tuple(m[k] for k in ('level','route','pending','held')) == state
        active=True
        origin = [0,0] if n>=27 or (9<=n<=20 and s==1.5) else [13,17]
        if 9<=n<=20:
            enabled=True
            edge=(n-9)//3
            physical = [[L-2,T-2,4,B-T+4],[R-2,T-2,4,B-T+4],[L-2,T-2,R-L+4,4],[L-2,B-2,R-L+4,4]]
            logical = [[74,300,4,160],[594,300,4,160],[90,271,490,4],[90,502,490,4]]
            clip = [math.floor(z*s) for z in logical[edge]] if s==1.5 else physical[edge]
        if n in (21,22,23):
            enabled=True
            clip = [R+4,T+4,8,8] if n==21 else [L,T,0,0] if n==22 else [152,546,0,0]
        if 24<=n<=26: origin,resource=[-L,-T],True
        assert m['blend']==(0 if n==23 else 1)
    width,height = (64,64) if resource else (vw+2*origin[0],vh+2*origin[1])
    ox,oy=origin
    visible=intersect([0,0,width,height],[ox,oy,ox+vw,oy+vh])
    if enabled: visible=intersect(visible,[ox+clip[0],oy+clip[1],ox+clip[0]+clip[2],oy+clip[1]+clip[3]])
    allow=intersect([ox+L-1,oy+T-1,ox+R+1,oy+B+1],visible) if active else [0,0,0,0]
    assert m['output_size']==[width,height] and m['viewport']==[ox,oy,vw,vh]
    assert m['clip']==clip and m['clip_enabled']==enabled and m['active']==active and m['resource_crop']==resource
    assert m['visible_device_box']==visible and m['allowance_box']==allow
    for k,v in {'compared_pixels':width*height,'allowed_pixels':area(allow),'protected_pixels':width*height-area(allow),
                'intrinsic_pixels':area(box) if active else 0,'expanded_intrinsic_pixels':(R-L+2)*(B-T+2) if active else 0}.items():
        assert m[k]==r[k]==v,(suite,n,k)
    assert m['whole_frame_equality_required']==r['whole_frame_equality_required']==(area(allow)==0)
    if active:
        p=m['support']
        assert p['gradient_viewport_relative_box']==box and p['inset_binary32']==inside
        assert p['old_rows']==nrows and p['old_columns']==ncols and p['old_step']==pitch
        assert p['old_pairs']==len(old_boxes)//2
        assert p['old_ordered_fill_boxes_sha256']==digest(packed(old_boxes))
        assert p['new_ordered_fill_boxes_sha256']==digest(packed(new_boxes))
    assert len(r['per_row_different_pixels'])==height and len(r['per_row_outside_allowance_pixels'])==height
    assert sum(r['per_row_different_pixels'])==r['different_pixels']
    assert sum(r['per_row_outside_allowance_pixels'])==r['outside_allowance_pixels']==0
    assert sum(r['outside_allowance_channels_by_rgba'])==r['outside_allowance_channels']==0
    assert sum(r['different_channels_by_rgba'])==r['different_channels']
    assert all(0<=count<=width for count in r['per_row_different_pixels'])
    assert r['whole_frame_equal']==(r['before_rgba_sha256']==r['after_rgba_sha256'])==(r['different_pixels']==0)
    assert r['all_metadata_exact'] and r['before_metadata_sha256']==r['after_metadata_sha256'] and not any(r['metadata_errors'].values())
    assert r['passed'] and (r['different_pixels']>0 if area(allow) else r['different_pixels']==0)
    rows_digest.append([suite,n,box if active else None,visible,allow,width*height-area(allow)])

totals=report['totals']
for k in ('compared_pixels','protected_pixels','different_pixels','different_channels','outside_allowance_pixels','outside_allowance_channels'):
    assert sum(c[k] for c in report['cases'])==totals[k]
ordinary=[c for c in report['cases'] if c['allowed_pixels'] and not c['resource_crop'] and not c['clip_enabled']]
assert min(c['protected_pixels'] for c in ordinary)==1059289
assert min(c['protected_pixels'] for c in report['cases'] if c['allowed_pixels'])==0
assert sum(c['whole_frame_equal'] for c in report['cases'])==37
children=[c['children'] for c in report['cases'] if c['children']['applicable']]
probes=[p for c in children for p in c['probes']]
assert len(children)==12 and len(probes)==216 and sum(p['pixels'] for p in probes)==121526
assert min(p['pixels'] for p in probes)==111
assert all(p['opaque'] and p['different_pixels']==p['different_channels']==p['maximum_channel_delta']==0 for p in probes)
assert sum(c['focus']['after_pixels'] for c in children)==21864
assert all(c['focus']['before_mask_sha256']==c['focus']['after_mask_sha256'] and c['focus']['differing_positions']==0 for c in children)

def solve(matrix,rhs):
    a=[[Q(z) for z in row]+[Q(v)] for row,v in zip(matrix,rhs,strict=True)]
    for i in range(3):
        divisor=a[i][i]
        a[i]=[z/divisor for z in a[i]]
        for j in range(3):
            if i!=j:
                multiplier=a[j][i]
                a[j]=[x-multiplier*y for x,y in zip(a[j],a[i],strict=True)]
    return [row[-1] for row in a]

def statistics(image):
    result={}
    for name,(left,top,w,h) in {'left':(88,320,18,128),'right':(572,320,14,128)}.items():
        pts=[(x,y,2126*r+7152*g+722*b) for y in range(h) for x in range(w) for r,g,b in [image.getpixel((left+x,top+y))[:3]]]
        n=w*h; sx=sum(x for x,y,z in pts); sy=sum(y for x,y,z in pts)
        xx=sum(x*x for x,y,z in pts); xy=sum(x*y for x,y,z in pts); yy=sum(y*y for x,y,z in pts)
        rhs=[sum(z for x,y,z in pts),sum(x*z for x,y,z in pts),sum(y*z for x,y,z in pts)]
        zz=sum(z*z for x,y,z in pts)
        beta=solve([[n,sx,sy],[sx,xx,xy],[sy,xy,yy]],rhs)
        sse=(zz-sum(a*b for a,b in zip(beta,rhs,strict=True)))/100000000
        result[name]={'mean_exact':str(Q(rhs[0],10000*n)),'mean':float(Q(rhs[0],10000*n)),
                      'residual_sse_exact':str(sse),'residual_rms':math.sqrt(float(sse/n)),
                      'sum_L':rhs[0],'sum_L2':zz,'sum_LX':2*rhs[1]-(w-1)*rhs[0],
                      'sum_LY':2*rhs[2]-(h-1)*rhs[0],
                      'sum_X2':sum((2*x-w+1)**2 for x,y,z in pts),'sum_Y2':sum((2*y-h+1)**2 for x,y,z in pts)}
    return result

ref=Image.open(ROOT/'docs/design/atlas-cover-reference.jpg').convert('RGB')
assert digest(ref.tobytes())==report['reference_statistics']['rgb_sha256']
reference=statistics(ref)
for side,s in reference.items():
    for k,v in s.items(): assert report['reference_statistics']['patches'][side][k]==v,(side,k)

def screens(actual):
    errors=[]
    for side in ('left','right'):
        errors.extend([abs(float(Q(actual[side]['mean_exact'])-Q(reference[side]['mean_exact']))),abs(actual[side]['residual_rms']-reference[side]['residual_rms'])])
    errors.append(abs(float(Q(actual['right']['mean_exact'])-Q(actual['left']['mean_exact'])-Q(reference['right']['mean_exact'])+Q(reference['left']['mean_exact']))))
    return {'absolute_errors':errors,'passed':[e<=t for e,t in zip(errors,(2,.4,2,.4,1.5),strict=True)]}

sampled=[]; metrics={}
for suite,n in [('percussion',24),('percussion',52),('upper',3),('upper',10),('upper',23),('upper',26),('upper',27),('upper',28),('upper',29)]:
    record=next(c for c in report['cases'] if c['suite']==suite and c['case']==n)
    images=[]; headers=[]
    for side in ('before','after'):
        executable=report['identities']['binaries'][side+'_'+suite]['path']
        run=subprocess.run([executable,'--case',str(n)],capture_output=True,timeout=45,check=True)
        assert not run.stderr
        header,pixels=run.stdout.split(b'\n',1)
        obj=json.loads(header)
        assert len(pixels)==obj['bytes']==obj['width']*obj['height']*4
        assert digest(header)==record[side+'_header_bytes_sha256'] and digest(pixels)==record[side+'_rgba_sha256']
        headers.append(obj)
        images.append(Image.frombytes('RGBA',(obj['width'],obj['height']),pixels))
        if suite=='upper' and n>=27:
            current=statistics(images[-1])
            metrics[str(n)+'_'+side]={'patches':current,'screens':screens(current)}
            assert all(screens(current)['passed']) if side=='after' else not any(screens(current)['passed'])
            if n==28:
                for patch in current:
                    for k,v in current[patch].items(): assert record[side+'_statistics']['patches'][patch][k]==v
    assert headers[0]==headers[1]
    channels=ImageChops.difference(*images).split()
    count=sum(sum(ch.histogram()[1:]) for ch in channels)
    assert count==record['different_channels']
    sampled.append([suite,n,record['before_rgba_sha256'],record['after_rgba_sha256'],count])
assert metrics['27_after']['patches']==metrics['28_after']['patches']==metrics['29_after']['patches']

# Verify every retained synthetic lossless artifact independently, bytewise.
synthetic=json.loads((REPORTS/'A20-synthetic-rejections/selfcheck.json').read_bytes())
artifact_count=0
for check in synthetic['checks']:
    artifacts=check['artifacts']
    for item in artifacts.values():
        b=Path(item['path']).read_bytes(); assert digest(b)==item['sha256'] and len(b)==item['bytes']; artifact_count+=1
    if not artifacts: continue
    before=Image.open(artifacts['before']['path']).tobytes()
    after=Image.open(artifacts['after']['path']).tobytes()
    delta=bytes(abs(a-b) for a,b in zip(before,after,strict=True))
    assert delta==Image.open(artifacts['absolute-rgba-difference']['path']).tobytes()
    maximum=bytes(max(delta[i:i+4]) for i in range(0,len(delta),4))
    assert maximum==Image.open(artifacts['maximum-channel-difference']['path']).tobytes()
    outside=Image.open(artifacts['outside-allowance-mask']['path']).tobytes()
    if 'outside_allowance_pixels' in check['observed']: assert outside.count(255)==check['observed']['outside_allowance_pixels']
assert artifact_count==21

# A tiny positive control plus four rejection paths, not native fixture credit.
specification=importlib.util.spec_from_file_location('a25_comparator_under_test',ROOT/'tools/compare_upper_rack_material.py')
checker=importlib.util.module_from_spec(specification); specification.loader.exec_module(checker)
tiny={'suite':'percussion','case':99,'logical_size':[16,16],'scale':[1,1],'output_size':[16,16],
      'active':True,'resource_crop':False,'clip_enabled':False,'compared_pixels':256,'intrinsic_pixels':36,
      'expanded_intrinsic_pixels':64,'visible_intrinsic_pixels':36,'allowed_pixels':64,'protected_pixels':192,
      'whole_frame_equality_required':False,'allowance_box':[4,4,12,12],'fixture':[16,16,0,0,0,0,0,0,0],'offset':0}
header={'schema':1,'case':99,'width':16,'height':16,'bytes':1024,'fixture':tiny['fixture'],'scale':1,'offset':0,'active':True}
before=bytes([12,23,34,255])*256
inside=bytearray(before); inside[(6*16+6)*4]+=1
alpha=bytearray(inside); alpha[3]-=1
faults=[]
with tempfile.TemporaryDirectory(prefix='A25-fault-',dir=REPORTS) as temporary:
    for name,new,changed,empty,expected in [('inside_rgb',inside,False,False,True),('outside_alpha',alpha,False,False,False),
            ('changed_header',inside,True,False,False),('active_no_change',before,False,False,False),('empty_allowance',inside,False,True,False)]:
        s=dict(tiny); h=dict(header)
        if changed: h['extra_metadata']=True
        if empty: s.update(allowed_pixels=0,protected_pixels=256,allowance_box=[0,0,0,0],whole_frame_equality_required=True)
        out=Path(temporary)/name; out.mkdir()
        result=checker.compare_case(s,(header,before,digest(packed(header))),(h,bytes(new),digest(packed(h))),{},out)
        assert result['passed']==expected
        if name=='outside_alpha': assert result['outside_allowance_pixels']==result['outside_allowance_channels']==1
        faults.append({'name':name,'passed':result['passed'],'expected':expected,'outside_pixels':result['outside_allowance_pixels']})

print(json.dumps({'schema':1,'audit':'A25 independent comparison admission','script_sha256':digest(Path(__file__).read_bytes()),
    'report_raw_sha256':digest(report_raw),'report_gzip_sha256':compression['compressed_sha256'],
    'mask_sha256':report['mask']['sha256'],'tool_sha256':report['identities']['tool']['sha256'],
    'painter_sha256':report['identities']['current_source_sha256']['apps/standalone/InstrumentView.cpp'],
    'independent_mask_rows_sha256':digest(packed(rows_digest)),'all_96_supports_and_report_rows_checked':True,
    'grain_origin_sha256':origin_sha,'counts':totals,'native_sample_count':len(sampled),'native_samples':sampled,
    'reference_rgb_sha256':digest(ref.tobytes()),'decoder':{'Pillow':pillow_version,'JPEG_API':features.version_codec('jpg'),'libjpeg_turbo':features.version_feature('libjpeg_turbo')},
    'reference_statistics':reference,'supplemental_27_28_29_statistics_equal':True,
    'candidate_statistics':metrics['28_after'],'baseline_statistics':metrics['28_before'],
    'synthetic_artifacts_verified':artifact_count,'comparator_controls':faults,
    'build_ninja_current_matches_report':digest(Path(report['identities']['build_inputs']['build.ninja']['path']).read_bytes())==report['identities']['build_inputs']['build.ninja']['sha256'],
    'limits':'Nine pairs independently resampled, not 96 pairs rerun. All-source support and retained per-case rows checked. Four rejection paths plus one positive control. Resource crops protect zero output pixels. Opaque interiors are partial probes. No full-frame visual, deadline, native display, accessibility, physical fidelity or whole-interface 1:1 admission.'},indent=2))
