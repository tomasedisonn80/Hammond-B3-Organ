#!/usr/bin/env python3
"""Independent Lower contract audit, using exact uncentered normal equations.

No build, candidate renderer, material formula, learned pixel mask or image write.
The author receipt is read only after measurements have been independently made.
"""
from fractions import Fraction as Q
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
PATCHES = [
    ('left', (612,320,18,128)), ('right', (1094,320,14,128)),
    ('left_top', (612,298,18,14)), ('right_top', (1094,298,14,14)),
    ('center_top', (800,302,112,6)), ('left_bottom', (612,460,18,20)),
    ('right_bottom', (1094,460,14,20)),
    ('bottom_interior_left', (704,492,12,8)),
    ('bottom_interior_middle', (852,492,14,8)),
    ('bottom_interior_right', (1047,492,12,8)),
]


def identity(path):
    data = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def rational(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator), 'value': float(value)}


def solve(matrix, vector):
    a = [[Q(v) for v in row] + [Q(vector[i])] for i, row in enumerate(matrix)]
    for pivot in range(3):
        assert a[pivot][pivot]
        divisor = a[pivot][pivot]
        a[pivot] = [v/divisor for v in a[pivot]]
        for row in range(3):
            if row == pivot:
                continue
            multiplier = a[row][pivot]
            a[row] = [v-multiplier*w for v,w in zip(a[row],a[pivot])]
    return [row[-1] for row in a]


def measure(image, box, channel):
    x,y,w,h = box
    n = w*h
    normal = [[0]*3 for _ in range(3)]
    rhs = [0]*3
    zz = 0
    denominator = 10000 if channel is None else 1
    for yy in range(h):
        for xx in range(w):
            rgb = image.getpixel((x+xx,y+yy))
            z = 2126*rgb[0]+7152*rgb[1]+722*rgb[2] if channel is None else rgb[channel]
            basis = [1,xx,yy]
            zz += z*z
            for i in range(3):
                rhs[i] += basis[i]*z
                for j in range(3):
                    normal[i][j] += basis[i]*basis[j]
    coefficients = solve(normal, [Q(v,denominator) for v in rhs])
    sse = Q(zz,denominator*denominator)-sum(c*Q(b,denominator) for c,b in zip(coefficients,rhs))
    assert sse >= 0
    return {'mean': rational(Q(rhs[0],n*denominator)),
            'slope_x': rational(coefficients[1]), 'slope_y': rational(coefficients[2]),
            'residual_sse': rational(sse), 'residual_population_rms': math.sqrt(float(sse/n)),
            'uncentered_normal_matrix': normal, 'uncentered_integer_rhs': rhs,
            'sum_integer_squares': zz, 'denominator': denominator, 'n': n}


def f32(value):
    return struct.unpack('<f',struct.pack('<f',value))[0]


def geometry(width,height):
    sx,sy = f32(width/1672),f32(height/941)
    x,y = f32(600*sx),f32(269*sy)
    w,h = f32(f32(1116*sx)-x),f32(f32(508*sy)-y)
    dx,dy = f32(4*sx),f32(4*sy)
    return (sx,sy), (x,y,w,h), (f32(x+dx),f32(y+dy),f32(w-f32(2*dx)),f32(h-f32(2*dy)))


def mix(value):
    value ^= value >> 16
    value = (value*0x7FEB352D) & 0xffffffff
    value ^= value >> 15
    value = (value*0x846CA68B) & 0xffffffff
    return value ^ (value >> 16)


def marks():
    return [(606+mix(0xB3160A08 ^ (4*i+2*m))%504,
             275+mix(0xB3160A08 ^ (4*i+2*m+1))%227)
            for i in range(2304) for m in (0,1)]


def filled(rect,rx,ry):
    x,y,w,h = rect
    l,t = math.trunc(f32(x*rx)),math.trunc(f32(y*ry))
    return (l,t,l+max(math.trunc(f32(w*rx)),1),t+max(math.trunc(f32(h*ry)),1))


