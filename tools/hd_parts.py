#!/usr/bin/env python3
"""Peças da VEX-9 em alta resolução, para a animação recortada (cutout).

    python tools/hd_parts.py        (usa o Chromium do Playwright: npm/pip playwright)

Cada peça é um desenho vetorial (SVG) com o PIVÔ (a articulação onde ela gira)
na origem (0, 0) e "apontando para baixo" (ângulo 0). O script desenha cada uma
em PNG (art/hd/vex_parts/<peça>.png, em R pixels por unidade) e grava em
scripts/hd_parts.gd onde fica o pivô de cada PNG. A montagem e a animação ficam
em scenes/player/hd_hero.gd.

Unidades: 1 unidade = 1/4 de pixel do jogo (a personagem tem ~184 unidades,
46 px no jogo). Para a arte final, um artista pode substituir os PNG mantendo
tamanho e pivô (ou desenhar maior e ajustar R).
"""
import json
import os
import subprocess
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'art', 'hd', 'vex_parts')
R = 2  # pixels por unidade

LINE = '#1c1612'
DEFS = '''
<linearGradient id="armor" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#ffffff"/><stop offset="0.45" stop-color="#ece2c8"/><stop offset="1" stop-color="#9c8c6a"/>
</linearGradient>
<linearGradient id="armorDark" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#d8ccb0"/><stop offset="1" stop-color="#7c6e52"/>
</linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#fff0b0"/><stop offset="0.5" stop-color="#e2ae44"/><stop offset="1" stop-color="#8a5e1c"/>
</linearGradient>
<linearGradient id="suit" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#45405a"/><stop offset="1" stop-color="#15131c"/>
</linearGradient>
<linearGradient id="visor" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#e8f4ff"/><stop offset="0.35" stop-color="#5aa8ff"/><stop offset="1" stop-color="#1a3a9a"/>
</linearGradient>
<radialGradient id="gem" cx="0.35" cy="0.35" r="0.7">
  <stop offset="0" stop-color="#f0f6ff"/><stop offset="0.45" stop-color="#4a7aff"/><stop offset="1" stop-color="#14287a"/>
</radialGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#d8ecff" stop-opacity="1"/><stop offset="1" stop-color="#5aa8ff" stop-opacity="0"/>
</radialGradient>
'''
S = f'stroke="{LINE}" stroke-width="2" stroke-linejoin="round"'
RIM = 'fill="none" stroke="#cfe6ff" stroke-width="1.6" stroke-linecap="round" opacity="0.7"'

