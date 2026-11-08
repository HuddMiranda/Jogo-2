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
        # Corrida de exploradora: passada longa, joelho da frente subindo alto,
        # perna de trás esticada empurrando com a ponta do pé, tronco inclinado
        # e um quique a cada passo (mais alto quando as pernas se cruzam).
        ph = t * math.tau
        def leg(phase):
            sn, cs = math.sin(phase), math.cos(phase)
            thigh = 0.2 + 1.0 * sn
            knee = 0.15 + 1.5 * max(0.0, math.cos(phase + 0.7))
            return thigh, knee, ('toe' if thigh < -0.35 else 'flat')
        th_f, kn_f, foot_f = leg(ph)
        th_b, kn_b, foot_b = leg(ph + math.pi)
        p.update(bob=round(2 * abs(math.cos(ph))), lean=2, th_f=th_f, kn_f=kn_f, th_b=th_b, kn_b=kn_b,
                 foot_f=foot_f, foot_b=foot_b, arm_b=-0.6 * math.sin(ph), el_b=-1.0)
    elif anim == 'spin':
        # Encolhida para a cambalhota (o quadro é girado depois).
        p.update(bob=-2, th_f=2.1, kn_f=2.7, th_b=1.8, kn_b=2.5, foot_b='toe', foot_f='toe', arm_b=1.2, el_b=1.2)
    elif anim == 'jump':
        p.update(bob=-2, th_f=1.1, kn_f=1.6, th_b=0.2, kn_b=1.3, foot_b='toe', arm_b=-0.8, el_b=-0.6)
    elif anim == 'fall':
        p.update(bob=-1, th_f=0.45, kn_f=0.5, th_b=-0.2, kn_b=0.4, foot_b='toe', arm_b=-1.4 + 0.2 * s, el_b=-0.3)
    elif anim == 'dash':
        p.update(bob=3, lean=2, th_f=1.2, kn_f=1.5, th_b=-1.05, kn_b=0.25, foot_b='toe', arm_b=-0.6, el_b=-0.4)
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


BACK_ARM = [({13: (7, "ddd"), 14: (7, "ddd"), 15: (7, "ddd"), 16: (7, "bbd")}, (12, 24)),
            ({17: (7, "bbb"), 18: (7, "bbb")}, (12, 24)),
            ({19: (6, "daad"), 20: (6, "daad"), 21: (6, "daad"), 22: (6, "dddd")}, (12, 24)),
            ({23: (7, "bbb"), 24: (7, "bbb")}, (12, 24))]


def upper_block():
    """Tronco inteiro (como no desenho aprovado) numa peça rígida só, com o
    pivô no centro do quadril. Contornos internos já incluídos."""
    f = Frame(64, 64)
    at = (32, 40)
    for piece in BACK_ARM:
        f.part(place(piece, at))
    f.part(place(BACK_PAD, (at[0] - 4, at[1] - 11)))
    f.part(place(HIPS, at))
    f.part(place(BELLY, at))
    f.part(place(CHEST, at))
    f.part(place(NECK, (at[0], at[1] - 14)))
    f.part(place(FIN, (at[0], at[1] - 14)))
    f.part(place(HELMET, (at[0], at[1] - 14)))
    return {(x - at[0], y - at[1]): ch for (x, y), ch in f.g.items()}


_UPPER = None


def leg_layer(joint, knee, ankle, foot, dark):
    """Perna inteira numa peça só: coxa, canela, joelheira e pé, sem
    contornos internos (o joelho é marcado pela joelheira)."""
    layer = {}
    layer.update(segment((joint[0], joint[1] - 1), knee, 4.0, darker=dark))
    layer.update(segment(knee, ankle, 3.6, darker=dark))
    layer.update(place(KNEE, knee, darker=dark))
    layer.update(place(foot, (ankle[0], ankle[1] - 0.5), darker=dark))
    return layer


def draw(anim, t, w=64, h=64, origin=(32, 60)):
    """Desenha um quadro do corpo (sem o braço-canhão). Retorna (Frame, ombro da frente)."""
    global _UPPER
    if _UPPER is None:
        _UPPER = upper_block()
    p = pose(anim, t)
    f = Frame(w, h)
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
    top = (round(hip[0] + p['lean'] * 0.5), round(hip[1]))
    joint, knee, ankle = legs['b']
    f.part(leg_layer(joint, knee, ankle, FOOT_TOE if p['foot_b'] == 'toe' else FOOT_FLAT, True))
    f.part({(x + top[0], y + top[1]): ch for (x, y), ch in _UPPER.items()})
    joint, knee, ankle = legs['f']
    f.part(leg_layer(joint, knee, ankle, FOOT_TOE if p['foot_f'] == 'toe' else FOOT_FLAT, False))
    return f, (top[0] + 5, top[1] - 10)


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