def support_summary(width,height,rx,ry,points):
    (sx,sy),(bx,by,bw,bh),(ix,iy,iw,ih) = geometry(width,height)
    intrinsic = (math.ceil(ix*rx-.5),math.ceil(iy*ry-.5),
                 math.ceil((ix+iw)*rx-.5),math.ceil((iy+ih)*ry-.5))
    rows = int(max(0,math.floor(f32(f32(bh/sy)-16))))
    cols = int(max(0,math.floor(f32(f32(bw/sx)-21))))
    step = max(4,math.ceil(math.sqrt(rows*cols/(3*2048))))
    def count(p): return ((rows-2)//p+1 if rows>1 else 0)*((cols-2)//(3*p)+1 if cols>1 else 0)
    while count(step)>2048:
        step += 1
    old = []
    for row in range(1,rows,step):
        for col in range(1,cols,step*3):
            grain = (row*1973+col*9277)&0xffffffff
            x = f32(bx+f32(f32(f32(7+float(col))+float((grain>>5)%3))*sx))
            y = f32(by+f32(f32(7+float(row))*sy))
            old.extend([filled((x,y,sx,sy),rx,ry),
                        filled((f32(x+f32(3*sx)),f32(y+sy),f32(2*sx),sy),rx,ry)])
    assert len(old)//2 == count(step) <= 2048
    new = [filled((f32(x*sx),f32(y*sy),sx,sy),rx,ry) for x,y in points]
    l,t,r,b = intrinsic
    assert all(l<=a and t<=c and d<=r and e<=b for a,c,d,e in old+new)
    return {'logical_size':[width,height], 'renderer_scale':[rx,ry],
            'mapped_inset':[ix,iy,iw,ih], 'intrinsic_ltrb':list(intrinsic),
            'intrinsic_pixels':(r-l)*(b-t), 'expanded_pixels':(r-l+2)*(b-t+2),
            'old_rows':rows,'old_columns':cols,'old_step':step,'old_pairs':len(old)//2,
            'new_marks':len(new),'all_old_and_new_marks_inside_intrinsic':True}


def numeric(value): return Q(int(value['numerator']),int(value['denominator']))


def main():
    baseline = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT.parent/'baseline/play-reference.png'
    reference = ROOT/'docs/design/atlas-cover-reference.jpg'
    files = [reference,baseline,ROOT/'docs/design/LOWER_RACK_MATERIAL_CONTRACT.md',
             ROOT/'apps/standalone/InstrumentView.cpp',
             ROOT/'apps/standalone/native_tests/test_standalone_upper_rack_material_raster.cpp',
             ROOT/'apps/standalone/native_tests/test_standalone_lower_rack_material_raster.cpp',Path(__file__)]
    report = {'schema':1,'scope':'independent protocol admission only; no candidate acceptance',
              'method':'exact uncentered 3x3 normal equations and Gauss elimination; no author measurement helpers',
              'decoder':{'python':platform.python_version(),'pillow':pillow_version,
                         'libjpeg_turbo':features.version_feature('libjpeg_turbo'),
                         'operation':'RGB decode only; no resampling or registration'},
              'source_files':[identity(path) for path in files], 'images':{}}
    for name,path in [('reference',reference),('genuine_baseline',baseline)]:
        image = Image.open(path).convert('RGB')
        assert image.size == (1672,941)
        report['images'][name] = {'decoded_rgb_sha256':hashlib.sha256(image.tobytes()).hexdigest(),
                                 'patches':{}}
        for label,box in PATCHES:
            report['images'][name]['patches'][label] = {'xywh':list(box), 'Yprime':measure(image,box,None),
                                                      'RGB':[measure(image,box,c) for c in range(3)]}
    # Read author's receipt only after independent results have been formed.
    author = json.loads((HERE/'A08-lower-observations.json').read_text())
    matches = 0
    for name in report['images']:
        ours,theirs = report['images'][name],author['images'][name]
        assert ours['decoded_rgb_sha256'] == theirs['decoded_rgb_sha256']
        for label,_ in PATCHES:
            a,b = ours['patches'][label],theirs['patches'][label]
            for independent,claimed in zip([a['Yprime']]+a['RGB'],[b['Yprime']]+b['RGB']):
                for field in ('mean','slope_x','slope_y','residual_sse'):
                    assert numeric(independent[field]) == numeric(claimed[field]), (name,label,field)
                    matches += 1
                assert independent['residual_population_rms'] == claimed['residual_population_rms']
    report['author_reproduction'] = {'exact_rational_equalities':matches,
                                    'population_rms_equalities':80,'decoded_hash_equalities':2}
    screens = []
    ref,old = (report['images'][name]['patches'] for name in ('reference','genuine_baseline'))
    def screen(name,a,b,limit):
        error = abs(a-b)
        screens.append({'name':name,'baseline':float(a),'reference':float(b),
                        'absolute_error':float(error),'limit':float(limit),'passed':error<=limit})
    for label,_ in PATCHES[:7]:
        screen(label+'.Yprime.mean',numeric(old[label]['Yprime']['mean']),numeric(ref[label]['Yprime']['mean']),Q(5,2))
        for channel in range(3):
            screen(label+'.RGB.'+str(channel)+'.mean',numeric(old[label]['RGB'][channel]['mean']),
                   numeric(ref[label]['RGB'][channel]['mean']),Q(3))
    for label in ('left','right'):
        screen(label+'.Yprime.residual_population_rms',old[label]['Yprime']['residual_population_rms'],
               ref[label]['Yprime']['residual_population_rms'],.5)
        for field,limit in [('slope_x',Q(6,100)),('slope_y',Q(25,1000))]:
            screen(label+'.Yprime.'+field,numeric(old[label]['Yprime'][field]),numeric(ref[label]['Yprime'][field]),limit)
    screen('right-minus-left.Yprime.mean',numeric(old['right']['Yprime']['mean'])-numeric(old['left']['Yprime']['mean']),
           numeric(ref['right']['Yprime']['mean'])-numeric(ref['left']['Yprime']['mean']),Q(7,4))
    assert len(screens)==35
    report['baseline_authoring_screens'] = {'count':len(screens),'passed':sum(s['passed'] for s in screens),
                                          'failed':sum(not s['passed'] for s in screens),'screens':screens,
                                          'interpretation':'Material observations only; not native fixture invariants.'}
    points = marks()
    report['grain_position_audit'] = {'marks':len(points),'unique_origins':len(set(points)),
        'canonical_origin_bounds_inclusive':[min(x for x,y in points),min(y for x,y in points),
                                              max(x for x,y in points),max(y for x,y in points)],
        'ordered_uint16le_xy_sha256':hashlib.sha256(b''.join(struct.pack('<HH',*p) for p in points)).hexdigest(),
        'ideal_sparse_rms_at_amplitude_8':8*math.sqrt(len(points)/(508*231))}
    geometry_cases = [(w,h,scale,scale) for w,h in [(1672,941),(1400,820),(1920,1080),
                      (1920,820),(1672.5,941.25),(8192,8192)] for scale in (1,1.5,2)]
    geometry_cases.append((1672,941,1.5,2))
    report['independent_operation_support'] = [support_summary(*case,points) for case in geometry_cases]
    maximum = report['independent_operation_support'][17]
    report['work_audit'] = {'field_columns':127,'edge_array_integers':128,'grain_primitives':4608,
        'hash_calls':9216,'max_observed_intrinsic_rows_at_8192_scale_2':maximum['intrinsic_ltrb'][3]-maximum['intrinsic_ltrb'][1],
        'contract_conservative_rows':4028,'contract_max_primitives':127*4028+4608,
        'resource_visible_rows_at_most':64,'resource_max_primitives':127*64+4608}
    destination = HERE/'A11-independent-lower-audit.json'
    destination.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'report':str(destination.relative_to(ROOT)),
                      'exact_equalities':matches,'baseline_passed':sum(s['passed'] for s in screens),
                      'baseline_failed':sum(not s['passed'] for s in screens),
                      'geometry_cases':len(geometry_cases),'grain':report['grain_position_audit'],
                      'work':report['work_audit']}))

if __name__ == '__main__': main()