# nome: (caixa [x0, y0, x1, y1] em unidades, conteúdo SVG)
PARTS = {
    'helmet': ([-40, -50, 40, 4], f'''
<path d="M-22 -26 L-38 -36 L-31 -21 Z" fill="url(#armorDark)" {S}/>
<path d="M-24 -6 C -30 -30 -16 -46 4 -46 C 22 -46 30 -36 30 -25 L 37 -20 L 26 -16 C 26 -8 22 -2 14 0 L -16 0 C -22 0 -24 -2 -24 -6 Z" fill="url(#armor)" {S}/>
<path d="M-3 -46 C 6 -45 11 -40 13 -33 L 7 -31 C 5 -37 1 -41 -6 -44 Z" fill="url(#gold)" {S}/>
<path d="M7 -27 L 33 -21 L 31 -15 L 7 -19 Z" fill="url(#visor)" {S}/>
<path d="M11 -24 L 27 -20.5" stroke="#ffffff" stroke-width="1.6" stroke-linecap="round" opacity="0.9"/>
<path d="M6 -16 L 26 -14 C 24 -6 20 -2 12 0 L 3 0 Z" fill="url(#armor)" {S}/>
<rect x="12" y="-10" width="3" height="5" rx="1" fill="{LINE}"/><rect x="17" y="-9" width="3" height="5" rx="1" fill="{LINE}"/>
<rect x="-12" y="-25" width="11" height="11" rx="2" fill="url(#gold)" {S}/>
<path d="M-21 -10 C -26 -26 -16 -40 0 -43" {RIM}/>
'''),
    'torso': ([-24, -64, 24, 12], f'''
<rect x="-6" y="-62" width="12" height="10" rx="2" fill="url(#suit)" {S}/>
<path d="M-12 -32 L 12 -32 L 10 -10 L -10 -10 Z" fill="url(#suit)" {S}/>
<path d="M-16 -12 L 16 -12 L 14 4 L 4 9 L -4 9 L -14 4 Z" fill="url(#armor)" {S}/>
<rect x="-17" y="-16" width="34" height="6" rx="2" fill="url(#gold)" {S}/>
<circle cx="3" cy="-13" r="2.6" fill="url(#gem)"/>
<path d="M-18 -52 C -10 -59 12 -59 20 -51 L 18 -35 C 8 -28 -8 -28 -16 -35 Z" fill="url(#armor)" {S}/>
<path d="M-12 -40 C -4 -36 6 -36 14 -40" fill="none" stroke="#9c8c6a" stroke-width="1.4"/>
<circle cx="7" cy="-45" r="5" fill="url(#gem)" {S}/>
<circle cx="5.5" cy="-46.5" r="1.4" fill="#ffffff"/>
<path d="M-16 -36 C -18 -44 -14 -52 -8 -55" {RIM}/>
'''),
    'pauldron': ([-22, -16, 24, 20], f'''
<path d="M-18 6 C -20 -8 -8 -14 4 -14 C 16 -14 22 -6 21 6 C 20 12 14 16 2 16 C -10 16 -17 12 -18 6 Z" fill="url(#armor)" {S}/>
<path d="M-15 10 C -6 16 12 16 19 9" fill="none" stroke="url(#gold)" stroke-width="3.5" stroke-linecap="round"/>
<path d="M-12 -2 C -6 -8 4 -10 12 -7" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" opacity="0.8"/>
'''),
    'upper_arm': ([-9, -4, 9, 28], f'''
<rect x="-6" y="-2" width="12" height="27" rx="6" fill="url(#suit)" {S}/>
<rect x="-7" y="7" width="14" height="8" rx="3" fill="url(#armorDark)" {S}/>
'''),
    'forearm': ([-12, -5, 12, 34], f'''
<ellipse cx="0" cy="26" rx="6" ry="5" fill="url(#suit)" {S}/>
<path d="M-8 -3 C -8 -5 8 -5 8 -3 L 9 22 C 6 24 -6 24 -9 22 Z" fill="url(#armor)" {S}/>
<rect x="-9" y="4" width="18" height="4" rx="1.5" fill="url(#gold)" {S}/>
'''),
    'cannon': ([-15, -7, 15, 48], f'''
<rect x="-6" y="-5" width="12" height="10" rx="4" fill="url(#suit)" {S}/>
<rect x="-11" y="0" width="22" height="42" rx="9" fill="url(#armor)" {S}/>
<rect x="-12" y="7" width="24" height="5" rx="2" fill="url(#gold)" {S}/>
<rect x="-12" y="29" width="24" height="4" rx="2" fill="url(#gold)" {S}/>
<ellipse cx="0" cy="41" rx="9" ry="4" fill="#2a2420" {S}/>
<ellipse cx="0" cy="41" rx="6" ry="2.4" fill="url(#visor)"/>
<path d="M-7 4 L -7 36" {RIM}/>
'''),
    'thigh': ([-13, -6, 13, 38], f'''
<path d="M-10 -3 C -10 -6 10 -6 10 -3 L 8 34 C 4 36 -4 36 -7 34 Z" fill="url(#armor)" {S}/>
<path d="M5 0 L 4 30" stroke="url(#gold)" stroke-width="2.5" stroke-linecap="round"/>
<path d="M-7 2 L -5 30" {RIM}/>
'''),
    'shin': ([-12, -9, 12, 40], f'''
<rect x="-4" y="30" width="8" height="8" rx="2" fill="url(#suit)" {S}/>
<path d="M-7 4 L 8 4 L 6 33 C 3 35 -3 35 -6 33 Z" fill="url(#armor)" {S}/>
<ellipse cx="1" cy="0" rx="9" ry="7" fill="url(#armor)" {S}/>
<circle cx="3" cy="0" r="2.4" fill="url(#gold)"/>
<path d="M-4 8 L -3 30" {RIM}/>
'''),
    'foot': ([-14, -5, 32, 27], f'''
<path d="M-8 -2 L 6 -2 L 10 8 L 26 14 C 30 16 30 21 26 23 L -10 23 C -12 18 -12 8 -8 -2 Z" fill="url(#armor)" {S}/>
<rect x="-11" y="20" width="39" height="5" rx="2" fill="#3a3226" {S}/>
<path d="M10 9 L 24 14" stroke="url(#gold)" stroke-width="2" stroke-linecap="round"/>
'''),
}


# Escala de cada peça (proporções humanas: capacete e ombreiras menores).
SCALE = {'helmet': 0.72, 'pauldron': 0.8}


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    with tempfile.TemporaryDirectory() as tmp:
        jobs = []
        for name, (box, body) in PARTS.items():
            k = SCALE.get(name, 1.0)
            x0, y0, x1, y1 = (v * k for v in box)
            body = f'<g transform="scale({k})">{body}</g>'
            w, h = int(round((x1 - x0) * R)), int(round((y1 - y0) * R))
            svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}">'
                   f'<defs>{DEFS}</defs>{body}</svg>')
            path = os.path.join(tmp, name + '.svg')
            with open(path, 'w') as f:
                f.write(svg)
            jobs.append({'svg': path, 'png': os.path.join(OUT, name + '.png'), 'w': w, 'h': h})
            meta[name] = {'pivot': [round(-x0 * R, 2), round(-y0 * R, 2)], 'size': [w, h]}
        script = os.path.join(tmp, 'render.js')
        with open(script, 'w') as f:
            f.write('''
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(process.argv[2]);
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
        subprocess.run(['node', script, json.dumps(jobs)], check=True)
    lines = ['class_name HDParts', '## Gerado por tools/hd_parts.py: pivô (em pixels do PNG) e tamanho de cada peça.',
             f'const UNITS_PER_PIXEL := {1.0 / R}', 'const PARTS := {']
    for name, m in meta.items():
        lines.append(f'\t"{name}": {{"pivot": Vector2({m["pivot"][0]}, {m["pivot"][1]}), "size": Vector2({m["size"][0]}, {m["size"][1]})}},')
    lines.append('}')
    with open(os.path.join(ROOT, 'scripts', 'hd_parts.gd'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'{len(meta)} peças em art/hd/vex_parts/')


if __name__ == '__main__':
    main()
