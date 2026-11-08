#!/usr/bin/env python3
"""Esqueleto e poses da Elyra: ângulos por articulação (radianos; "para a
frente" positivo) para cada animação e golpe de espada. tools/hd_frames.py usa
isto para saber onde fica cada parte do corpo e desenha cada quadro inteiro.
"""
import math

# Esqueleto (unidades; 4 unidades = 1 px do jogo). Origem nos pés.
HIP = (0.0, -92.0)
NECK = (2.0, -60.0)
SHOULDER_B = (-12.0, -50.0)
SHOULDER_F = (12.0, -50.0)
HIP_B = (-4.0, 0.0)
HIP_F = (5.0, 0.0)
THIGH = 34.0
SHIN = 34.0
UPPER_ARM = 24.0
HAND = 24.0


def pose(anim, t):
    """Pose alvo no instante t (segundos) da animação."""
    p = dict(lean=0.05, bob=0.0, thf=0.28, knf=0.05, thb=-0.2, knb=0.05, ftf=0.0, ftb=0.0,
             armb=0.08, elb=0.2, armf=0.35, cf=0.9, sw=1.7, spin=0.0)
    if anim == 'idle':
        breath = math.sin(t * 2.2)
        p.update(bob=-1.2 + breath * 1.2, armb=0.08 + breath * 0.03, armf=0.35 + breath * 0.03)
    elif anim == 'run':
        ph = t * 9.5
        def leg(phase):
            thigh = 0.18 + 0.9 * math.sin(phase)
            knee = 0.15 + 1.35 * max(0.0, math.cos(phase + 0.75))
            foot = 0.55 if thigh < -0.3 else (-0.15 if thigh > 0.6 else 0.0)
            return thigh, knee, foot
        thf, knf, ftf = leg(ph)
        thb, knb, ftb = leg(ph + math.pi)
        p.update(lean=0.16, bob=-5.0 * abs(math.cos(ph)), thf=thf, knf=knf, ftf=ftf, thb=thb, knb=knb, ftb=ftb,
                 armb=-0.55 * math.sin(ph), elb=0.9, armf=0.1 + 0.5 * math.sin(ph), cf=0.5, sw=-1.35)
    elif anim == 'jump':
        p.update(lean=0.08, thf=1.15, knf=1.7, thb=0.25, knb=1.35, ftb=0.6, armb=-0.6, elb=0.6, armf=-0.4, cf=0.6,
                 sw=-1.2)
    elif anim == 'fall':
        sway = math.sin(t * 6.0)
        p.update(lean=0.0, thf=0.45, knf=0.55, thb=-0.25, knb=0.35, ftb=0.45, armb=-1.2 + sway * 0.1, elb=0.4,
                 armf=0.6, cf=0.4, sw=1.9)
    elif anim == 'spin':
        p.update(lean=0.45, thf=2.0, knf=2.55, thb=1.75, knb=2.45, ftf=0.5, ftb=0.6, armb=0.9, elb=1.6, armf=0.6,
                 cf=1.2, sw=-1.4, spin=t * 15.0)
    elif anim == 'dash':
        p.update(lean=0.42, bob=8.0, thf=1.05, knf=1.35, thb=-0.95, knb=0.2, ftb=0.6, armb=-0.5, elb=0.5, armf=-0.7,
                 cf=0.3, sw=-1.3)
    elif anim == 'wall':
        p.update(lean=-0.12, thf=0.85, knf=1.5, thb=0.15, knb=1.0, ftb=0.4, armb=-2.2, elb=-0.4, armf=0.5, cf=0.8,
                 sw=1.6)
    elif anim == 'hurt':
        p.update(lean=-0.38, bob=-2.0, thf=0.5, knf=0.6, thb=-0.5, knb=0.35, armb=-2.0, elb=0.5, armf=-0.4, cf=0.3,
                 sw=0.6)
    return p


