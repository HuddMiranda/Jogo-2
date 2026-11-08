#!/usr/bin/env python3
"""Peças da Elyra em alta resolução, para a animação recortada (cutout).

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
  <stop offset="0" stop-color="#2f5446"/><stop offset="1" stop-color="#0c1c16"/>
</linearGradient>
<linearGradient id="visor" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#f0fff0"/><stop offset="0.35" stop-color="#5ee89a"/><stop offset="1" stop-color="#0e5a3a"/>
</linearGradient>
<radialGradient id="gem" cx="0.35" cy="0.35" r="0.7">
  <stop offset="0" stop-color="#f0fff4"/><stop offset="0.45" stop-color="#2ec27a"/><stop offset="1" stop-color="#0a4a2c"/>
</radialGradient>
<linearGradient id="hair" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#f4f6f0"/><stop offset="1" stop-color="#a8b4b0"/>
</linearGradient>
<radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#e4ffe8" stop-opacity="1"/><stop offset="1" stop-color="#5ee89a" stop-opacity="0"/>
</radialGradient>
'''
S = f'stroke="{LINE}" stroke-width="2" stroke-linejoin="round"'
RIM = 'fill="none" stroke="#e4ffe8" stroke-width="1.6" stroke-linecap="round" opacity="0.7"'

# nome: (caixa [x0, y0, x1, y1] em unidades, conteúdo SVG)
PARTS = {
    'helmet': ([-54, -58, 40, 40], f'''
<path d="M-16 -30 C -34 -26 -48 -6 -50 34 C -42 18 -38 8 -32 0 C -34 14 -36 24 -42 36 C -26 20 -22 4 -18 -6 C -16 4 -18 12 -22 20 C -10 6 -8 -8 -8 -18 Z" fill="url(#hair)" {S}/>
<path d="M-24 -18 C -34 -6 -40 10 -42 24" fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.6"/>
<path d="M-6 -24 L -40 -40 L -30 -24 L -12 -15 Z" fill="url(#armorDark)" {S}/>
<path d="M-22 -8 C -26 -30 -12 -46 6 -45 C 22 -44 30 -34 30 -24 L 32 -16 L 24 -12 C 24 -6 20 -2 14 0 L -14 0 C -20 0 -22 -3 -22 -8 Z" fill="url(#armor)" {S}/>
<path d="M20 -36 C 8 -52 -14 -56 -30 -46 C -14 -48 2 -46 14 -34 Z" fill="url(#gold)" {S}/>
<path d="M8 -26 C 16 -30 26 -29 31 -22 C 24 -19 15 -19 8 -22 Z" fill="url(#visor)" {S}/>
<path d="M12 -25 C 18 -27 24 -26 28 -23" fill="none" stroke="#ffffff" stroke-width="1.4" stroke-linecap="round" opacity="0.9"/>
<path d="M6 -17 L 25 -14 C 23 -6 19 -2 12 0 L 3 0 Z" fill="url(#armor)" {S}/>
<path d="M-2 -26 C -14 -30 -30 -36 -44 -40 C -34 -30 -20 -20 -4 -15 Z" fill="url(#armor)" {S}/>
<path d="M-6 -22 C -18 -26 -28 -31 -36 -36" fill="none" stroke="url(#gold)" stroke-width="2" stroke-linecap="round"/>
<circle cx="20" cy="-33" r="2.6" fill="url(#gem)" {S}/>
<path d="M-20 -10 C -24 -26 -14 -40 0 -43" {RIM}/>
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
    'cannon': ([-15, -7, 15, 50], f'''
<rect x="-6" y="-5" width="12" height="10" rx="4" fill="url(#suit)" {S}/>
<path d="M-9 0 C -9 -4 9 -4 9 0 L 7 27 L -7 27 Z" fill="url(#armor)" {S}/>
<rect x="-10" y="6" width="20" height="4" rx="1.5" fill="url(#gold)" {S}/>
<path d="M-5 13 C -1 16 1 20 -2 24 M 4 13 C 1 17 2 21 5 23" fill="none" stroke="url(#gold)" stroke-width="1.6" stroke-linecap="round"/>
<path d="M-8 26 L -11 40 L -4 33 Z" fill="url(#gold)" {S}/>
<path d="M8 26 L 11 40 L 4 33 Z" fill="url(#gold)" {S}/>
<circle cx="0" cy="38" r="9" fill="url(#glow)" opacity="0.55"/>
<path d="M0 27 L 5 35 L 0 46 L -5 35 Z" fill="url(#gem)" {S}/>
<path d="M-1 30 L -3 35" stroke="#ffffff" stroke-width="1.2" stroke-linecap="round"/>
<path d="M-6 4 L -5 24" {RIM}/>
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
