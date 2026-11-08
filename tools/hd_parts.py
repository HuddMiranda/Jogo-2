#!/usr/bin/env python3
"""Peças da Elyra (elfa, sem armadura) em alta resolução, para a animação recortada (cutout).

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
DEFS = """
<linearGradient id="skin" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#fbe6d0"/><stop offset="0.55" stop-color="#e8bf9c"/><stop offset="1" stop-color="#b98466"/>
</linearGradient>
<linearGradient id="hair" x1="0" y1="0" x2="0.4" y2="1">
  <stop offset="0" stop-color="#fff6d8"/><stop offset="0.5" stop-color="#ecd28e"/><stop offset="1" stop-color="#b48c46"/>
</linearGradient>
<linearGradient id="tunic" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#7cbc6a"/><stop offset="0.5" stop-color="#3f7a42"/><stop offset="1" stop-color="#1e3e24"/>
</linearGradient>
<linearGradient id="sleeve" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#f2ead2"/><stop offset="1" stop-color="#b8ac8c"/>
</linearGradient>
<linearGradient id="leather" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#b07a4a"/><stop offset="0.5" stop-color="#7a4e2c"/><stop offset="1" stop-color="#43281a"/>
</linearGradient>
<linearGradient id="pants" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#6a6250"/><stop offset="1" stop-color="#2e2a22"/>
</linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#fff0b0"/><stop offset="0.5" stop-color="#e2ae44"/><stop offset="1" stop-color="#8a5e1c"/>
</linearGradient>
<linearGradient id="blade" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#ffffff"/><stop offset="0.5" stop-color="#d4e2ea"/><stop offset="1" stop-color="#7a8a98"/>
</linearGradient>
<radialGradient id="gem" cx="0.35" cy="0.35" r="0.7">
  <stop offset="0" stop-color="#f0fff4"/><stop offset="0.45" stop-color="#2ec27a"/><stop offset="1" stop-color="#0a4a2c"/>
</radialGradient>
"""
S = f'stroke="{LINE}" stroke-width="2" stroke-linejoin="round"'
T = f'stroke="{LINE}" stroke-width="1.4" stroke-linejoin="round"'
RIM = 'fill="none" stroke="#fff6e0" stroke-width="1.4" stroke-linecap="round" opacity="0.65"'

# nome: (caixa [x0, y0, x1, y1] em unidades, conteúdo SVG). Pivô na origem,
# peça "apontando para baixo"; a frente da personagem é +x.
PARTS = {
    'head': ([-30, -40, 20, 40], f"""
<path d="M-6 -30 C -18 -30 -22 -16 -21 -2 C -20 12 -18 24 -24 38 C -14 32 -12 20 -12 8 C -11 18 -12 26 -16 34 C -6 26 -6 10 -4 -4 Z" fill="url(#hair)" {S}/>
<path d="M-3 -10 L 4 -10 L 5 2 L -4 2 Z" fill="url(#skin)" {T}/>
<path d="M-10 -14 C -12 -26 -6 -33 2 -33 C 10 -33 13 -27 13 -21 L 15 -15 L 12.5 -14 L 12.5 -10 C 12 -6 8 -4 4 -4 L -3 -4 C -8 -5 -10 -9 -10 -14 Z" fill="url(#skin)" {S}/>
<path d="M-13 -8 C -17 -26 -8 -37 4 -35 C 12 -34 16 -28 14 -22 C 10 -27 4 -28 -1 -25 C -3 -21 -5 -16 -7 -8 Z" fill="url(#hair)" {S}/>
<path d="M7 -31 C 12 -29 14 -25 13 -21 C 11 -24 9 -27 5 -28 Z" fill="url(#hair)" {T}/>
<path d="M-1 -19 L -16 -30 L -5 -13 Z" fill="url(#skin)" {S}/>
<path d="M-3 -18 L -12 -25" stroke="#b98466" stroke-width="1.2" stroke-linecap="round"/>
<path d="M-12 -23 C -3 -27 6 -28 13 -26" fill="none" stroke="url(#gold)" stroke-width="2" stroke-linecap="round"/>
<circle cx="12" cy="-26" r="1.8" fill="url(#gem)"/>
<path d="M4.5 -19 C 6 -21 9 -21.5 10.5 -19.5 C 8.5 -18 6.5 -18 4.5 -19 Z" fill="#1e4a32"/>
<circle cx="8.6" cy="-19.8" r="0.7" fill="#ffffff"/>
<path d="M4 -22.5 L 11 -22" stroke="#8a6a3a" stroke-width="1.2" stroke-linecap="round"/>
<path d="M9 -9 L 11.5 -9.3" stroke="#8a4a3a" stroke-width="1.1" stroke-linecap="round"/>
<path d="M-11 -12 C -15 -24 -8 -33 2 -33" {RIM}/>
"""),
    'torso': ([-22, -64, 22, 18], f"""
