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
    # Ruínas bio-mecânicas (fase de abertura): placas de metal tomadas por veios vivos.
    'ruins': dict(base=c(70, 82, 92), light=c(104, 120, 132), dark=c(40, 48, 58), mortar=c(20, 26, 34),
                  top=c(40, 150, 140), top_light=c(110, 255, 220), drip=c(30, 110, 104), pattern='brick',
                  ledge='slab', wood=c(84, 96, 108), wood_light=c(130, 146, 160), wood_dark=c(46, 54, 64),
                  wall=c(22, 28, 36), wall_light=c(32, 40, 50), wall_mortar=c(12, 16, 22)),
    # Colmeia de Plasma (fase da Vespa): cera âmbar e favos.
    'hive': dict(base=c(150, 96, 30), light=c(200, 140, 50), dark=c(90, 54, 18), mortar=c(48, 26, 8),
                 top=c(230, 170, 60), top_light=c(255, 230, 140), drip=c(200, 130, 40), pattern='rock',
                 ledge='sinew', wood=c(170, 110, 40), wood_light=c(230, 170, 80), wood_dark=c(100, 60, 20),
                 accent=c(255, 200, 80), wall=c(44, 26, 12), wall_light=c(64, 40, 18), wall_mortar=c(24, 12, 4)),
}


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
    pattern = b['pattern']
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
        tone = c(40, 6, 10) if rng.random() < 0.3 else c(0, 0, 0)
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
    to_image(grime(wall_texture(b, rng), b, rng, 26)).save(os.path.join(OUT, f'{name}_wall.png'))


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, b in BIOMES.items():
        build(name, b)
    print(f'{len(BIOMES)} tilesets gerados em art/tiles/')


if __name__ == '__main__':
    main()
