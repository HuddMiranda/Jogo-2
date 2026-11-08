#!/usr/bin/env python3
"""VEX-9 em pixel art de console, montada por peças (usado por generate_sprites.py).

As peças rígidas (capacete, ombreiras, tronco, quadril, pés, braço-canhão) são
desenhadas à mão, letra por letra (uma letra = um pixel, paleta em PALETTE). Os
membros (coxa, canela, braços) são traçados em cada quadro na posição da pose,
com o mesmo sombreado em faixas: claro do lado da luz, meio-tom e escuro do
outro lado. Cada peça ganha um contorno escuro por cima da peça de trás,
como na pixel art de 16 bits. Tudo virado para a direita.

Letras: A/a/d armadura (luz/meio/sombra), G/g dourado, B/b traje, V/v/w visor,
W branco, C/c gema, O contorno.
"""
import math

from PIL import Image

# Paleta "Marfim".
PALETTE = {
    'O': '1a1410', 'A': 'ffffff', 'a': 'e4d8bc', 'd': '9a8a66', 'G': 'ffe08a', 'g': 'c8902e',
    'B': '3a3546', 'b': '1a1722', 'V': 'd0e6ff', 'v': '3a8aff', 'w': '0a2a8a', 'W': 'ffffff',
    'C': 'd0e0ff', 'c': '3a6aff',
}
# Peças na sombra (atrás do corpo) usam tons mais escuros.
DARKER = {'A': 'a', 'a': 'd', 'd': 'd', 'G': 'g', 'g': 'g', 'B': 'b', 'b': 'b'}

# --- Peças rígidas: copiadas do desenho aprovado (coordenadas da grade dele) ----
# Cada peça: ({linha: (coluna, texto)}, pivô). O pivô é a articulação onde ela
# se prende; em cada quadro, o pivô vai para a posição da pose.

HELMET = ({0: (11, "AGa"), 1: (9, "AAAGad"), 2: (8, "AAagaaad"), 3: (8, "Aaagaaaad"), 4: (8, "aaaAddddddA"),
           5: (8, "aGgadVWVVvw"), 6: (8, "aggaddvvwwd"), 7: (8, "daaaAAaaad"), 8: (9, "daaOaOaad"),
           9: (10, "dddddd")}, (12, 10))
FIN = ({2: (7, "dd"), 3: (6, "ddd"), 4: (6, "dd"), 5: (7, "d")}, (12, 10))
NECK = ({9: (11, "bBb"), 10: (11, "bb")}, (12, 10))
BACK_PAD = ({9: (6, "ddd"), 10: (5, "daaad"), 11: (4, "daaaad"), 12: (4, "daaadd"), 13: (5, "dggd")}, (8, 13))
FRONT_PAD = ({8: (14, "AAAa"), 9: (13, "AAAAaaa"), 10: (13, "AAAaaaad"), 11: (13, "AAaaaaad"), 12: (13, "Aaaaaadd"),
              13: (13, "aaaaaddd"), 14: (14, "gggggd")}, (17, 14))
CHEST = ({11: (10, "AAaa"), 12: (10, "AAaaa"), 13: (10, "AACca"), 14: (10, "Aaccad"), 15: (10, "aaaadd"),
          16: (10, "dddddd")}, (12, 24))
BELLY = ({17: (11, "BBbb"), 18: (11, "BBbb"), 19: (11, "Bbbb"), 20: (11, "Bbbb")}, (12, 24))
HIPS = ({21: (10, "BBBbb"), 22: (9, "gGGGggg"), 23: (10, "daaad")}, (12, 24))
KNEE = ({31: (16, "AAad"), 32: (16, "AGgd"), 33: (16, "dddd")}, (17, 32))
FOOT_FLAT = ({40: (18, "AAa"), 41: (17, "AAaaad"), 42: (17, "AAaaaaad"), 43: (17, "dddddddddd")}, (19, 39))
FOOT_TOE = ({40: (18, "AAa"), 41: (18, "AAad"), 42: (18, "Aaad"), 43: (18, "aaad"), 44: (19, "ddd"), 45: (20, "dd")},
            (19, 39))
CANNON_DOWN = ({14: (16, "bBb"), 15: (16, "bBb"), 16: (16, "bBb"), 17: (16, "bbb"), 18: (15, "AAaad"),
                19: (14, "AAaaad"), 20: (14, "AGGggd"), 21: (14, "AAaaad"), 22: (14, "AAaaad"), 23: (14, "Aaaaad"),
                24: (14, "Aaaaad"), 25: (14, "ggggdd"), 26: (15, "dCcd")}, (17, 14))