<path d="M-5 -62 L 6 -62 L 7 -54 L -5 -54 Z" fill="url(#skin)" {T}/>
<path d="M-14 -56 C -6 -60 8 -60 16 -56 L 16 -38 C 14 -26 12 -16 13 -10 L 16 15 L 2 12 L -12 15 L -12 -10 C -15 -26 -16 -40 -14 -56 Z" fill="url(#tunic)" {S}/>
<path d="M-2 -58 L 4 -47 L 10 -58" fill="none" stroke="#f2ead2" stroke-width="2.2" stroke-linejoin="round"/>
<path d="M4 -47 L 4 -14" stroke="url(#gold)" stroke-width="1.3" stroke-dasharray="3 2"/>
<path d="M-12 2 L 15 2" stroke="url(#gold)" stroke-width="1.6"/>
<rect x="-14" y="-14" width="30" height="5" rx="1.5" fill="url(#leather)" {T}/>
<rect x="4" y="-15" width="5" height="7" rx="1" fill="url(#gold)" {T}/>
<path d="M-13 -40 C -15 -48 -12 -54 -6 -57" {RIM}/>
"""),
    # Saia da túnica: presa ao tronco, desenhada na frente das pernas.
    'skirt': ([-18, -16, 20, 18], f"""
<path d="M-12 -14 L 15 -14 C 13 -6 13 0 16 15 L 2 12 L -12 15 C -11 4 -11 -6 -12 -14 Z" fill="url(#tunic)" {S}/>
<path d="M-11 2 L 14 2" stroke="url(#gold)" stroke-width="1.6"/>
<rect x="-14" y="-14" width="30" height="5" rx="1.5" fill="url(#leather)" {T}/>
<rect x="4" y="-15" width="5" height="7" rx="1" fill="url(#gold)" {T}/>
"""),
    'shoulder': ([-12, -12, 12, 12], f"""
<path d="M-9 4 C -10 -5 -4 -9 1 -9 C 7 -9 10 -4 9 4 C 8 8 4 10 0 10 C -5 10 -8 8 -9 4 Z" fill="url(#tunic)" {S}/>
<path d="M-8 6 C -3 10 5 10 8 6" fill="none" stroke="url(#gold)" stroke-width="1.6" stroke-linecap="round"/>
"""),
    'upper_arm': ([-8, -4, 8, 28], f"""
<rect x="-5.5" y="-2" width="11" height="27" rx="5" fill="url(#sleeve)" {S}/>
"""),
    'forearm': ([-9, -5, 9, 32], f"""
<path d="M-5 -3 C -5 -5 5 -5 5 -3 L 5 18 L -5 18 Z" fill="url(#sleeve)" {S}/>
<path d="M-6 6 L 6 6 L 5.5 19 L -5.5 19 Z" fill="url(#leather)" {S}/>
<path d="M-6 9 L 6 9 M -6 14 L 6 14" stroke="url(#gold)" stroke-width="1.1"/>
<ellipse cx="0" cy="24" rx="5" ry="5.5" fill="url(#skin)" {S}/>
"""),
    'sword': ([-12, -13, 12, 70], f"""
<rect x="-2.2" y="-7" width="4.4" height="13" rx="1.5" fill="url(#leather)" {T}/>
<circle cx="0" cy="-9" r="3" fill="url(#gold)" {T}/>
<path d="M-11 7 C -6 4 6 4 11 7 C 6 9 -6 9 -11 7 Z" fill="url(#gold)" {T}/>
<circle cx="0" cy="7" r="1.6" fill="url(#gem)"/>
<path d="M-3 9 L 3 9 C 4.5 28 4 48 0 68 C -4 48 -4.5 28 -3 9 Z" fill="url(#blade)" {T}/>
<path d="M0 12 L 0 54" stroke="#9aaab8" stroke-width="1"/>
<path d="M-1.6 14 C -2 30 -1.8 46 -0.6 60" fill="none" stroke="#ffffff" stroke-width="0.9" opacity="0.9"/>
"""),
    'thigh': ([-12, -6, 12, 38], f"""
<path d="M-9 -3 C -9 -6 9 -6 9 -3 L 7 34 C 3 36 -3 36 -6 34 Z" fill="url(#pants)" {S}/>
<path d="M-6 2 L -4 30" {RIM}/>
"""),
    'shin': ([-11, -9, 11, 40], f"""
<path d="M-6 -2 L 6 -2 L 5 12 L -5 12 Z" fill="url(#pants)" {T}/>
<path d="M-7 8 C -4 4 5 4 8 7 L 6 34 C 3 36 -3 36 -6 34 Z" fill="url(#leather)" {S}/>
<path d="M-7 9 C -3 12 4 12 8 8" fill="none" stroke="#c99a62" stroke-width="1.6"/>
<circle cx="1" cy="0" r="4.5" fill="url(#pants)" {T}/>
<path d="M-4 14 L -3 30" {RIM}/>
"""),
    'foot': ([-14, -5, 30, 27], f"""
<path d="M-7 -2 L 6 -2 L 9 9 L 22 14 C 27 16 27 21 23 23 L -9 23 C -11 18 -11 8 -7 -2 Z" fill="url(#leather)" {S}/>
<rect x="-10" y="20" width="35" height="4" rx="2" fill="#3a2a1a" {S}/>
<path d="M9 10 L 20 14" stroke="#c99a62" stroke-width="1.4" stroke-linecap="round"/>
"""),
}


# Escala de cada peça (1 = como desenhada).
SCALE = {}


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
