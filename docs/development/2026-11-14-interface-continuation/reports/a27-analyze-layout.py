#!/usr/bin/env python3
"""Independent rectangle/inventory checks on a27-layout-probe.cpp JSON.

Not a production geometry oracle or a replacement for A18/A19. This audits
ordinary control composition, exposed pointer samples and font envelopes.
"""
import collections
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

EPS = 0.001
COMMON = {11, 12, 13, 14, 15, 18, 20, 21}
EXPECTED = {1: 4, 4: 18, 5: 2, 6: 4, 7: 1, 8: 3, 9: 1, 10: 1,
            11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 18: 1, 19: 24, 20: 3, 21: 1}
NAMES = {1: "Edit bank", 4: "Manual drawbar", 5: "Pedal mixture", 6: "Percussion",
         7: "Expression", 8: "Keyboard target", 9: "Octave down", 10: "Octave up",
         11: "Save", 12: "Load", 13: "Audio", 14: "Help", 15: "Panic",
         18: "MIDI", 19: "Preset", 20: "Workspace", 21: "Flat"}


def contains(outer, inner):
    x, y, w, h = inner
    a, b, c, d = outer
    return (all(map(math.isfinite, inner + outer)) and w > 0 and h > 0
            and x >= a-EPS and y >= b-EPS and x+w <= a+c+EPS and y+h <= b+d+EPS)


def overlap(a, b):
    x, y = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[0]+a[2], b[0]+b[2]), min(a[1]+a[3], b[1]+b[3])
    return [x, y, right-x, bottom-y] if right-x > EPS and bottom-y > EPS else None


def allowed_preset_overlap(a, b):
    return a['id'][0] == b['id'][0] == 19 and a['id'][1] == b['id'][1]


def audit(cases):
    failures = []
    counts = collections.Counter()
    groups = {}
    samples = []
    per_size = {}
    common_by_size = {}

    def check(ok, kind, context, detail):
        counts[kind + '_checks'] += 1
        if not ok:
            failures.append({'kind': kind, 'case': context, 'detail': detail})

    for case in cases:
        width, height = case['size']
        context = f"{width}x{height}/w{case['workspace']}/p{case['presentation']}"
        controls = case['controls']
        counts['layouts'] += 1
        counts['retained_records'] += case['retained_controls']
        counts['visible_records'] += len(controls)
        inventory = collections.Counter(c['id'][0] for c in controls)
        expected = EXPECTED if case['workspace'] == 0 else {k: v for k, v in EXPECTED.items() if k in COMMON}
        check(case['retained_controls'] == 68 and inventory == expected, 'inventory', context, dict(inventory))
        check(len({tuple(c['id']) for c in controls}) == len(controls), 'unique_control_identity', context, len(controls))
        focus_count = len(controls) + (3 if case['workspace'] == 0 else 0)
        check(focus_count == (71 if case['workspace'] == 0 else 10), 'focus_inventory', context, focus_count)
        window = [0, 0, width, height]
        panels = [p for p in case['panels'] if p[2] and p[3]]
        for panel in panels:
            check(contains(window, panel), 'panel_containment', context, panel)
        for a, b in itertools.combinations(panels, 2):
            check(not overlap(a, b), 'panel_disjoint', context, [a, b])
        check(not overlap(case['panels'][0], case['workspace_panel']), 'header_body_disjoint', context,
              [case['panels'][0], case['workspace_panel']])

        header = [c for c in controls if c['id'][0] in COMMON]
        positions = [(c['id'], c['bounds']) for c in header]
        size_key = f'{width}x{height}'
        if size_key not in common_by_size:
            common_by_size[size_key] = positions
        check(len(header) == 10 and positions == common_by_size[size_key], 'common_header_positions', context, positions)
        for c in controls:
            ident = c['id']
            check(contains(window, c['bounds']) and contains(c['parent'], c['bounds']), 'control_containment', context, c)
            for region in ('label', 'value', 'track'):
                r = c[region]
                if r[2] == 0 and r[3] == 0:
                    continue
                check(contains(c['bounds'], r), region + '_containment', context, {'id': ident, 'rect': r})
            if ident[0] in COMMON:
                check(contains(case['panels'][0], c['bounds']), 'header_control_containment', context, c)
            for point in c['pointer_samples'] + [c['label_center']]:
                check(point['hit'] == ident, 'ordinary_pointer_hit', context, {'id': ident, **point})
            for painted in c['paint_rects']:
                check(contains(c['bounds'], painted), 'slider_slot_cap_containment', context, {'id': ident, 'rect': painted})
            for t in c['text']:
                check(contains(t['box'], t['ink_envelope']), 'text_envelope_containment', context, {'id': ident, **t})
                key = f"{NAMES[ident[0]]}/{t['role']}/{'flat' if case['presentation'] else 'dimensional'}"
                value = {'size': t['effective_size'], 'text': t['text'], 'case': context, 'id': ident,
                         'box': t['box'], 'ink_envelope': t['ink_envelope']}
                if key not in groups or value['size'] < groups[key]['size']:
                    groups[key] = value
                if ident[0] in COMMON:
                    check(t['effective_size'] + EPS >= 11, 'header_font_floor', context, value)
                if ident[0] != 19:
                    check(t['effective_size'] + EPS >= 10, 'nonpreset_compact_font_floor', context, value)
        for a, b in itertools.combinations(controls, 2):
            intersection = overlap(a['bounds'], b['bounds'])
            if intersection and allowed_preset_overlap(a, b):
                counts['intentional_preset_rectangle_pairs'] += 1
            else:
                check(not intersection, 'nonpreset_control_disjoint', context, {'a': a['id'], 'b': b['id'], 'intersection': intersection})
            for ta, tb in itertools.product(a['text'], b['text']):
                check(not overlap(ta['ink_envelope'], tb['ink_envelope']), 'control_text_disjoint', context,
                      {'a': a['id'], 'b': b['id'], 'text_a': ta, 'text_b': tb})
        for t in case['header_text']:
            check(contains(case['panels'][0], t['ink_envelope']), 'header_text_containment', context, t)
            for c in header:
                check(not overlap(t['ink_envelope'], c['bounds']), 'header_text_controls_disjoint', context, {'text': t, 'id': c['id']})
        if case['workspace'] == 0 and case['presentation'] == 0:
            def first(kind, index=0):
                return next(c for c in controls if c['id'][0] == kind and c['id'][1] == 0 and c['id'][3] == index)
            per_size[size_key] = {
                'cabinet': bool(case['cabinet']), 'edit_in_cheeks': bool(case['edit_in_cheeks']),
                'header': case['panels'][0], 'workspace_body': case['workspace_panel'],
                'header_controls': [{'id': c['id'], 'label': c['text'][0]['text'], 'bounds': c['bounds'],
                                     'font_size': c['text'][0]['effective_size']} for c in header],
                'upper_edit_A': first(1)['bounds'],
                'upper_preset_C': first(19)['bounds'], 'upper_preset_C_exposed': first(19)['exposed'],
                'upper_preset_D_sharp': first(19, 3)['bounds'],
                'upper_drawbar_16': first(4)['bounds'], 'upper_drawbar_track_16': first(4)['track'],
                'smallest_exposed_control': min(({'id': c['id'], 'rect': c['exposed'],
                                                  'half_min_extent': min(c['exposed'][2:])/2} for c in controls),
                                                key=lambda x: x['half_min_extent']),
            }
            for c in controls:
                if c['id'][1] == 0 and ((c['id'][0] == 19 and c['id'][3] in (0, 1, 3)) or c['id'][0] == 20):
                    samples.append({'case': context, 'id': c['id'], 'bounds': c['bounds'], 'exposed': c['exposed'], 'text': c['text']})
    return {'status': 'passed' if not failures else 'failed', 'counts': dict(counts), 'failures': failures,
            'font_minima': groups, 'responsive_sizes': per_size, 'representative_samples': samples}


