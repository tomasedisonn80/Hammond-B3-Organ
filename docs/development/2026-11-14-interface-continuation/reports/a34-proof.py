#!/usr/bin/env python3
"""Retain literal app crop comparisons, pixel checks and font budgets for A34."""
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

report = Path(__file__).resolve().parent
repo = report.parents[3]
temporary = repo.parent / 'a34-captures'
layouts = json.loads((report / 'a34-layout-fonts.json').read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(rectangle):
    x, y, width, height = rectangle
    return (math.floor(x), math.floor(y), math.ceil(x + width), math.ceil(y + height))


def intersects(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def contained(a, b):
    return a[0] >= b[0] - .001 and a[1] >= b[1] - .001 and a[0] + a[2] <= b[0] + b[2] + .001 and a[1] + a[3] <= b[1] + b[3] + .001


result = {'qualification': 'Literal crops from actual application PNGs, without resizing or repainting app pixels; software renderer at 1x.',
          'cases': [], 'glyphs_checked': 0, 'unchanged_natural_labels': 0, 'crop_provenance': []}
preset_rows = []
header_rows = []
for layout in layouts:
    width, height = layout['window']
    title = layout['title']
    assert title['after_center'] == width / 2
    assert len(layout['header_controls']) == 10 and len(layout['presets']) == 24
    assert layout['playing_counts'] == [61, 61, 25]
    for action in layout['header_controls']:
        assert not intersects(title['after_ink'], action['bounds'])
    for key in layout['presets']:
        assert contained(key['label'], key['bounds'])
        for glyph in key['glyphs']:
            assert glyph['size'] == 9 and glyph['advance'] <= key['label'][2]
            assert contained(glyph['ink'], key['label'])
            result['glyphs_checked'] += 1
        if len(key['glyphs']) == 2:
            assert not intersects(key['glyphs'][0]['ink'], key['glyphs'][1]['ink'])
    left = math.floor(min(k['bounds'][0] for k in layout['presets'])) - 4
    right = math.ceil(max(k['bounds'][0] + k['bounds'][2] for k in layout['presets'])) + 4
    top = math.floor(min(k['bounds'][1] for k in layout['presets'])) - 6
    bottom = math.ceil(max(k['bounds'][1] + k['bounds'][3] for k in layout['presets'])) + 6
    crops = []
    for mode in ('dimensional', 'flat'):
        images = {phase: Image.open(temporary / phase / f'{width}x{height}-{mode}.png').convert('RGB')
                  for phase in ('before', 'after')}
        changed = ImageChops.difference(images['before'], images['after']).convert('L')
        allowed = Image.new('L', (width, height))
        allow = ImageDraw.Draw(allowed)
        for key in layout['presets']:
            if len(key['glyphs']) == 2:
                allow.rectangle(box(key['bounds']), fill=255)
            else:
                region = box(key['label'])
                assert ImageChops.difference(images['before'].crop(region), images['after'].crop(region)).getbbox() is None
                result['unchanged_natural_labels'] += 1
        for ink in (title['before_ink'], title['after_ink']):
            x, y, w, h = ink
            allow.rectangle(box([x - 2, y - 2, w + 5, h + 6]), fill=255)
        outside = ImageChops.multiply(changed, ImageChops.invert(allowed))
        assert outside.getbbox() is None, (width, height, mode, outside.getbbox())
        focused = next(k for k in layout['presets'] if k['manual'] == 0 and k['index'] == 3)
        cyan = sum(pixel == (165, 228, 223) for pixel in images['after'].crop(box(focused['bounds'])).get_flattened_data())
        assert cyan >= 2
        item = {'window': [width, height], 'mode': mode, 'focused_dsharp_cyan_pixels': cyan,
                'all_changed_pixels_inside_accidentals_or_title': True,
                'header_advance_center': title['after_center'], 'native_title_ink': {}}
        for phase, image in images.items():
            bounds = title[f'{phase}_ink']
            region = box([bounds[0] - 2, bounds[1] - 2, bounds[2] + 4, bounds[3] + 4])
            xs, ys = [], []
            for y in range(region[1], region[3]):
                for x in range(region[0], region[2]):
                    if image.getpixel((x, y)) == (214, 182, 124):
                        xs.append(x); ys.append(y)
            assert xs and ys
            item['native_title_ink'][phase] = [min(xs), min(ys), max(xs) + 1, max(ys) + 1]
            assert min(xs) >= math.floor(bounds[0]) and max(xs) + 1 <= math.ceil(bounds[0] + bounds[2])
            if width in (960, 1400, 1672):
                crops.append((f'{phase.upper()} / {mode}', image.crop((left, top, right, bottom))))
                result['crop_provenance'].append({'window': [width, height], 'mode': mode, 'phase': phase,
                    'source_sha256': sha(temporary / phase / f'{width}x{height}-{mode}.png'),
                    'literal_crop': [left, top, right, bottom]})
            if mode == 'dimensional' and width in (960, 1280, 1672):
                header_rows.append((f'{phase.upper()} / {width} x {height}', image.crop((0, 14, width, 108))))
        before = item['native_title_ink']['before']
        after = item['native_title_ink']['after']
        expected_shift = title['after_center'] - title['before_center']
        assert after[0] - before[0] == after[2] - before[2] == expected_shift
        assert before[1] == after[1] and before[3] == after[3]
        item['native_title_horizontal_shift'] = expected_shift
        result['cases'].append(item)
    if crops:
        preset_rows.append((f'{width} x {height}', crops))

sheet = Image.new('RGB', (720, sum(max(c.height for _, c in crops) + 55 for _, crops in preset_rows)), '#242424')
draw = ImageDraw.Draw(sheet)
y = 0
for label, crops in preset_rows:
    draw.text((8, y + 4), label, fill='white')
    for index, (caption, crop) in enumerate(crops):
        x = index * 180 + 8
        draw.text((x, y + 23), caption, fill='white')
        sheet.paste(crop, (x, y + 42))
    y += max(c.height for _, c in crops) + 55
sheet.save(report / 'a34-preset-before-after.png', optimize=True)
header = Image.new('RGB', (1692, len(header_rows) * 118), '#242424')
draw = ImageDraw.Draw(header)
for row, (caption, crop) in enumerate(header_rows):
    draw.text((10, row * 118 + 4), caption, fill='white')
    header.paste(crop, (10, row * 118 + 20))
header.save(report / 'a34-header-before-after.png', optimize=True)
full = temporary / 'after/1672x941-dimensional.png'
(report / 'a34-play-reference-after.png').write_bytes(full.read_bytes())
result['images'] = {p.name: {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in report.glob('a34-*.png')}
(report / 'a34-proof.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'cases': len(result['cases']), 'glyphs_checked': result['glyphs_checked'],
                  'unchanged_natural_labels': result['unchanged_natural_labels'], 'images': result['images']}, indent=2))
