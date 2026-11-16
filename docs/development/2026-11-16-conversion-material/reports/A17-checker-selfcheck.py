#!/usr/bin/env python3
"""Adversarial checks of the Lower comparator, not product acceptance."""
from fractions import Fraction as F
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from PIL import Image
ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location('lower_comparator', ROOT / 'tools/compare_lower_rack_material.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
checks = []
def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)

# Exact planes have no residual; their three channel slopes are hand-derived.
im = Image.new('RGB', (6, 5))
for y in range(5):
    for x in range(6):
        im.putpixel((x, y), (20 + 2*x + 3*y, 40 + 4*x + 5*y, 60 + 6*x + 7*y))
for c, (base, dx, dy) in enumerate(((20,2,3),(40,4,5),(60,6,7))):
    p=M.patch_statistics(im,(0,0,6,5),c)
    check(f'plane_channel_{c}_mean', F(p['mean_exact']) == base + F(5,2)*dx + 2*dy)
    check(f'plane_channel_{c}_slopes', F(p['slope_x_exact']) == dx and F(p['slope_y_exact']) == dy)
    check(f'plane_channel_{c}_zero_residual', F(p['residual_variance_exact']) == 0)

# A near-boundary exact radical inequality must not be decided by rounded sqrt.
def field(var='1'):
    return {'mean_exact':'0','mean':0.,'slope_x_exact':'0','slope_x':0.,
            'slope_y_exact':'0','slope_y':0.,'residual_variance_exact':var,
            'residual_rms':float(F(var))**.5}
def stats(var='1'):
    return {'patches':{n:{'Yprime':field(var),'RGB':[field(var) for _ in range(3)]} for n in M.PATCHES},
            'right_minus_left_exact':'0','right_minus_left':0.}
a=stats();b=stats();b['patches']['right']['Yprime']=field('9/4')
check('exact_RMS_boundary_accepts',M.reference_screens(a,b)['passed'])
b['patches']['right']['Yprime']=field(str(F(9,4)+F(1,10**20)))
r=M.reference_screens(a,b)
check('exact_RMS_beyond_rounded_boundary_refuses',not r['passed'] and len(r['failed_inequalities'])==1 and r['failed_inequalities'][0]['name']=='right_residual_rms')
check('metadata_rejects_bool_integer_alias',not M.metadata_value_equal([True],[1]))
check('metadata_allows_exact_serializer_float_integer',M.metadata_value_equal([1.0],[1]))
mask=M.declare_mask();spec=mask['cases'][1]
check('source_mask_canonical_geometry',spec['allowance_box']==[603,272,1113,505] and spec['allowed_pixels']==118830)
check('source_mask_has_all_98_cases',len(mask['cases'])==98)
check('source_mask_empty_has_zero_allowance',mask['cases'][66+22]['allowed_pixels']==0)

def header(s):
    return {'schema':1,'case':s['case'],'width':s['output_size'][0],'height':s['output_size'][1],
            'bytes':s['compared_pixels']*4,'fixture':s['fixture'],'scale':s['scale'][0],
            'offset':s['offset'],'active':s['active']}
def frame(h,im):
    return h,im.tobytes(),M.sha(M.canonical_json(h))
with tempfile.TemporaryDirectory(prefix='A17-selfcheck-') as tmp:
    root=Path(tmp)
    base=Image.new('RGBA',tuple(spec['output_size']),(0,0,0,255))
    h=header(spec)
    for name,point,pixel,expected,escaped in (
        ('inside_color',(700,350),(1,0,0,255),True,0),
        ('outside_color',(1200,350),(1,0,0,255),False,1),
        ('outside_alpha',(1200,350),(0,0,0,254),False,1)):
        after=base.copy();after.putpixel(point,pixel);dest=root/name;dest.mkdir()
        r=M.compare_case(spec,frame(h,base),frame(h,after),{},dest)
        check(name,r['passed']==expected and r['outside_allowance_pixels']==escaped)
        check(name+'_one_channel',r['different_channels']==1)
    dest=root/'nonvacuous';dest.mkdir()
    r=M.compare_case(spec,frame(h,base),frame(h,base),{},dest)
    check('active_no_change_cannot_pass',not r['passed'] and not r['nonvacuous_surface_change'])
    inactive=mask['cases'][24];h=header(inactive)
    base=Image.new('RGBA',tuple(inactive['output_size']),(0,0,0,255))
    dest=root/'inactive_equal';dest.mkdir()
    r=M.compare_case(inactive,frame(h,base),frame(h,base),{},dest)
    check('inactive_requires_full_equality',r['passed'] and r['whole_frame_equality_required'])
    after=base.copy();after.putpixel((0,0),(1,0,0,255));dest=root/'inactive_changed';dest.mkdir()
    r=M.compare_case(inactive,frame(h,base),frame(h,after),{},dest)
    check('inactive_change_refused',not r['passed'] and r['outside_allowance_pixels']==1)
report={'scope':'Comparator adversarial selfcheck only, no candidate/material acceptance.',
        'status':'passed','checks':checks,'count':len(checks),
        'comparator_sha256':hashlib.sha256((ROOT/'tools/compare_lower_rack_material.py').read_bytes()).hexdigest(),
        'selfcheck_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
p=Path(__file__).with_name('A17-checker-selfcheck.json')
p.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'passed','checks':len(checks)}))
