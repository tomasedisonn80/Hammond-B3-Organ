#!/usr/bin/env python3
"""Independent binary32/source-metric admission; does not render or import painter."""
from pathlib import Path
import hashlib,json,re,struct
ROOT=Path(__file__).resolve().parents[4]
REPORT=Path(__file__).with_suffix('.json')
def f(x): return struct.unpack('f',struct.pack('f',x))[0]
def add(a,b): return f(a+b)
def sub(a,b): return f(a-b)
def mul(a,b): return f(a*b)
def div(a,b): return f(a/b)
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
font=(ROOT/'apps/standalone/FontData.h').read_text()
section=font.split('kSerifGlyphs{{',1)[1].split('}};',1)[0]
glyphs={int(m[7]):tuple(map(int,m[:7])) for m in re.findall(r'\{(\d+), (\d+), (\d+), (\d+), (-?\d+), (-?\d+), (\d+)\}, // ASCII (\d+)',section)}
assert len(glyphs)==95
labels=["16'","5 1/3'","8'","4'","2 2/3'","2'","1 3/5'","1 1/3'","1'"]
centers=[[158,206,254,302,351,400,449,498,548],[685,734,782,830,878,927,975,1024,1074]]
def width(text,size):
    scale=div(size,40); result=0.
    for ch in text: result=add(result,div(mul(glyphs[ord(ch)][6],scale),64))
    return result
def quad_run(text,x,top,size):
    scale=div(size,40); baseline=add(top,mul(38,scale)); out=[]
    for ch in text:
        ax,ay,w,h,bx,by,adv=glyphs[ord(ch)]
        if w and h:
            px=2 if mul(w,scale)<1 else 0;py=2 if mul(h,scale)<1 else 0
            gx=add(x,mul(bx-px,scale));gy=add(baseline,mul(by-py,scale))
            out.append(dict(character=ch,quad=[gx,gy,mul(w+2*px,scale),mul(h+2*py,scale)],baseline=baseline))
        x=add(x,div(mul(adv,scale),64))
    return out
records=[]; failures=[]; maximum_baseline_recomposition_error=0.
for w,h in [(1672,941),(1400,820),(1920,1080),(1920,820),(1400,1080),(1672.5,941.25),(8192,8192)]:
    sx=div(w,1672);sy=div(h,941);fs=min(sx,sy)
    for manual in range(2):
        for index,label in enumerate(labels):
            x=mul(centers[manual][index]-23,sx);y=mul(467,sy)
            bw=sub(mul(centers[manual][index]+23,sx),x);bh=sub(mul(490,sy),y)
            size=min(mul(19,fs),div(bh,f(1.2)))
            original_width=width(label,size)
            available=sub(bw,mul(2,mul(2,sx)))
            if original_width>available: size=mul(size,div(max(f(.1),available),original_width))
            old_x=add(x,div(sub(bw,width(label,size)),2))
            old_top=add(y,div(sub(bh,mul(size,f(1.2))),2))
            old=quad_run(label,old_x,old_top,size)
            runs=[(label,20.5,21.5)] if len(label)!=6 else [(label[0],20.5,21.5),(label[2],13,15.5),(label[3],16,19.5),(label[4],13,21.5),(label[5],20.5,21.5)]
            widths=[width(t,mul(s,fs)) for t,s,b in runs]
            total=0.
            for i,advance in enumerate(widths):
                total=add(total,advance)
                if len(runs)==5 and i in(0,3): total=add(total,mul(f(.5),sx))
            cursor=add(x,div(sub(bw,total),2));new=[]
            for i,(text,nominal,offset) in enumerate(runs):
                requested=add(y,mul(offset,sy));run_size=mul(nominal,fs)
                top=sub(requested,div(mul(38,run_size),40))
                out=quad_run(text,cursor,top,run_size);new+=out
                maximum_baseline_recomposition_error=max(maximum_baseline_recomposition_error,max(abs(q['baseline']-requested) for q in out))
                cursor=add(cursor,widths[i])
                if len(runs)==5 and i in(0,3): cursor=add(cursor,mul(f(.5),sx))
            assert len(new)==len(label.replace(' ',''))
            checks=dict(padded_width=total<=sub(bw,mul(4,sx)),glyph_inside_label=all(q['quad'][0]>=x and q['quad'][1]>=y and add(q['quad'][0],q['quad'][2])<=add(x,bw) and add(q['quad'][1],q['quad'][3])<add(y,bh) for q in new),above_value_row=all(add(q['quad'][1],q['quad'][3])<mul(491,sy) for q in new))
            if not all(checks.values()): failures.append([w,h,manual,index,checks])
            records.append(dict(logical_size=[w,h],manual=manual,index=index,label=label,scales=[sx,sy,fs],box=[x,y,bw,bh],old_size=size,old_baseline=old[0]['baseline'],new_total_advance=total,new_runs=len(runs),old_glyphs=old,new_glyphs=new,checks=checks))
assert not failures,failures
canonical=[r for r in records if r['logical_size']==[1672,941] and r['manual']==0]
assert sum(r['new_runs'] for r in canonical)*2==50
assert sum(len(r['new_glyphs']) for r in canonical)*2==62
assert width("16'",f(20.5))==f(31.2625)
paths=['apps/standalone/FontData.h','apps/standalone/Drawing.cpp','apps/standalone/UiModel.h','apps/standalone/UiModel.cpp','apps/standalone/InstrumentView.cpp','apps/standalone/native_tests/test_standalone_lower_rack_material_raster.cpp','apps/standalone/native_tests/test_standalone_footage_typography_raster.cpp','docs/design/atlas-cover-reference.jpg']
report=dict(schema='footage-typography-admission-audit-v1',status='passed',scope='independent source/binary32 geometry only; no compiled fixture or raster/readability acceptance',source_hashes={p:sha(p) for p in paths},labels=labels,atlas={'height':40,'ascent':38,'digits_advance':25,'slash_advance':13,'apostrophe_advance':11},label_records=len(records),checks=len(records)*3,failures=failures,text_calls=50,nonempty_glyph_copies=62,maximum_baseline_recomposition_error=maximum_baseline_recomposition_error,records=records)
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','label_records','checks','text_calls','nonempty_glyph_copies','maximum_baseline_recomposition_error']}))
