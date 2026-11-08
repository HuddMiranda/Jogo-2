#!/usr/bin/env python3
"""Gera os tilesets do cenário em pixel art (art/tiles/).

    python tools/generate_tiles.py          (precisa de: pip install pillow numpy)

Para cada bioma (ruins, hive):
  art/tiles/<bioma>.png       — blocos de 16 × 16 (atlas 8 × 4):
      linha 0: topo (4 variações), canto esquerdo, canto direito, coluna única
      linha 1: miolo (4 variações), borda esquerda, borda direita, coluna única
      linha 2: miolo fundo (mais escuro), mesmas colunas
      linha 3: plataforma vazada: ponta esquerda, meio (3), ponta direita, única
  art/tiles/<bioma>_wall.png  — parede do fundo (128 × 128, repete sem emenda)

As fases (scenes/level/level.gd) desenham o mapa com esses blocos e a parede
do fundo com a textura. Para retocar à mão,
edite os PNG mantendo o tamanho; rodar o script de novo os sobrescreve.
"""
import os
import random

import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'art', 'tiles')
T = 16


def c(*v): return np.array(v, dtype=np.float32)


BIOMES = {
    # Ruínas de Aelindor (fase de abertura): pedra clara élfica com entalhes
    # dourados, tomada por musgo; galhos vivos servem de plataforma.
    'ruins': dict(base=c(150, 150, 132), light=c(196, 194, 172), dark=c(96, 98, 86), mortar=c(44, 50, 42),
                  top=c(62, 118, 52), top_light=c(140, 196, 90), drip=c(46, 92, 44), pattern='elven',
                  ledge='branch', wood=c(104, 74, 48), wood_light=c(150, 112, 72), wood_dark=c(60, 40, 26),
                  leaf=c(86, 150, 64), accent=c(226, 184, 84),
                  wall=c(20, 34, 30), wall_light=c(34, 54, 44), wall_mortar=c(10, 18, 16), wall_glow=c(150, 230, 140)),
    # Colmeia da Árvore-Mãe (fase da Vespa): favos de âmbar dentro do tronco
    # gigante, com cipós por cima.
    'hive': dict(base=c(170, 104, 30), light=c(222, 156, 56), dark=c(104, 58, 18), mortar=c(56, 32, 14),
                 top=c(70, 110, 44), top_light=c(150, 190, 80), drip=c(210, 140, 40), pattern='comb',
                 ledge='branch', wood=c(96, 64, 40), wood_light=c(142, 100, 62), wood_dark=c(54, 34, 20),
                 leaf=c(96, 146, 60), accent=c(255, 200, 80),
                 wall=c(46, 30, 18), wall_light=c(66, 44, 24), wall_mortar=c(24, 14, 8)),
}

# Entalhes élficos (folha, runa, arco), em ouro, 5 × 5.
CARVINGS = [["00100", "01110", "11111", "01110", "00100"],
            ["01010", "00100", "11111", "00100", "01010"],
            ["01110", "10001", "10101", "10001", "00000"]]


