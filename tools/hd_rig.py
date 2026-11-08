#!/usr/bin/env python3
"""Esqueleto e poses da Elyra HD (espelho em Python de scenes/player/hd_hero.gd),
usado para gerar prévias (GIF) fora do Godot.

    python tools/hd_rig.py run saida.gif

As poses são ângulos por articulação (radianos; "para a frente" positivo) que
o jogo interpola suavemente quadro a quadro. Mantenha este arquivo e
hd_hero.gd iguais ao mexer nas poses.
"""
import math
import os
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
R = 2  # pixels por unidade nos PNG
PIVOTS = {}

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
MUZZLE = (0.0, 41.0)


def pose(anim, t):
    """Pose alvo no instante t (segundos) da animação."""
    p = dict(lean=0.05, bob=0.0, thf=0.28, knf=0.05, thb=-0.2, knb=0.05, ftf=0.0, ftb=0.0,
             armb=0.08, elb=0.2, armf=0.1, cf=0.05, spin=0.0)
    if anim == 'idle':
        breath = math.sin(t * 2.2)
        p.update(bob=-1.2 + breath * 1.2, armb=0.08 + breath * 0.03, armf=0.1 + breath * 0.03)
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
                 armb=-0.55 * math.sin(ph), elb=0.9)
    elif anim == 'jump':
        p.update(lean=0.08, thf=1.15, knf=1.7, thb=0.25, knb=1.35, ftb=0.6, armb=-0.6, elb=0.6)
    elif anim == 'fall':
        sway = math.sin(t * 6.0)
        p.update(lean=0.0, thf=0.45, knf=0.55, thb=-0.25, knb=0.35, ftb=0.45, armb=-1.2 + sway * 0.1, elb=0.4)
    elif anim == 'spin':
        p.update(lean=0.45, thf=2.0, knf=2.55, thb=1.75, knb=2.45, ftf=0.5, ftb=0.6, armb=0.9, elb=1.6, armf=0.6,
                 cf=0.9, spin=t * 15.0)
    elif anim == 'dash':
        p.update(lean=0.42, bob=8.0, thf=1.05, knf=1.35, thb=-0.95, knb=0.2, ftb=0.6, armb=-0.5, elb=0.5)
    elif anim == 'wall':
        p.update(lean=-0.12, thf=0.85, knf=1.5, thb=0.15, knb=1.0, ftb=0.4, armb=-2.2, elb=-0.4)
    elif anim == 'hurt':
        p.update(lean=-0.38, bob=-2.0, thf=0.5, knf=0.6, thb=-0.5, knb=0.35, armb=-2.0, elb=0.5, armf=-0.4)
    return p


def aim_pose(p, shooting):
    """Braço-canhão: apontado para a frente (atirando/correndo) ou solto."""
    if shooting:
        p = dict(p, armf=0.72 + p['lean'], cf=0.85)
    return p


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
    cannon = mul(up_f, mat(-p['cf'], (0, UPPER_ARM)))
    parts = [('upper_arm', up_b, True), ('forearm', fore_b, True), ('pauldron', mul(torso, mat(0, SHOULDER_B)), True),
             ('thigh', tb, True), ('shin', sb, True), ('foot', fb, True),
             ('torso', torso, False),
             ('thigh', tf, False), ('shin', sf, False), ('foot', ff, False),
             ('helmet', mul(torso, mat(0, NECK)), False),
             ('upper_arm', up_f, False), ('cannon', cannon, False), ('pauldron', mul(torso, mat(0, SHOULDER_F)), False)]
    shift = 0.0
    if grounded:
        sole = max(apply(m, pt)[1] for m in (fb, ff) for pt in ((-10, 24), (28, 24)))
        shift = -sole
    return parts, shift, cannon


def load_pivots():
    if not PIVOTS:
        for line in open(os.path.join(ROOT, 'scripts', 'hd_parts.gd')):
            if '"pivot"' in line:
                name = line.split('"')[1]
                nums = line.split('Vector2(')[1].split(')')[0].split(',')
                PIVOTS[name] = (float(nums[0]), float(nums[1]))


def render(anim, t, shooting=False, grounded=None, size=(300, 440), origin=(120, 420)):
    load_pivots()
    if grounded is None:
        grounded = anim in ('idle', 'run', 'dash', 'hurt')
    return render_pose(aim_pose(pose(anim, t), shooting), grounded, size, origin)


def render_pose(p, grounded, size=(300, 440), origin=(120, 420)):
    load_pivots()
    parts, shift, _ = skeleton(p, grounded)
    out = Image.new('RGBA', size, (0, 0, 0, 0))
    for name, m, back in parts:
        img = Image.open(os.path.join(ROOT, 'art', 'hd', 'vex_parts', name + '.png')).convert('RGBA')
        if back:
            px = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b, a = px[x, y]
                    px[x, y] = (int(r * 0.72), int(g * 0.7), int(b * 0.78), a)
        rot = math.atan2(m[2], m[0])
        pivot = PIVOTS[name]
        rotated = img.rotate(-math.degrees(rot), resample=Image.BICUBIC, expand=True)
        # Posição do pivô depois de girar com expand: recalcula pelo centro.
        cx, cy = img.width / 2, img.height / 2
        dx, dy = pivot[0] - cx, pivot[1] - cy
        c, s = math.cos(rot), math.sin(rot)
        new_pivot = (rotated.width / 2 + dx * c - dy * s, rotated.height / 2 + dx * s + dy * c)
        wx, wy = m[4] * R + origin[0], (m[5] + shift) * R + origin[1]
        out.alpha_composite(rotated, (int(round(wx - new_pivot[0])), int(round(wy - new_pivot[1]))))
    return out


if __name__ == '__main__':
    anim = sys.argv[1] if len(sys.argv) > 1 else 'run'
    path = sys.argv[2] if len(sys.argv) > 2 else 'preview.gif'
    shooting = anim in ('run', 'dash') or (len(sys.argv) > 3 and sys.argv[3] == 'shoot')
    frames = []
    for i in range(36):
        f = render(anim, i / 30.0, shooting)
        bg = Image.new('RGBA', f.size, (24, 26, 36, 255))
        bg.alpha_composite(f)
        frames.append(bg.convert('P', palette=Image.ADAPTIVE))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=33, loop=0, disposal=2)