CANNON_FORWARD = ({14: (16, "bBb"), 15: (16, "bbBAAAAAAaad"), 16: (16, "AAAGAAaaaaad"), 17: (15, "AAAAGaaaaaaadC"),
                   18: (15, "aaaagaaaaadddc"), 19: (16, "dddgdddddddd")}, (17, 14))


def place(piece, at, darker=False):
    """Camada de uma peça com o pivô na posição `at`."""
    rows, (px, py) = piece
    layer = {}
    for y, (x, text) in rows.items():
        for i, ch in enumerate(text):
            if ch not in '. ':
                if darker:
                    ch = DARKER.get(ch, ch)
                layer[(round(at[0]) + x + i - px, round(at[1]) + y - py)] = ch
    return layer


def _unused_lines_to_layer(patch, at, darker=False, flip_rows=False):
    rows, ax, ay = patch
    layer = {}
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch not in '. ':
                if darker:
                    ch = DARKER.get(ch, ch)
                layer[(at[0] - ax + i, at[1] - ay + j)] = ch
    return layer


def segment(a, b, width, darker=False, suit=False):
    """Membro traçado entre dois pontos, com sombreado em faixas."""
    layer = {}
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length = max(1e-3, math.hypot(dx, dy))
    nx, ny = -dy / length, dx / length
    if nx * -0.6 + ny * -0.8 < 0:  # normal apontando para a luz (cima/esquerda)
        nx, ny = -nx, -ny
    r = width / 2.0
    for y in range(int(min(ay, by) - r - 1), int(max(ay, by) + r + 2)):
        for x in range(int(min(ax, bx) - r - 1), int(max(ax, bx) + r + 2)):
            px, py = x + 0.5, y + 0.5
            t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (length * length)))
            cx, cy = ax + dx * t, ay + dy * t
            if math.hypot(px - cx, py - cy) <= r:
                side = ((px - cx) * nx + (py - cy) * ny) / max(r, 0.5)
                if suit:
                    ch = 'B' if side > 0.2 else 'b'
                else:
                    ch = 'A' if side > 0.35 else ('a' if side > -0.45 else 'd')
                if darker:
                    ch = DARKER.get(ch, ch)
                layer[(x, y)] = ch
    return layer


class Frame:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = {}

    def part(self, layer):
        """Contorna a peça por cima do que já existe e a pinta."""
        for (x, y) in layer:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in layer and n in self.g:
                    self.g[n] = 'O'
        self.g.update(layer)

    def image(self):
        img = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        out = dict(self.g)
        for (x, y), ch in self.g.items():
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in self.g and ch != 'O':
                    out[n] = 'O'
        for (x, y), ch in out.items():
            if 0 <= x < self.w and 0 <= y < self.h:
                c = PALETTE[ch]
                img.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
        return img


# --- Poses ------------------------------------------------------------------------

def pose(anim, t):
    """Ângulos (radianos a partir da vertical, + = para a frente) e deslocamentos."""
    s = math.sin(t * math.tau)
    p = dict(bob=0, lean=0, th_f=0.32, kn_f=0.0, th_b=-0.22, kn_b=0.0, foot_b='flat', foot_f='flat',
             arm_b=0.05, el_b=-0.15)
    if anim == 'idle':
        p['bob'] = 1 if t >= 0.5 else 0
    elif anim == 'run':
        p.update(bob=round(abs(s) * 1.5), lean=1, th_f=0.75 * s, th_b=-0.75 * s,
                 kn_f=max(0.0, -s) * 1.4 + 0.15, kn_b=max(0.0, s) * 1.4 + 0.15,
                 arm_b=0.7 * s, el_b=-0.9)
        p['foot_f'] = 'toe' if s < -0.4 else 'flat'
        p['foot_b'] = 'toe' if s > 0.4 else 'flat'
    elif anim == 'jump':
        p.update(bob=-2, th_f=1.1, kn_f=1.6, th_b=0.2, kn_b=1.3, foot_b='toe', arm_b=-0.8, el_b=-0.6)
    elif anim == 'fall':
        p.update(bob=-1, th_f=0.45, kn_f=0.5, th_b=-0.2, kn_b=0.4, foot_b='toe', arm_b=-1.4 + 0.2 * s, el_b=-0.3)
    elif anim == 'dash':
        p.update(bob=3, lean=3, th_f=1.2, kn_f=1.5, th_b=-1.05, kn_b=0.25, foot_b='toe', arm_b=-0.6, el_b=-0.4)
    elif anim == 'wall':
        p.update(lean=-1, th_f=0.8, kn_f=1.4, th_b=0.1, kn_b=0.9, foot_b='toe', arm_b=-2.3, el_b=0.3)
    elif anim == 'hurt':
        p.update(bob=-1, lean=-2, th_f=0.5, kn_f=0.6, th_b=-0.5, kn_b=0.3, arm_b=-2.2, el_b=-0.3)
    return p


