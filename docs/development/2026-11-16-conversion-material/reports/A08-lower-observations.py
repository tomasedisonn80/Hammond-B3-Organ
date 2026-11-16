#!/usr/bin/env python3
"""Lower-material authoring observations; no native build, paint or grading.

Reads unchanged source/reference and root's actual baseline; writes this author's
receipt only. Exact sufficient statistics describe encoded RGB, not physical
luminance or material roughness. No candidate modules or prior report helpers.
"""
from __future__ import annotations
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import platform
import struct
import sys
from PIL import Image, features, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PATCHES = {
    "left": (612,320,18,128), "right": (1094,320,14,128),
    "left_top": (612,298,18,14), "right_top": (1094,298,14,14),
    "center_top": (800,302,112,6),
    "left_bottom": (612,460,18,20), "right_bottom": (1094,460,14,20),
    "bottom_interior_left": (704,492,12,8),
    "bottom_interior_middle": (852,492,14,8),
    "bottom_interior_right": (1047,492,12,8),
}
PRIMARY = tuple(PATCHES)[:7]
WEIGHTS = (2126,7152,722)


def identity(path):
    data=path.read_bytes()
    try: name=path.relative_to(ROOT).as_posix()
    except ValueError: name=str(path.resolve())
    return {"path":name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}


def rational(q):
    return {"numerator":str(q.numerator),"denominator":str(q.denominator),"value":float(q)}


def patch(image, box, channel=None):
    x,y,w,h=box
    denominator=10000 if channel is None else 1
    total=squares=xcross=ycross=0
    for yy in range(h):
        for xx in range(w):
            rgb=image.getpixel((x+xx,y+yy))
            z=sum(a*b for a,b in zip(rgb,WEIGHTS)) if channel is None else rgb[channel]
            total+=z; squares+=z*z
            xcross+=(2*xx-w+1)*z; ycross+=(2*yy-h+1)*z
    n=w*h; sx2=F(h*w*(w*w-1),12); sy2=F(w*h*(h*h-1),12)
    mean=F(total,n*denominator)
    bx=F(xcross,2*denominator)/sx2; by=F(ycross,2*denominator)/sy2
    sse=F(squares,denominator**2)-n*mean*mean-bx*bx*sx2-by*by*sy2
    return {"mean":rational(mean),"slope_x":rational(bx),"slope_y":rational(by),
            "residual_sse":rational(sse),"residual_population_rms":math.sqrt(float(sse/n)),
            "sufficient_statistics":{"n":n,"sum":total,"sum_squares":squares,
                "twice_centered_x_sum":xcross,"twice_centered_y_sum":ycross,
                "centered_x_square_sum":rational(sx2),"centered_y_square_sum":rational(sy2),
                "channel_denominator":denominator}}


def f32(x): return struct.unpack('<f',struct.pack('<f',x))[0]


def mapped_inset(width,height):
    sx=f32(width/1672); sy=f32(height/941)
    bx=f32(600*sx); by=f32(269*sy)
    bw=f32(f32(1116*sx)-bx); bh=f32(f32(508*sy)-by)
    dx=f32(4*sx); dy=f32(4*sy)
    return [f32(bx+dx),f32(by+dy),max(0,f32(bw-f32(2*dx))),max(0,f32(bh-f32(2*dy)))]


def main():
    baseline=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT.parent/'baseline/play-reference.png'
    reference=ROOT/'docs/design/atlas-cover-reference.jpg'
    report={"schema_version":1,"scope":"authoring observations, no candidate admission",
       "evidence_class":"generated-reference image statistics",
       "decoder":{"python":platform.python_version(),"pillow":pillow_version,
          "libjpeg_turbo":features.version_feature('libjpeg_turbo'),
          "operation":"RGB decode only; no resampling, gamma/ICC transform or registration"},
       "source_files":[identity(p) for p in (reference,baseline,
          ROOT/'apps/standalone/InstrumentView.cpp',ROOT/'apps/standalone/UiModel.cpp',
          ROOT/'apps/standalone/Drawing.cpp',Path(__file__))],
       "patch_selection":{"primary":list(PRIMARY),"descriptive_only":list(PATCHES)[7:],
           "reason":"Primary strips avoid numerals, heading glyphs, wells and controls. Three bottom-interior witnesses expose an extra warm reflection not identified by the first field; preserve this residual."},
       "images":{}}
    for key,path in (("reference",reference),("genuine_baseline",baseline)):
        image=Image.open(path).convert('RGB')
        assert image.size==(1672,941)
        report['images'][key]={"decoded_rgb_sha256":hashlib.sha256(image.tobytes()).hexdigest(),
            "size":list(image.size),"patches":{name:{"xywh":list(box),"primary":name in PRIMARY,
              "Yprime":patch(image,box),"RGB":[patch(image,box,c) for c in range(3)]}
              for name,box in PATCHES.items()}}
    report['mapped_insets']=[{"logical_size":[w,h],"inset":mapped_inset(w,h)}
        for w,h in ((1672,941),(1400,820),(1920,1080),(1920,820),(1672.5,941.25),(8192,8192))]
    report['canonical_support']={"gradient":[604,273,1112,504],"expanded_one_device_pixel":[603,272,1113,505],
        "gradient_pixels":508*231,"expanded_pixels":510*233,
        "new_grain_canonical_envelope":[606,275,1110,502],"pairs":2304,
        "marks":4608,"nominal_density":4608/(508*231),
        "ideal_sparse_rms_at_amplitude_8":8*math.sqrt(4608/(508*231))}
    destination=HERE/'A08-lower-observations.json'
    destination.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('Wrote',destination.relative_to(ROOT),'(authoring only)')
    for name in PATCHES:
        a=report['images']['reference']['patches'][name]['Yprime']
        b=report['images']['genuine_baseline']['patches'][name]['Yprime']
        print(name, 'reference mean/RMS',round(a['mean']['value'],6),round(a['residual_population_rms'],6),
              'baseline mean/RMS',round(b['mean']['value'],6),round(b['residual_population_rms'],6))

if __name__=='__main__': main()