def main():
    if len(sys.argv) != 4:
        raise SystemExit('usage: a27-analyze-layout.py layouts.json source-before.json output.json')
    raw, before_path, output = map(Path, sys.argv[1:])
    data = json.loads(raw.read_text())
    source = json.loads(before_path.read_text())
    root = Path(__file__).resolve().parents[4]
    after = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in source['source_hashes']}
    result = audit(data['cases'])
    result['status_applies_to'] = 'Automated ordinary-control composition checks only.'
    result['readability_status'] = 'open_for_A34'
    result['scope'] = '54 layouts; ordinary controls only; playing-key homography and transition behavior inherited from A18/A19, not rerun'
    result['coordinate_tolerance_logical_pixels'] = EPS
    result['source'] = source
    result['source_hashes_after'] = after
    result['recorded_inputs_unchanged'] = after == source['source_hashes']
    result['probe_output_sha256'] = hashlib.sha256(raw.read_bytes()).hexdigest()
    result['audit_source_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
        (Path(__file__), Path(__file__).with_name('a27-layout-probe.cpp'))}
    result['readability_residual'] = {
        'classification': 'Measured retained limitation; geometry pass does not close preset readability.',
        'minimum_preset_D_sharp_font': 6.15384626,
        'minimum_preset_D_sharp_ink_envelope': [9.03846359, 4.42306519],
        'requested_preset_font': 9,
        'minimum_preset_accidental_label_width': 10,
        'full_semantic_focus_footer_source_size': 10.5,
        'disposition': 'Open for A34 before final handoff; A28 independently audits native scale/pixels; root assigns production repair ownership separately.'}
    result['limits'] = ['No new native process was run by this probe; eight existing gallery PNGs visually inspected separately.',
                        'Text sizes and ink envelopes derive from the embedded atlas and inspected fit rule, not raster coverage, native accessibility or physical DPI.',
                        'Pointer checks sample center, four inset exposed corners and label center; preset rectangle overlap is intentional.',
                        'Slider cap/slot rectangles exclude ornamental shadows; endpoint caps plus the slot cover all movement positions.',
                        'Focus counts are composition census, not a repeat of A18 traversal, suppression or owner tests.',
                        'Both banks remain controls; one A/B edited combination was used because bank identity does not alter rectangles.',
                        'This report does not establish reference image equality or hardware fidelity.']
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'counts': result['counts'], 'failure_count': len(result['failures']),
                      'recorded_inputs_unchanged': result['recorded_inputs_unchanged']}, indent=2))
    if result['failures']:
        print(json.dumps(result['failures'][:10], indent=2))
    return 0 if not result['failures'] and result['recorded_inputs_unchanged'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