def noise(w, h, rng, scale=4):
    """Ruído suave e periódico (repete sem emenda)."""
    hh, ww = max(1, h // scale), max(1, w // scale)
    small = np.array([[rng.random() for _ in range(ww)] for _ in range(hh)])
    img = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.array(img, dtype=np.float32) / 255.0


def material(b, w, h, rng, deep=False):
    """Textura do miolo do bloco (w × h), com o padrão do bioma."""
    base, light, dark, mortar = b['base'], b['light'], b['dark'], b['mortar']
    if deep:
        base, light, dark = base * 0.72, light * 0.72, dark * 0.75
    img = np.zeros((h, w, 3), dtype=np.float32)
    n = noise(w, h, rng, 4)
    img[:] = base
    pattern = b['pattern']
    if pattern == 'panel':
        # Placas de metal de cantos arredondados, com chanfro e rebites.
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        for y0 in range(0, h, 8):
            offset = 8 if (y0 // 8) % 2 else 0
            for x0 in range(-offset, w, 16):
                tone = base + (light - base) * rng.uniform(0.0, 0.35)
                for yy in range(y0, min(y0 + 8, h)):
                    for xx in range(max(x0, 0), min(x0 + 16, w)):
                        lx, ly = xx - x0, yy - y0
                        corner = (lx in (0, 15)) and (ly in (0, 7))
                        if lx == 0 or ly == 7 or corner:
                            img[yy, xx] = mortar
                        elif ly == 0 or lx == 1:
                            img[yy, xx] = np.minimum(tone + 34, 255)
                        elif ly == 6 or lx == 15:
                            img[yy, xx] = tone * 0.7
                        else:
                            img[yy, xx] = tone * (1.0 - 0.06 * (ly / 7.0))
                if rng.random() < 0.35 and x0 + 13 < w and x0 + 3 >= 0:
                    rx = x0 + (3 if rng.random() < 0.5 else 12)
                    if 0 <= rx < w - 1:
                        img[y0 + 3, rx] = np.minimum(tone + 60, 255)
                        img[y0 + 4, rx] = tone * 0.6
        return img
    if pattern == 'elven':
        # Cantaria élfica: blocos lisos de pedra clara, chanfrados, com
        # entalhes dourados de vez em quando.
        for y0 in range(0, h, 8):
            offset = 8 if (y0 // 8) % 2 else 0
            for x0 in range(-offset, w, 16):
                tone = base + (light - base) * rng.uniform(0.0, 0.4)
                x1, x2 = max(x0, 0), min(x0 + 16, w)
                img[y0:y0 + 8, x1:x2] = tone[None, None, :] * (0.94 + 0.1 * n[y0:y0 + 8, x1:x2, None])
                img[y0, x1:x2] = np.minimum(tone + 26, 255)
                img[y0 + 1, x1:x2] = np.minimum(tone + 10, 255)
                img[min(y0 + 6, h - 1), x1:x2] = tone * 0.8
                if not deep and rng.random() < 0.22 and x0 + 10 < w and x0 + 5 >= 0:
                    glyph = rng.choice(CARVINGS)
                    gx = x0 + 5
                    for j in range(3):
                        for i, ch in enumerate(glyph[j + 1][1:4]):
                            if ch == '1' and 0 <= gx + i < w:
                                img[y0 + 2 + j, gx + i] = b['accent'] * (1.0 if j == 0 else 0.8)
                if rng.random() < 0.18:                               # musgo nas frestas
                    mx = rng.randint(x1, max(x1, x2 - 1))
                    img[min(y0 + 6, h - 1), mx] = b['top'] * (0.6 if deep else 0.9)
            img[min(y0 + 7, h - 1), :] = mortar
            for x0 in range(-offset, w + 16, 16):
                if 0 <= x0 < w:
                    img[y0:y0 + 8, x0] = mortar
        return img
    if pattern == 'comb':
        # Favos: células redondas e brilhantes de cera.
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        img[:] = mortar
        for cy, cx in ((4, 4), (4, 12), (12, 0), (12, 8), (12, 16), (4, 20), (12, -8)):
            r2 = ((xs - cx) ** 2 + (ys - cy) ** 2) / 14.0
            cell = r2 < 1.0
            tone = (-(xs - cx) * 0.55 - (ys - cy) * 0.83) / 4.0 * 0.8 + (1 - r2) * 0.4
            img[cell] = base
            img[cell & (tone > 0.35)] = light
            img[cell & (tone < -0.25)] = dark
            img[cell & (tone > 0.75)] = np.minimum(light + 50, 255)
        return img
    if pattern == 'brick':
        # Tijolos 16 × 8 desencontrados: alinhados à grade de 16, emendam bem.
        for y0 in range(0, h, 8):
            offset = 8 if (y0 // 8) % 2 else 0
            for x0 in range(-offset, w, 16):
                tone = base + (light - base) * rng.uniform(0.0, 0.6) if rng.random() < 0.8 else dark * 1.1
                x1, x2 = max(x0, 0), min(x0 + 16, w)
                img[y0:y0 + 8, x1:x2] = tone
                img[y0, x1:x2] = np.minimum(tone + 22, 255)        # aresta de cima clara
                img[min(y0 + 6, h - 1), x1:x2] = tone * 0.82        # base mais escura
                if rng.random() < 0.15:                              # lasca / rachadura
                    cx = rng.randint(x1, max(x1, x2 - 2))
                    img[y0 + 2:y0 + 6, cx] = mortar * 1.3
            img[min(y0 + 7, h - 1), :] = mortar
            for x0 in range(-offset, w + 16, 16):
                if 0 <= x0 < w:
                    img[y0:y0 + 8, x0] = mortar
    elif pattern == 'rock':
        img[:] = base[None, None, :] * (0.85 + 0.3 * n[:, :, None])
        for _ in range(w * h // 90):
            x, y = rng.randrange(w), rng.randrange(h)
            img[y, x] = light if rng.random() < 0.5 else dark
        for _ in range(max(1, w * h // 400)):                       # rachaduras
            x, y = rng.randrange(w), rng.randrange(h)
            for _ in range(rng.randint(3, 7)):
                img[y % h, x % w] = mortar
                x += rng.choice((-1, 0, 1)); y += 1
        if 'accent' in b and not deep:
            for _ in range(max(1, w * h // 700)):
                x, y = rng.randrange(1, w - 1), rng.randrange(1, h - 1)
                img[y, x] = b['accent']; img[y - 1, x] = b['accent'] * 0.7
    elif pattern == 'flesh':
        img[:] = base[None, None, :] * (0.8 + 0.4 * n[:, :, None])
        for _ in range(max(1, w * h // 120)):                        # veias
            x, y = rng.randrange(w), rng.randrange(h)
            for _ in range(rng.randint(4, 9)):
                img[y % h, x % w] = mortar
                x += rng.choice((-1, 0, 1)); y += rng.choice((0, 1))
        for _ in range(max(1, w * h // 300)):                        # poros
            x, y = rng.randrange(1, w - 1), rng.randrange(1, h - 1)
            img[y, x] = dark; img[y - 1, x] = light
        if not deep and rng.random() < 0.3:
            for _ in range(max(1, w * h // 900)):                    # pústula brilhante
                x, y = rng.randrange(2, w - 2), rng.randrange(2, h - 2)
                img[y - 1:y + 1, x - 1:x + 1] = b['accent'] * 0.8
    else:  # obsidian
        img[:] = base[None, None, :] * (0.8 + 0.4 * n[:, :, None])
        for _ in range(max(1, w * h // 200)):                        # facetas
            x, y = rng.randrange(w), rng.randrange(h)
            L = rng.randint(2, 5)
            for k in range(L):
                img[(y + k) % h, (x + k) % w] = light
        for _ in range(max(1, w * h // 500)):                        # veios violeta
            x, y = rng.randrange(w), rng.randrange(h)
            for _ in range(rng.randint(3, 7)):
                img[y % h, x % w] = b['accent'] * (0.45 if deep else 0.7)
                x += 1; y += rng.choice((-1, 0, 1))
    return img


def add_top(img, b, rng):
    """Camada do topo: musgo, gelo, membrana ou crosta, escorrendo um pouco."""
    h, w, _ = img.shape
    top, top_light, drip = b['top'], b['top_light'], b['drip']
    for x in range(w):
        depth = 3 + (1 if rng.random() < 0.35 else 0)
        img[0:depth, x] = top
        img[0, x] = top_light
        if rng.random() < 0.18:                                       # gota / fio escorrendo
            img[depth:depth + rng.randint(1, 4), x] = drip
    img[min(4, h - 1), :] = img[min(4, h - 1), :] * 0.8               # sombra logo abaixo
    if 'leaf' in b:
        for x in range(1, w - 1, 3):                                  # folhinhas e flores no musgo
            if rng.random() < 0.3:
                img[1, x] = b['leaf'] * 1.2
            if rng.random() < 0.06:
                img[1, x] = c(240, 230, 190)
    if b.get('icicles'):
        for x in range(1, w - 1, 5):                                  # pingentes de gelo
            if rng.random() < 0.5:
                img[4:4 + rng.randint(2, 4), x] = top
    return img


def edge(img, side, b):
    """Borda lateral (bloco que termina): aresta escura e chanfro claro."""
    h, w, _ = img.shape
    if side == 'left':
        img[:, 0] = b['mortar']
        img[:, 1] = np.minimum(img[:, 1] + 18, 255)
    else:
        img[:, w - 1] = b['mortar']
        img[:, w - 2] = img[:, w - 2] * 0.7
    return img


def ledge_tile(b, rng, part):
    """Plataforma vazada (16 × 16; a parte de cima é a que pisa)."""
    img = np.zeros((T, T, 4), dtype=np.float32)
    kind = b['ledge']
    wood, wl, wd = b['wood'], b['wood_light'], b['wood_dark']
    if kind == 'planks':
        img[1:6, :, :3] = wood
        img[1, :, :3] = wl
        img[5, :, :3] = wd
        img[1:6, :, 3] = 255
        for x in (rng.randint(3, 6), rng.randint(9, 13)):
            img[3, x, :3] = (30, 26, 28)                               # pregos
        img[0, :, :3] = b['mortar']; img[0, :, 3] = 255
        img[6, :, :3] = b['mortar']; img[6, :, 3] = 255
        if part in ('left', 'right', 'single') or rng.random() < 0.4:  # mão-francesa
            x = 3 if part != 'right' else 11
            for k in range(7):
                img[6 + k, x + (k // 2 if part != 'right' else -(k // 2)), :3] = wd
                img[6 + k, x + (k // 2 if part != 'right' else -(k // 2)), 3] = 255
    elif kind in ('slab', 'ice'):
        img[0:6, :, :3] = wood
        img[0, :, :3] = wl
        img[5, :, :3] = wd
        img[0:6, :, 3] = 255
        for _ in range(4):
            x = rng.randrange(T)
            img[rng.randint(1, 4), x, :3] = wl if kind == 'ice' else wd
        if kind == 'ice':
            for x in range(1, T, 4):
                if rng.random() < 0.6:
                    n = rng.randint(2, 6)
                    img[6:6 + n, x, :3] = wood; img[6:6 + n, x, 3] = 255
                    img[6 + n - 1, x, :3] = wl
        else:
            img[6, 2:T - 2, :3] = wd * 0.7; img[6, 2:T - 2, 3] = 255
    elif kind == 'branch':
        # Galho vivo: casca com veios, folhas por cima.
        for x in range(T):
            y = 2 + int(round(np.sin(x / T * np.pi * 2 + 0.6) * 0.7))
            img[y:y + 4, x, :3] = wood; img[y:y + 4, x, 3] = 255
            img[y, x, :3] = wl
            img[y + 3, x, :3] = wd
            if x % 5 == 2:
                img[y + 2, x, :3] = wd
        for x in range(0, T, 4):
            if rng.random() < 0.6:
                lx = x + rng.randint(0, 2)
                img[0:2, lx, :3] = b['leaf']; img[0:2, lx, 3] = 255
                img[0, lx, :3] = b['leaf'] * 1.3
        if part in ('left', 'right', 'single'):
            x = 3 if part != 'right' else 12
            img[6:10, x, :3] = b['leaf'] * 0.7; img[6:10, x, 3] = 255  # folha pendurada
    elif kind == 'sinew':
        for x in range(T):
            y = 2 + int(round(np.sin(x / T * np.pi * 2) * 0.8))
            img[y:y + 3, x, :3] = wood; img[y:y + 3, x, 3] = 255
            img[y, x, :3] = wl
            img[y + 2, x, :3] = wd
        for x in (4, 11):
            img[1:6, x, :3] = wd; img[1:6, x, 3] = 255                # nós
    else:  # bone
        img[1:5, :, :3] = wood
        img[1, :, :3] = wl
        img[4, :, :3] = wd
        img[1:5, :, 3] = 255
        for x in (0, 7, 8, 15):
            img[0:6, x, :3] = wl; img[0:6, x, 3] = 255                # juntas dos ossos
    if part in ('left', 'single'):
        img[:, 0, 3] = 0
    if part in ('right', 'single'):
        img[:, T - 1, 3] = 0
    # Contorno escuro de 1 px.
    alpha = img[:, :, 3] > 0
    grown = alpha.copy()
    grown[1:] |= alpha[:-1]; grown[:-1] |= alpha[1:]; grown[:, 1:] |= alpha[:, :-1]; grown[:, :-1] |= alpha[:, 1:]
    border = grown & ~alpha
    img[border, :3] = (12, 8, 16)
    img[border, 3] = 255
    return img


def wall_texture(b, rng):
    """Parede do fundo, escura e repetível (128 × 128)."""
    S = 128
    img = np.zeros((S, S, 3), dtype=np.float32)
    n = noise(S, S, rng, 16)
    n2 = noise(S, S, rng, 4)
    wall, wl, wm = b['wall'], b['wall_light'], b['wall_mortar']
    img[:] = wall[None, None, :] * (0.85 + 0.25 * n[:, :, None] + 0.1 * n2[:, :, None])
    pattern = {'panel': 'brick', 'elven': 'forest'}.get(b['pattern'], b['pattern'])
    if pattern == 'forest':
        # Floresta escura ao fundo: troncos verticais com casca, copas e
        # vaga-lumes (repete a cada 128 px).
        for trunk in range(4):
            cx = trunk * 32 + rng.randint(4, 14)
            tw = rng.randint(7, 13)
            tone = wl * rng.uniform(1.0, 1.35)
            for x in range(cx, cx + tw):
                xx = x % S
                k = (x - cx) / tw
                img[:, xx] = tone[None, :] * (0.75 + 0.45 * np.sin(k * np.pi)) * (0.9 + 0.15 * n2[:, xx, None])
                if (x - cx) % 3 == 1:                                  # veios da casca
                    img[:, xx] *= 0.85
            for _ in range(3):                                         # nós e musgo
                y = rng.randrange(S)
                img[y:y + 3, (cx + tw // 2) % S] = wm
        for _ in range(70):                                            # folhagem (cachos de folhas)
            x, y = rng.randrange(S), rng.randrange(S)
            r = rng.randint(1, 3)
            ys, xs = np.ogrid[0:S, 0:S]
            dx = np.minimum(np.abs(xs - x), S - np.abs(xs - x))
            dy = np.minimum(np.abs(ys - y), S - np.abs(ys - y))
            mask = (dx * dx + dy * dy) < r * r
            img[mask] = wall * 1.5 + c(0, 14, 4)
            img[(y - r) % S, x] = wall * 2.0 + c(0, 20, 6)
        for _ in range(10):                                            # vaga-lumes
            x, y = rng.randrange(1, S - 1), rng.randrange(1, S - 1)
            img[y, x] = b['wall_glow'] * 0.8
            img[y - 1, x] = img[y + 1, x] = img[y, x - 1] = img[y, x + 1] = b['wall_glow'] * 0.3
        return img
    if pattern == 'comb':
        # Favos grandes e escuros ao fundo (repete a cada 128 px).
        ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
        img[:] = wm
        for row in range(7):
            for col in range(6):
                cx = col * 24 + (12 if row % 2 else 0)
                cy = row * 21
                for ox in (-128, 0, 128):
                    for oy in (-128, 0, 128):
                        dx, dy = xs - (cx + ox), ys - (cy + oy)
                        r2 = (dx * dx + dy * dy) / 100.0
                        cell = r2 < 1.0
                        tone = (-dx * 0.55 - dy * 0.83) / 10.0 + (1 - r2) * 0.3
                        img[cell] = wall
                        img[cell & (tone > 0.35)] = wl
                        img[cell & (tone < -0.3)] = wall * 0.7
        return img
    if pattern == 'brick':
        for y0 in range(0, S, 16):
            offset = 16 if (y0 // 16) % 2 else 0
            for x0 in range(-offset, S, 32):
                tone = wall + (wl - wall) * rng.uniform(0, 1)
                x1, x2 = max(x0, 0), min(x0 + 32, S)
                img[y0:y0 + 16, x1:x2] = tone[None, None, :] * (0.9 + 0.2 * n2[y0:y0 + 16, x1:x2, None])
                img[y0, x1:x2] = tone * 1.25
            img[y0 + 15, :] = wm
            for x0 in range(-offset, S + 32, 32):
                if 0 <= x0 < S:
                    img[y0:y0 + 16, x0] = wm
    elif pattern in ('rock', 'obsidian'):
        for _ in range(60):
            x, y = rng.randrange(S), rng.randrange(S)
            for _ in range(rng.randint(5, 14)):
                img[y % S, x % S] = wm
                x += rng.choice((-1, 0, 1)); y += 1
        for _ in range(220):
            x, y = rng.randrange(S), rng.randrange(S)
            img[y, x] = wl
    else:  # flesh: dobras horizontais e veias
        for y in range(S):
            img[y] *= 0.85 + 0.25 * np.sin(y / S * np.pi * 8 + n[y, :] * 3)[:, None]
        for _ in range(40):
            x, y = rng.randrange(S), rng.randrange(S)
            for _ in range(rng.randint(6, 16)):
                img[y % S, x % S] = wm
                x += rng.choice((-1, 0, 1)); y += 1
    if 'accent' in b and pattern != 'flesh':
        for _ in range(12):
            x, y = rng.randrange(S), rng.randrange(S)
            img[y, x] = b['accent'] * 0.35
    return img


def to_image(arr, alpha=None):
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    if arr.shape[2] == 4:
        return Image.fromarray(arr, 'RGBA')
    a = np.full(arr.shape[:2] + (1,), 255, dtype=np.uint8)
    return Image.fromarray(np.concatenate([arr, a], axis=2), 'RGBA')


SKULL = ["01110", "11111", "10101", "11111", "01010"]


def grim(b):
    """Tom mais sombrio: cores mais escuras e menos saturadas (exceto o brilho)."""
    out = {}
    for k, v in b.items():
        if isinstance(v, np.ndarray) and k not in ('accent',):
            gray = v.mean()
            out[k] = (v * 0.72 + gray * 0.28) * 0.84
        else:
            out[k] = v
    return out


def add_bones(img, b, rng):
    """Crânio enterrado na pedra (miolo fundo do castelo e do Abismo)."""
    bone = c(150, 142, 124) if b['pattern'] != 'obsidian' else c(120, 108, 120)
    x0, y0 = rng.randint(2, 9), rng.randint(2, 9)
    for j, line in enumerate(SKULL):
        for i, ch in enumerate(line):
            if ch == '1':
                img[y0 + j, x0 + i] = bone * (1.0 if j < 2 else 0.85)
    img[y0 + 2, x0 + 1] = img[y0 + 2, x0 + 3] = c(10, 6, 10)
    return img


def grime(img, b, rng, amount):
    """Escorridos escuros (umidade, sangue velho) descendo pela parede."""
    h, w, _ = img.shape
    for _ in range(amount):
        x = rng.randrange(w)
        y = rng.randrange(h)
        length = rng.randint(6, 30)
        tone = c(0, 0, 0)
        for k in range(length):
            yy = (y + k) % h
            alpha = 0.45 * (1 - k / length)
            img[yy, x] = img[yy, x] * (1 - alpha) + tone * alpha
    return img


def build(name, b):
    rng = random.Random(name)
    atlas = Image.new('RGBA', (T * 8, T * 4), (0, 0, 0, 0))
    for row, deep in ((0, False), (1, False), (2, True)):
        for col in range(7):
            tile = material(b, T, T, rng, deep)
            if row == 0:
                tile = add_top(tile, b, rng)
            if deep and col == 2 and b['pattern'] in ('brick', 'obsidian'):
                tile = add_bones(tile, b, rng)
            if col in (4, 6):
                tile = edge(tile, 'left', b)
            if col in (5, 6):
                tile = edge(tile, 'right', b)
            atlas.paste(to_image(tile), (col * T, row * T))
    for col, part in enumerate(('left', 'mid', 'mid', 'mid', 'right', 'single')):
        atlas.paste(to_image(ledge_tile(b, rng, part)), (col * T, 3 * T))
    atlas.save(os.path.join(OUT, f'{name}.png'))
    to_image(grime(wall_texture(b, rng), b, rng, 8)).save(os.path.join(OUT, f'{name}_wall.png'))


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, b in BIOMES.items():
        build(name, b)
    print(f'{len(BIOMES)} tilesets gerados em art/tiles/')


if __name__ == '__main__':
    main()
