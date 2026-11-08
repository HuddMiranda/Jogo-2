#!/usr/bin/env python3
"""Elyra desenhada quadro a quadro (estilo Afterimage), sem peças à mostra.

    python tools/hd_frames.py           (usa o Chromium do Playwright via node)

Para cada quadro, as poses de tools/hd_rig.py dão onde ficam quadril, joelhos,
tornozelos, ombros, cotovelos, mãos e espada; este script desenha a personagem
INTEIRA como uma ilustração vetorial: perna (coxa + canela) e braço (braço +
antebraço) são UMA forma contínua que dobra em curva suave, sem juntas; o
contorno escuro só aparece por fora (cada grupo é desenhado primeiro como
silhueta escura e depois preenchido por cima); o cabelo balança atrasado em
relação ao corpo. Saída:

    art/hd/elyra/<animação>/0001.png ...     (quadros)
    scripts/hero_frames.gd                   (quadros, fps, mão e lâmina por quadro)

Um artista pode repintar os PNG por cima mantendo tamanho e posição dos pés.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hd_rig  # noqa: E402
from hd_rig import apply, mat, mul  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'art', 'hd', 'elyra')
R = 1.2                              # pixels por unidade (4 unidades = 1 px do jogo)
BOX = (-120.0, -262.0, 140.0, 22.0)  # área do quadro em unidades (x0, y0, x1, y1); pés em (0, 0)
LINE = '#1a1410'
OUTLINE = 3.2

# animação: (quadros, qps, repete?, função t -> (pose, no chão?))
SWING_TIME = hd_rig.ATTACK_TIME
RUN_PERIOD = 2 * math.pi / 9.5
IDLE_PERIOD = 2 * math.pi / 2.2


def _slash(kind, air):
    def f(i, n):
        base = hd_rig.pose('fall' if air else 'idle', 0.0)
        return hd_rig.attack_pose(base, kind, SWING_TIME * i / (n - 1)), not air
    return f


ANIMS = {
    'idle': (16, 16 / IDLE_PERIOD, True, lambda i, n: (hd_rig.pose('idle', IDLE_PERIOD * i / n), True)),
    'run': (16, 16 / RUN_PERIOD, True, lambda i, n: (hd_rig.pose('run', RUN_PERIOD * i / n), True)),
    'jump': (2, 10, True, lambda i, n: (hd_rig.pose('jump', 0.0), False)),
    'fall': (8, 12, True, lambda i, n: (hd_rig.pose('fall', 2 * math.pi / 6.0 * i / n), False)),
    'spin': (12, 30, True, lambda i, n: (dict(hd_rig.pose('spin', 0.0), spin=2 * math.pi * i / n), False)),
    'dash': (2, 10, True, lambda i, n: (hd_rig.pose('dash', 0.0), True)),
    'wall': (1, 1, True, lambda i, n: (hd_rig.pose('wall', 0.0), False)),
    'hurt': (1, 1, True, lambda i, n: (hd_rig.pose('hurt', 0.0), True)),
    'slash_down': (8, 8 / SWING_TIME, False, _slash(0, False)),
    'slash_up': (8, 8 / SWING_TIME, False, _slash(1, False)),
    'slash_charged': (8, 8 / SWING_TIME, False, _slash(2, False)),
    'air_slash_down': (8, 8 / SWING_TIME, False, _slash(0, True)),
    'air_slash_up': (8, 8 / SWING_TIME, False, _slash(1, True)),
    'air_slash_charged': (8, 8 / SWING_TIME, False, _slash(2, True)),
}

# Para onde o cabelo é jogado em cada animação (unidades, no espaço da cabeça).
HAIR_FLOW = {'run': (-16, -4), 'dash': (-30, -14), 'jump': (-6, 6), 'fall': (-8, -26), 'spin': (-12, 0),
             'wall': (8, -8), 'hurt': (10, -10)}


# --- Cores e degradês -----------------------------------------------------------------

PAL = {
    'skin': ('#fbe6d0', '#e6bc98', '#b07c5e'),
    'hair': ('#fff6d8', '#ecd08a', '#a8803e'),
    'tunic': ('#86c672', '#3f7a42', '#1b3a22'),
    'sleeve': ('#f6efda', '#d6caa8', '#9a8e70'),
    'leather': ('#b8804e', '#7a4e2c', '#3e2416'),
    'pants': ('#6e6654', '#48413a', '#24201a'),
    'gold': ('#fff0b0', '#e2ae44', '#8a5e1c'),
    'blade': ('#ffffff', '#d4e2ea', '#7a8a98'),
}


def darker(hex_color, k):
    v = int(hex_color[1:], 16)
    r, g, b = (v >> 16) & 255, (v >> 8) & 255, v & 255
    return '#%02x%02x%02x' % (int(r * k), int(g * k * 0.98), int(b * min(1.0, k * 1.08)))


def defs():
    out = []
    for name, (a, b, c) in PAL.items():
        for suffix, k in (('', 1.0), ('B', 0.68)):
            out.append(f'<linearGradient id="{name}{suffix}" x1="0" y1="0" x2="1" y2="1">'
                       f'<stop offset="0" stop-color="{darker(a, k)}"/><stop offset="0.5" stop-color="{darker(b, k)}"/>'
                       f'<stop offset="1" stop-color="{darker(c, k)}"/></linearGradient>')
    out.append('<radialGradient id="gem" cx="0.35" cy="0.35" r="0.7"><stop offset="0" stop-color="#f0fff4"/>'
               '<stop offset="0.45" stop-color="#2ec27a"/><stop offset="1" stop-color="#0a4a2c"/></radialGradient>')
    out.append('<filter id="soft" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="0.35"/></filter>')
    return ''.join(out)


# --- Formas contínuas -----------------------------------------------------------------

def _sub(a, b): return (a[0] - b[0], a[1] - b[1])
def _add(a, b): return (a[0] + b[0], a[1] + b[1])
def _mulv(a, k): return (a[0] * k, a[1] * k)


def _norm(v):
    length = math.hypot(*v) or 1.0
    return (v[0] / length, v[1] / length)


def _lerp(a, b, t): return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def chain(points, widths, steps=6):
    """Amostras ao longo de uma corrente de pontos (com larguras), arredondando as dobras."""
    samples = []
    for i in range(len(points) - 1):
        for k in range(steps):
            t = k / steps
            samples.append((_lerp(points[i], points[i + 1], t), widths[i] + (widths[i + 1] - widths[i]) * t))
    samples.append((points[-1], widths[-1]))
    # Suaviza a linha central nas dobras (joelho/cotovelo viram curva).
    pts = [s[0] for s in samples]
    for _ in range(3):
        pts = [pts[0]] + [_lerp(_lerp(pts[j - 1], pts[j + 1], 0.5), pts[j], 0.5) for j in range(1, len(pts) - 1)] + [pts[-1]]
    return [(pts[j], samples[j][1]) for j in range(len(pts))]


def ribbon(samples, cap_start=True, cap_end=True):
    """Contorno fechado (caminho SVG suave) de uma forma de largura variável."""
    left, right = [], []
    n = len(samples)
    for j, (p, w) in enumerate(samples):
        a = samples[max(0, j - 1)][0]
        b = samples[min(n - 1, j + 1)][0]
        t = _norm(_sub(b, a))
        normal = (-t[1], t[0])
        left.append(_add(p, _mulv(normal, w / 2)))
        right.append(_sub(p, _mulv(normal, w / 2)))
    outline = left[:]
    if cap_end:
        p, w = samples[-1]
        t = _norm(_sub(samples[-1][0], samples[-2][0]))
        outline.append(_add(p, _mulv(t, w * 0.45)))
    outline += right[::-1]
    if cap_start:
        p, w = samples[0]
        t = _norm(_sub(samples[0][0], samples[1][0]))
        outline.append(_add(p, _mulv(t, w * 0.45)))
    return smooth_path(outline)


def smooth_path(pts):
    """Caminho fechado passando pelos pontos, com curvas (Catmull-Rom → Bézier)."""
    n = len(pts)
    d = [f'M{pts[0][0]:.2f} {pts[0][1]:.2f}']
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f'C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}')
    return ' '.join(d) + 'Z'


def group(shapes):
    """Grupo com contorno só por fora: silhueta escura grossa atrás, cores por cima."""
    sil = ''.join(f'<path d="{d}" fill="{LINE}" stroke="{LINE}" stroke-width="{OUTLINE}" stroke-linejoin="round"/>'
                  if not d.startswith('<') else d.replace('FILL', LINE).replace('<g ', f'<g stroke="{LINE}" stroke-width="{OUTLINE}" ')
                  for d, _ in shapes)
    fill = ''.join(f'<path d="{d}" fill="{f}"/>' if not d.startswith('<') else d.replace('FILL', f) for d, f in shapes)
    return sil + fill


def tg(m, inner):
    return f'<g transform="matrix({m[0]:.4f} {m[2]:.4f} {m[1]:.4f} {m[3]:.4f} {m[4]:.2f} {m[5]:.2f})">{inner}</g>'


def sub_chain(samples, a, b):
    n = len(samples) - 1
    return samples[int(round(a * n)):int(round(b * n)) + 1]


# --- A personagem -----------------------------------------------------------------------

HEAD = '''
<path d="M-3 -10 L 4 -10 L 5 4 L -4 4 Z" fill="url(#skin{B})"/>
<path d="M-10 -14 C -12 -26 -6 -33 2 -33 C 10 -33 13 -27 13 -21 L 15 -15 L 12.5 -14 L 12.5 -10 C 12 -6 8 -4 4 -4 L -3 -4 C -8 -5 -10 -9 -10 -14 Z" fill="url(#skin)"/>
<path d="M-1 -19 L -17 -31 L -5 -13 Z" fill="url(#skin)"/>
<path d="M-3 -18 L -12 -25.5" stroke="#b07c5e" stroke-width="1.1" stroke-linecap="round"/>
<path d="M-13 -9 C -17 -26 -8 -37 4 -35 C 12 -34 16 -28 14 -22 C 10 -27 4 -28 -1 -25 C -3 -21 -6 -15 -8 -9 Z" fill="url(#hair)"/>
<path d="M7 -31 C 12 -29 14 -25 13 -21 C 11 -24 9 -27 5 -28 Z" fill="url(#hair)"/>
<path d="M-12 -23 C -3 -27 6 -28 13 -26" fill="none" stroke="url(#gold)" stroke-width="1.8" stroke-linecap="round"/>
<circle cx="12" cy="-26" r="1.7" fill="url(#gem)"/>
<path d="M4.5 -19 C 6 -21 9 -21.5 10.5 -19.5 C 8.5 -18 6.5 -18 4.5 -19 Z" fill="#1e4a32"/>
<circle cx="8.6" cy="-19.8" r="0.7" fill="#ffffff"/>
<path d="M4 -22.5 L 11 -22" stroke="#8a6a3a" stroke-width="1.1" stroke-linecap="round"/>
<path d="M9 -9 L 11.5 -9.3" stroke="#8a4a3a" stroke-width="1" stroke-linecap="round"/>
<path d="M-9 -12 C -13 -24 -6 -33 3 -33.5" fill="none" stroke="#fff6e0" stroke-width="1.3" stroke-linecap="round" opacity="0.7"/>
'''
HEAD_SIL = ('M-3 -10 L 4 -10 L 5 4 L -4 4 Z M-13 -9 C -17 -26 -8 -37 4 -35 C 12 -34 16 -28 15 -15 L 12.5 -14 '
            'L 12.5 -10 C 12 -6 8 -4 4 -4 L -3 -4 C -8 -5 -12 -6 -13 -9 Z M-1 -19 L -17 -31 L -5 -13 Z')

TORSO = ('M-5 -62 L 6 -62 L 7 -54 C 12 -57 15 -55 16 -52 L 16 -38 C 14 -26 12 -18 13 -12 L -12 -12 '
         'C -15 -26 -16 -40 -14 -52 C -12 -56 -8 -56 -5 -54 Z')
SKIRT = 'M-12 -14 L 15 -14 C 13 -6 14 2 17 15 C 10 13 6 12 2 13 C -3 12 -8 13 -13 15 C -11 4 -11 -6 -12 -14 Z'
FOOT = 'M-8 -6 L 6 -6 L 9 9 L 22 14 C 27 16 27 21 23 23 L -9 23 C -11 18 -11 8 -8 -6 Z'
SWORD_BLADE = 'M-3 9 L 3 9 C 4.5 28 4 48 0 68 C -4 48 -4.5 28 -3 9 Z'


def frame_svg(p, grounded, anim, i, n):
    parts, shift, sword_m = hd_rig.skeleton(p, grounded)
    by = {}
    for name, m, back in parts:
        by[(name, back)] = m
    # Tudo desce/sobe junto para os pés ficarem no chão.
    root = mat(0, (0, shift))
    M = {k: mul(root, v) for k, v in by.items()}
    torso = M[('torso', False)]
    head = M[('head', False)]
    svg = []

    def leg(back):
        thigh, shin, foot = M[('thigh', back)], M[('shin', back)], M[('foot', back)]
        hip_pt, knee, ankle = apply(thigh, (0, 0)), apply(shin, (0, 0)), apply(foot, (0, 0))
        s = chain([hip_pt, knee, ankle], [20, 13.5, 9.5])
        # Panturrilha: um pouco mais grossa no começo da canela.
        s = [(pt, w + (2.5 * math.sin(math.pi * min(1, max(0, (j / (len(s) - 1) - 0.5) * 2.2)))))
             for j, (pt, w) in enumerate(s)]
        boot = [(pt, w + 1.6) for pt, w in sub_chain(s, 0.62, 1.0)]
        B = 'B' if back else ''
        shapes = [(ribbon(s), f'url(#pants{B})'), (ribbon(boot, cap_start=False), f'url(#leather{B})'),
                  (tg(foot, f'<path d="{FOOT}" fill="FILL"/>'), f'url(#leather{B})')]
        cuff = boot[0]
        out = group(shapes)
        # Dobra do cano da bota.
        t = _norm(_sub(boot[1][0], boot[0][0]))
        nrm = (-t[1], t[0])
        a, b = _add(cuff[0], _mulv(nrm, cuff[1] / 2)), _sub(cuff[0], _mulv(nrm, cuff[1] / 2))
        out += f'<path d="M{a[0]:.2f} {a[1]:.2f} L{b[0]:.2f} {b[1]:.2f}" stroke="{"#7a5a3a" if back else "#d8a86a"}" stroke-width="2.2" stroke-linecap="round"/>'
        out += tg(foot, f'<rect x="-10" y="20" width="35" height="4" rx="2" fill="{"#241810" if back else "#3a2a1a"}"/>')
        return out

    def arm(back):
        up, fore = M[('upper_arm', back)], M[('forearm', back)]
        sh, el, wr = apply(up, (0, 0)), apply(fore, (0, 0)), apply(fore, (0, 20))
        s = chain([sh, el, wr], [13, 9.5, 8])
        bracer = [(pt, w + 1.4) for pt, w in sub_chain(s, 0.62, 1.0)]
        B = 'B' if back else ''
        hand = apply(fore, (0, 24))
        shapes = [(ribbon(s), f'url(#sleeve{B})'), (ribbon(bracer), f'url(#leather{B})'),
                  (f'M{sh[0] - 8:.2f} {sh[1] + 2:.2f} C {sh[0] - 8:.2f} {sh[1] - 7:.2f} {sh[0] + 8:.2f} {sh[1] - 7:.2f} '
                   f'{sh[0] + 8:.2f} {sh[1] + 2:.2f} C {sh[0] + 7:.2f} {sh[1] + 7:.2f} {sh[0] - 7:.2f} {sh[1] + 7:.2f} '
                   f'{sh[0] - 8:.2f} {sh[1] + 2:.2f} Z', f'url(#tunic{B})')]
        out = group(shapes)
        if not back:
            out += tg(sword_m, f'''<g stroke="{LINE}" stroke-width="2" stroke-linejoin="round">
<path d="{SWORD_BLADE}" fill="url(#blade)"/><rect x="-2.2" y="-7" width="4.4" height="13" rx="1.5" fill="url(#leather)"/>
<circle cx="0" cy="-9" r="3" fill="url(#gold)"/><path d="M-11 7 C -6 4 6 4 11 7 C 6 9 -6 9 -11 7 Z" fill="url(#gold)"/></g>
<circle cx="0" cy="7" r="1.6" fill="url(#gem)"/><path d="M0 12 L 0 54" stroke="#9aaab8" stroke-width="1"/>
<path d="M-1.6 14 C -2 30 -1.8 46 -0.6 60" fill="none" stroke="#ffffff" stroke-width="0.9" opacity="0.9"/>''')
        out += (f'<ellipse cx="{hand[0]:.2f}" cy="{hand[1]:.2f}" rx="5.2" ry="5.6" fill="url(#skin{B})" '
                f'stroke="{LINE}" stroke-width="1.8"/>')
        return out

    def hair():
        flow = HAIR_FLOW.get(anim.replace('air_', '').split('_')[0], (0, 0))
        sway = math.sin(2 * math.pi * i / max(1, n)) * (3 if anim in ('idle', 'run', 'fall') else 1)
        root_pt = (-9, -22)
        mid = (-19 + flow[0] * 0.35, 0 + flow[1] * 0.35 + sway * 0.5)
        tip = (-25 + flow[0] + sway, 30 + flow[1])
        s = chain([root_pt, mid, tip], [19, 15, 3], steps=8)
        d = ribbon(s, cap_end=False)
        strands = ''.join(
            f'<path d="M{root_pt[0] + k:.1f} {root_pt[1] + 4:.1f} Q {mid[0] + k:.1f} {mid[1]:.1f} {tip[0] + k * 0.4:.1f} {tip[1] - 4:.1f}" '
            f'fill="none" stroke="{"#fff6d8" if k > 0 else "#a8803e"}" stroke-width="1" opacity="0.6"/>'
            for k in (-3, 2, 5))
        return tg(head, group([(d, 'url(#hair)')]) + strands)

    svg.append(arm(True))
    svg.append(leg(True))
    svg.append(hair())
    svg.append(tg(torso, group([(TORSO, 'url(#tunic)')]) + f'''
<path d="M-2 -58 L 4 -48 L 10 -58" fill="none" stroke="#f2ead2" stroke-width="2.2" stroke-linejoin="round"/>
<path d="M4 -47 L 4 -15" stroke="url(#gold)" stroke-width="1.2" stroke-dasharray="3 2"/>
<path d="M-13 -40 C -15 -48 -12 -54 -6 -57" fill="none" stroke="#e8ffd8" stroke-width="1.3" opacity="0.5"/>'''))
    svg.append(leg(False))
    svg.append(tg(torso, group([(SKIRT, 'url(#tunic)')]) + f'''
<path d="M-12 3 C -4 2 8 2 15 4" fill="none" stroke="url(#gold)" stroke-width="1.6"/>
<path d="M2 -9 L 3 12" stroke="#1b3a22" stroke-width="1" opacity="0.6"/>
<rect x="-14" y="-15" width="30" height="5" rx="1.5" fill="url(#leather)" stroke="{LINE}" stroke-width="1.4"/>
<rect x="4" y="-16" width="5" height="7" rx="1" fill="url(#gold)" stroke="{LINE}" stroke-width="1.2"/>'''))
    svg.append(tg(head, f'<path d="{HEAD_SIL}" fill="{LINE}" stroke="{LINE}" stroke-width="{OUTLINE}" stroke-linejoin="round"/>'
                  + HEAD.replace('{B}', '')))
    svg.append(arm(False))
    hand = apply(mul(root, by[('forearm', False)]), (0, 24))
    blade = apply(mul(root, sword_m), (0, 44))
    x0, y0, x1, y1 = BOX
    w, h = int((x1 - x0) * R), int((y1 - y0) * R)
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}">'
           f'<defs>{defs()}</defs><g filter="url(#soft)">{"".join(svg)}</g></svg>')
    return doc, w, h, hand, blade


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    jobs, data = [], {}
    with tempfile.TemporaryDirectory() as tmp:
        for anim, (n, fps, loop, fn) in ANIMS.items():
            os.makedirs(os.path.join(OUT, anim), exist_ok=True)
            hands, blades = [], []
            for i in range(n):
                p, grounded = fn(i, n)
                doc, w, h, hand, blade = frame_svg(p, grounded, anim, i, n)
                path = os.path.join(tmp, f'{anim}_{i}.svg')
                with open(path, 'w') as f:
                    f.write(doc)
                jobs.append({'svg': path, 'png': os.path.join(OUT, anim, '%04d.png' % (i + 1)), 'w': w, 'h': h})
                hands.append(hand)
                blades.append(blade)
            data[anim] = dict(frames=n, fps=round(fps, 2), loop=loop, hand=hands, blade=blades)
        script = os.path.join(tmp, 'render.js')
        with open(script, 'w') as f:
            f.write('''
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const job of jobs) {
    await page.setViewportSize({ width: job.w, height: job.h });
    await page.setContent(`<html><body style="margin:0;background:transparent">${fs.readFileSync(job.svg, 'utf8')}</body></html>`);
    await page.screenshot({ path: job.png, omitBackground: true, clip: { x: 0, y: 0, width: job.w, height: job.h } });
  }
  await browser.close();
})();
''')
        jobs_path = os.path.join(tmp, 'jobs.json')
        with open(jobs_path, 'w') as f:
            json.dump(jobs, f)
        subprocess.run(['node', script, jobs_path], check=True)
    x0, y0, _, _ = BOX
    v = lambda pt: f'Vector2({pt[0] / 4:.2f}, {pt[1] / 4:.2f})'
    lines = ['class_name HeroFrames',
             '## Gerado por tools/hd_frames.py: quadros da Elyra (art/hd/elyra/<animação>/NNNN.png).',
             '## PIVOT = pés no quadro (px do PNG); SCALE = px do PNG -> px do jogo.',
             '## hand/blade = mão da espada e meio da lâmina por quadro (px do jogo, a partir dos pés).',
             f'const PIVOT := Vector2({-x0 * R:.1f}, {-y0 * R:.1f})',
             f'const SCALE := {1.0 / (4 * R):.5f}',
             'const ANIMS := {']
    for anim, d in data.items():
        lines.append(f'\t"{anim}": {{"frames": {d["frames"]}, "fps": {d["fps"]}, "loop": {"true" if d["loop"] else "false"},')
        lines.append(f'\t\t"hand": [{", ".join(v(p) for p in d["hand"])}],')
        lines.append(f'\t\t"blade": [{", ".join(v(p) for p in d["blade"])}]}},')
    lines.append('}')
    with open(os.path.join(ROOT, 'scripts', 'hero_frames.gd'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'{len(jobs)} quadros em art/hd/elyra/')


if __name__ == '__main__':
    main()