# Golpes de espada: braço da frente de [início] até [fim] (armf, cf, sw).
ATTACK_TIME = 0.26
SWINGS = {
    0: ((2.7, 0.2, 0.4), (0.25, 0.1, 1.0)),   # de cima para baixo
    1: ((-0.2, 0.3, 1.2), (2.4, 0.4, 0.6)),   # de baixo para cima
    2: ((2.9, 0.1, 0.3), (0.15, 0.05, 1.1)),  # golpe carregado
}


def attack_pose(p, kind, t):
    """Sobrepõe o golpe de espada (t = segundos desde o início)."""
    start, end = SWINGS[kind]
    if t < 0.04:
        arm = start
    else:
        u = min(1.0, (t - 0.04) / 0.08)
        u = 1.0 - (1.0 - u) ** 3
        arm = tuple(a + (b - a) * u for a, b in zip(start, end))
    lean = p['lean'] + (0.12 if kind != 1 else -0.05)
    return dict(p, armf=arm[0], cf=arm[1], sw=arm[2], lean=lean)


# --- Cinemática (transformações 2D simples) -----------------------------------------

def mat(rot, pos):
    c, s = math.cos(rot), math.sin(rot)
    return (c, -s, s, c, pos[0], pos[1])


def mul(a, b):
    return (a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3],
            a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
            a[0] * b[4] + a[1] * b[5] + a[4], a[2] * b[4] + a[3] * b[5] + a[5])


def apply(m, pt):
    return (m[0] * pt[0] + m[1] * pt[1] + m[4], m[2] * pt[0] + m[3] * pt[1] + m[5])


def skeleton(p, grounded):
    """Transformações de cada peça (relativas aos pés), na ordem de desenho."""
    root = mat(0, (0, 0))
    hip = mul(root, mat(0, (HIP[0] + p['lean'] * 6, HIP[1] - p['bob'])))
    if p['spin']:
        center = (HIP[0], HIP[1] + 10)
        hip = mul(mat(p['spin'], center), mul(mat(0, (-center[0], -center[1])), hip))
    torso = mul(hip, mat(p['lean'], (0, 0)))
    parts = []

    def leg(side):
        th, kn, ft = (p['thf'], p['knf'], p['ftf']) if side == 'f' else (p['thb'], p['knb'], p['ftb'])
        thigh = mul(hip, mat(-th, HIP_F if side == 'f' else HIP_B))
        shin = mul(thigh, mat(kn, (0, THIGH)))
        foot = mul(shin, mat(ft - (-th + kn) - (p['spin'] and 0), (0, SHIN)))
        return thigh, shin, foot

    tb, sb, fb = leg('b')
    tf, sf, ff = leg('f')
    up_b = mul(torso, mat(-p['armb'], SHOULDER_B))
    fore_b = mul(up_b, mat(-p['elb'], (0, UPPER_ARM)))
    up_f = mul(torso, mat(-p['armf'], SHOULDER_F))
    fore_f = mul(up_f, mat(-p['cf'], (0, UPPER_ARM)))
    sword = mul(fore_f, mat(-p['sw'], (0, HAND)))
    parts = [('upper_arm', up_b, True), ('forearm', fore_b, True), ('shoulder', mul(torso, mat(0, SHOULDER_B)), True),
             ('thigh', tb, True), ('shin', sb, True), ('foot', fb, True),
             ('torso', torso, False),
             ('thigh', tf, False), ('shin', sf, False), ('foot', ff, False), ('skirt', torso, False),
             ('head', mul(torso, mat(0, NECK)), False),
             ('upper_arm', up_f, False), ('sword', sword, False), ('forearm', fore_f, False),
             ('shoulder', mul(torso, mat(0, SHOULDER_F)), False)]
    shift = 0.0
    if grounded:
        sole = max(apply(m, pt)[1] for m in (fb, ff) for pt in ((-10, 24), (28, 24)))
        shift = -sole
    return parts, shift, sword