def leg_points(hip, thigh, knee_bend):
    knee = (hip[0] + math.sin(thigh) * 7.0, hip[1] + math.cos(thigh) * 7.0)
    a = thigh - knee_bend
    ankle = (knee[0] + math.sin(a) * 8.0, knee[1] + math.cos(a) * 8.0)
    return knee, ankle


def draw(anim, t, w=64, h=64, origin=(32, 60)):
    """Desenha um quadro do corpo (sem o braço-canhão). Retorna (Frame, ombro da frente)."""
    p = pose(anim, t)
    f = Frame(w, h)
    # Quadril: no parado, a sola fica na linha do chão (origem).
    hip = (origin[0], origin[1] - 20 - p['bob'])
    legs = {}
    for side, th, kn in (('b', p['th_b'], p['kn_b']), ('f', p['th_f'], p['kn_f'])):
        joint = (hip[0] + (-1 if side == 'b' else 3), hip[1])
        legs[side] = (joint,) + leg_points(joint, th, kn)
    if anim in ('idle', 'run', 'dash', 'hurt'):
        lowest = max(legs['b'][2][1], legs['f'][2][1])
        shift = (origin[1] - 5) - lowest
        legs = {k: tuple((x, y + shift) for x, y in v) for k, v in legs.items()}
        hip = (hip[0], hip[1] + shift)
    top = (hip[0] + p['lean'], hip[1])
    shoulder_b = (top[0] - 4, top[1] - 11)
    shoulder_f = (top[0] + 5, top[1] - 10)
    neck = (top[0], top[1] - 14)
    # Braço de trás (na sombra): braço, cotovelo, antebraço, mão; ombreira.
    elbow_b = (shoulder_b[0] + math.sin(p['arm_b']) * 4.5, shoulder_b[1] + math.cos(p['arm_b']) * 4.5)
    a2 = p['arm_b'] + p['el_b']
    hand_b = (elbow_b[0] + math.sin(a2) * 5.0, elbow_b[1] + math.cos(a2) * 5.0)
    f.part(segment(shoulder_b, elbow_b, 2.6, darker=True, suit=True))
    f.part(segment(elbow_b, hand_b, 3.6, darker=True))
    f.part({(round(hand_b[0]) + dx, round(hand_b[1]) + dy): 'b' for dx in (-1, 0) for dy in (0, 1)})
    f.part(place(BACK_PAD, shoulder_b, darker=True))
    # Perna de trás, quadril, perna da frente.
    for side in ('b', 'f'):
        joint, knee, ankle = legs[side]
        dark = side == 'b'
        if side == 'f':
            f.part(place(HIPS, hip))
        f.part(segment(joint, knee, 4.0, darker=dark))
        f.part(segment(knee, ankle, 3.6, darker=dark))
        f.part(place(KNEE, knee, darker=dark))
        foot = FOOT_TOE if p['foot_' + side] == 'toe' else FOOT_FLAT
        f.part(place(foot, ankle, darker=dark))
    # Tronco, pescoço e capacete.
    f.part(place(BELLY, (top[0] - (p['lean'] > 1), top[1])))
    f.part(place(CHEST, top))
    f.part(place(NECK, neck))
    f.part(place(FIN, neck))
    f.part(place(HELMET, neck))
    return f, (round(shoulder_f[0]), round(shoulder_f[1]))


def cannon_layers(kind):
    """Braço-canhão com a ombreira da frente, pivô (ombro) no centro do quadro."""
    f = Frame(64, 64)
    center = (32, 32)
    f.part(place(CANNON_DOWN if kind == 0 else CANNON_FORWARD, center))
    f.part(place(FRONT_PAD, center))
    if kind == 1:
        muzzle = (center[0] + 13, center[1] + 3)
    else:
        muzzle = (center[0] - 1, center[1] + 12)
    return f, muzzle
