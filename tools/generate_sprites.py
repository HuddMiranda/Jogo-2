#!/usr/bin/env python3
"""Gera os sprites em pixel art (art/sprites/*.png) e os dados das animações
(scripts/sprite_data.gd).

    python tools/generate_sprites.py          (precisa de: pip install pillow numpy)

Cada folha tem uma animação por linha e um quadro por coluna; a origem de cada
quadro (os pés, ou o centro nos voadores) fica em `origin`. O herói tem ainda a
linha "arm": o braço da frente solto (0) e virado canhão (1), desenhado por cima
do corpo no ombro de cada quadro (`shoulders`); `muzzle` é a boca do canhão.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pixel import Canvas, rgb, shade, ang, add  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'art', 'sprites')

from PIL import Image  # noqa: E402

# --- Herói: caçador de armadura simbionte ---------------------------------------

HERO = dict(armor=rgb('8e1a2a'), metal=rgb('c9a24a'), trim=rgb('e8c46a'), suit=rgb('17151d'),
            glow=rgb('6af0ff'), gem=rgb('3ae0ff'), skin=rgb('e6c2a6'), eye=rgb('1a6a8a'), hair=rgb('d8dce6'))


def hero_pose(anim, t):
    s, c = math.sin(t * math.tau), math.cos(t * math.tau)
    p = dict(bob=0.0, lean=0.05, thigh_f=0.1, thigh_b=-0.1, knee_f=0.15, knee_b=0.15, arm_b=-0.15, elbow_b=-0.5,
             head=0.0)
    if anim == 'idle':
        p.update(bob=0.5 + 0.5 * s)
    elif anim == 'run':
        p.update(bob=abs(s) * 2.0, lean=0.28, thigh_f=0.85 * s, thigh_b=-0.85 * s,
                 knee_f=0.3 + max(0.0, -s) * 1.5, knee_b=0.3 + max(0.0, s) * 1.5, arm_b=0.7 * s, elbow_b=-1.1)
    elif anim == 'jump':
        p.update(bob=-1.0, lean=0.12, thigh_f=1.2, thigh_b=0.1, knee_f=1.7, knee_b=0.9, arm_b=-1.2, elbow_b=-0.6)
    elif anim == 'fall':
        p.update(bob=-1.0, lean=0.0, thigh_f=0.35, thigh_b=-0.25, knee_f=0.5, knee_b=0.2, arm_b=-1.6 + 0.2 * s,
                 elbow_b=-0.4)
    elif anim == 'dash':
        p.update(bob=-4.0, lean=0.6, thigh_f=1.1, thigh_b=-1.0, knee_f=1.6, knee_b=0.2, arm_b=-0.9, elbow_b=-0.2,
                 head=-0.25)
    elif anim == 'wall':
        # De costas para a parede (à esquerda), mão de trás apoiada nela.
        p.update(lean=-0.12, thigh_f=0.7, thigh_b=-0.2, knee_f=1.3, knee_b=0.6, arm_b=-2.2, elbow_b=0.3)
    elif anim == 'hurt':
        p.update(bob=-1.0, lean=-0.4, thigh_f=0.4, thigh_b=-0.5, knee_f=0.5, knee_b=0.3, arm_b=-2.4, elbow_b=-0.3,
                 head=-0.35)
    return p


def hero(cv, anim, t):
    """VEX-9: guerreira esguia e adulta. Cabeça pequena, corpo e pernas longos,
    armadura justa, capacete afilado de crista longa e cabelo comprido."""
    p = hero_pose(anim, t)
    col = HERO
    hip = (0.0, -23.0 - p['bob'] + 4.0 * (1 - math.cos(min(p['knee_f'], p['knee_b']) * 0.5)))
    lean = p['lean']
    neck = add(hip, (math.sin(lean) * 13.0, -math.cos(lean) * 13.0))
    sh_f = add(neck, (2.0, 2.0))
    sh_b = add(neck, (-2.0, 1.5))
    head = add(neck, (math.sin(lean + p['head']) * 5.0 + 0.5, -math.cos(lean + p['head']) * 5.0))
    wind = {'run': 1.0, 'dash': 1.6, 'jump': 0.6, 'fall': -0.8}.get(anim, 0.2)
    sway = math.sin(t * math.tau)

    def leg(a, k, back):
        dim = -0.32 if back else 0.0
        knee = add(hip, ang(a, 10.5))
        foot = add(knee, ang(a - k, 11.0))
        cv.limb(hip, knee, 4.2, shade(col['suit'], dim))
        # Caneleira justa e bota afilada; joelheira pontuda.
        cv.limb(add(knee, ang(a - k, 1.5)), add(foot, (0, -1.5)), 5.6, shade(col['armor'], dim))
        cv.poly([add(foot, (-3, -3)), add(foot, (4, -3)), add(foot, (7.5, 0.5)), add(foot, (-3.5, 0.5))],
                shade(col['armor'], dim - 0.08))
        cv.poly([add(knee, (-2.5, -1)), add(knee, (3.5, -2.5)), add(knee, (2.5, 2.5)), add(knee, (-2, 2))],
                shade(col['metal'], dim))
        cv.pixel(add(foot, (2, -1)), shade(col['trim'], dim))

    def back_arm():
        dim = -0.32
        el = add(sh_b, ang(p['arm_b'], 7.5))
        hand = add(el, ang(p['arm_b'] + p['elbow_b'], 7.0))
        cv.limb(sh_b, el, 3.4, shade(col['suit'], dim))
        cv.limb(el, add(el, ang(p['arm_b'] + p['elbow_b'], 5.5)), 4.6, shade(col['armor'], dim))
        cv.ellipse(hand, 2.2, 2.2, shade(col['suit'], dim + 0.1))
        cv.ellipse(add(sh_b, (0, -0.5)), 3.4, 3.0, shade(col['armor'], dim))

    # Cabelo longo (atrás de tudo), esvoaçando com o movimento.
    base = add(head, (-3.5, -1.5))
    prev = base
    for k in range(6):
        f = k + 1
        nxt = add(prev, (-2.6 - wind * 1.2, 2.6 - wind * 0.9 + sway * 0.35 * f * (0.4 if anim == 'idle' else 1.0)))
        cv.limb(prev, nxt, 5.2 - k * 0.7, col['hair'])
        prev = nxt
    back_arm()
    leg(p['thigh_b'], p['knee_b'], True)
    # Tronco esguio: traje preto, peitoral anguloso, cinto com gema.
    cv.limb(hip, add(neck, (0, 2)), 5.0, col['suit'])
    leg(p['thigh_f'], p['knee_f'], False)
    cv.poly([add(hip, (-4.5, -1)), add(hip, (4.5, -1)), add(hip, (4, 2.5)), add(hip, (0, 4)), add(hip, (-4, 2.5))],
            col['armor'])
    cv.limb(add(hip, (-4.5, -1.2)), add(hip, (4.5, -1.2)), 1.6, col['trim'], outline=False)
    cv.poly([add(neck, (-4.5, 0.5)), add(neck, (5.5, 0)), add(neck, (5.0, 6.5)), add(neck, (1.5, 9.0)),
             add(neck, (-3.5, 7.5))], col['armor'])
    cv.limb(add(neck, (-1, 1)), add(neck, (2.5, 6.5)), 1.4, col['metal'], outline=False)
    cv.ellipse(add(neck, (2.5, 3.5)), 1.6, 1.6, col['gem'], glow=True)
    # Capacete afilado: crista longa para trás, aba sobre os olhos, rosto sério.
    cv.poly([add(head, (-1, -4)), add(head, (-13, -7)), add(head, (-11, -5)), add(head, (-4, -1.5))], col['metal'])
    cv.ellipse(head, 5.2, 5.4, col['armor'])
    cv.ellipse(add(head, (2.4, 1.6)), 2.8, 3.3, col['skin'], spec=False)
    cv.poly([add(head, (-0.5, -2.8)), add(head, (6.2, -2.4)), add(head, (5.4, -0.9)), add(head, (0.5, -1.2))],
            col['armor'])
    cv.limb(add(head, (3.0, 0.2)), add(head, (4.6, 0.6)), 1, col['eye'], outline=False)   # olho fino
    cv.poly([add(head, (0, 2.5)), add(head, (2, 5.5)), add(head, (-0.5, 5))], col['armor'])  # protetor do queixo
    cv.ellipse(add(head, (-1.8, 0.8)), 2.0, 2.2, col['metal'])
    cv.ellipse(add(head, (2.2, -4.3)), 1.4, 1.4, col['gem'], glow=True)
    # Mecha de cabelo caindo na frente do rosto.
    cv.limb(add(head, (1.5, -2.5)), add(head, (0.5, 3.5)), 1.4, col['hair'], outline=False)
    return sh_f


def hero_arm(cv, kind):
    """Braço da frente com origem no ombro: 0 solto, 1 canhão apontado para a frente."""
    col = HERO
    if kind == 0:
        el = ang(0.18, 7.5)
        hand = add(el, ang(-0.1, 7.0))
        cv.limb((0, 1), el, 3.4, col['suit'])
        cv.limb(el, add(el, ang(-0.1, 5.5)), 4.8, col['armor'])
        cv.ellipse(hand, 2.3, 2.3, col['suit'])
        cv.ellipse((0, 0.4), 3.6, 3.2, col['armor'])
        cv.pixel((1, -1), col['trim'])
        return hand
    el = (5.5, 2.0)
    cv.limb((0, 1), el, 3.4, col['suit'])
    # Canhão esguio: cano longo, anel dourado e boca com energia.
    cv.limb(el, add(el, (11.0, 0)), 6.4, col['armor'])
    cv.limb(add(el, (3.0, -3.0)), add(el, (3.0, 3.0)), 1.8, col['trim'], outline=False)
    cv.ellipse(add(el, (12.0, 0)), 2.0, 3.2, col['metal'])
    cv.ellipse(add(el, (12.5, 0)), 1.2, 1.9, col['glow'], glow=True)
    cv.ellipse((0, 0.4), 3.6, 3.2, col['armor'])
    return add(el, (14.5, 0))


# --- Inimigos ------------------------------------------------------------------

def crawler(cv, anim, t):
    """Rastejante: besouro alienígena de carapaça dura que cospe ácido."""
    shell, belly, eye = rgb('5a3a5e'), rgb('2a1c30'), rgb('b6ff3a')
    s = math.sin(t * math.tau)
    for i, x in enumerate((-8, -2, 5)):
        k = (s if i % 2 == 0 else -s) * 2.5
        cv.limb((x, -7), (x - 3 + k, -1), 1.8, shade(belly, 0.2))
        cv.limb((x - 3 + k, -1), (x - 4 + k, 0), 1.5, shade(belly, 0.3), outline=False)
    cv.ellipse((0, -9), 11, 6.5, shell)
    cv.poly([(-9, -12), (-2, -15.5), (6, -14), (10, -10), (0, -11)], shade(shell, 0.2))
    for x in (-5, 1):
        cv.limb((x, -15), (x + 2, -5), 1, shade(shell, -0.35), outline=False)
    open_mouth = 2.5 if anim == 'shoot' else 0.5
    cv.ellipse((11, -7), 4.5, 4, belly)
    cv.poly([(13, -6), (18, -5 - open_mouth), (15, -4)], rgb('d6cdb4'))
    cv.poly([(13, -6), (18, -3 + open_mouth), (15, -5)], rgb('d6cdb4'))
    cv.pixel((12, -9), eye, 2)


def flyer(cv, anim, t):
    """Zumbidor: drone-inseto que mergulha sobre o jogador."""
    body, wing, eye = rgb('2c4a3a'), rgb('9fe8d0'), rgb('ff4a3a')
    flap = math.sin(t * math.tau)
    for side, dim in ((-1, -0.3), (1, 0.0)):
        tip = (-4 + side * 2, -10 - flap * 8)
        cv.poly([(-2, -2), tip, (6 + side * 2, -6 - flap * 6)], shade(wing, dim), light=0.1)
    cv.ellipse((0, 0), 8, 5, body)
    for x in (-4, 0):
        cv.limb((x, -4), (x, 4), 1.4, shade(body, 0.35), outline=False)
    cv.poly([(-7, 1), (-14, 4), (-7, 3)], rgb('e8d070'))
    cv.ellipse((8, -1), 4, 4, shade(body, 0.15))
    cv.pixel((9, -2), eye, 2)
    cv.limb((10, 1), (13, 4), 1, rgb('d6cdb4'), outline=False)


def turret(cv, anim, t):
    """Bulbo: casulo preso ao chão que se abre para atirar três esporos."""
    pod, inner, eye = rgb('3a5a2e'), rgb('1c2a14'), rgb('ffd23a')
    opening = {'closed': 0.0, 'opening': 0.5, 'open': 1.0}[anim] if anim in ('closed', 'opening', 'open') else 0.0
    cv.ellipse((0, -8), 9, 8, pod)
    if opening > 0:
        cv.ellipse((0, -10), 6 * opening + 1, 4 * opening + 1, inner, light=0.0)
        cv.ellipse((0, -10), 2.5 * opening + 0.5, 2.5 * opening + 0.5, eye, glow=True)
    for a in (-0.8, 0.0, 0.8):
        petal_y = -16 - opening * 3
        cv.poly([(math.sin(a) * 6, -9), (math.sin(a) * 10 - 2, petal_y), (math.sin(a) * 10 + 2, petal_y)],
                shade(pod, 0.15))
    cv.limb((-9, 0), (9, 0), 2.5, shade(pod, -0.3))


# --- Chefe: Vespa de Plasma ----------------------------------------------------

def wasp(cv, anim, t):
    amber, black, wing, glow = rgb('e0a020'), rgb('2a1c12'), rgb('ffe9a8'), rgb('ffb43a')
    s = math.sin(t * math.tau)
    bob = 2 * s if anim == 'idle' else 0
    lean = {'idle': 0.1, 'dash': 0.8, 'shoot': -0.2, 'hurt': -0.4}.get(anim, 0.1)
    y0 = -40 - bob
    # Asas (atrás), batendo rápido.
    flap = math.sin(t * math.tau * 2) * 6
    for side, dim in ((-1, -0.3), (1, 0.0)):
        cv.poly([(-4, y0 - 6), (-26 + side * 3, y0 - 22 - flap), (-14 + side * 2, y0 - 2)], shade(wing, dim), light=0.1)
    # Abdômen listrado com o ferrão (para trás e para baixo; aponta para a frente ao atirar).
    sting = {'shoot': (16, 18), 'dash': (-10, 22)}.get(anim, (-14, 18))
    ab = add((0, y0), (-8 - lean * 4, 10))
    cv.ellipse(ab, 9, 7, amber)
    for k in (-4, 1, 6):
        cv.limb(add(ab, (k - 3, -6)), add(ab, (k, 6)), 2, black, outline=False)
    tip = add(ab, sting)
    cv.poly([add(ab, (-3, 3)), add(ab, (3, 5)), tip], black)
    cv.pixel(tip, glow, 2)
    # Pernas finas.
    for k, dx in enumerate((-3, 2, 6)):
        knee = add((dx, y0 + 8), (4 + k, 8))
        cv.limb((dx, y0 + 8), knee, 2, black)
        cv.limb(knee, add(knee, (-2 + k, 10)), 1.6, black)
    # Tórax blindado.
    thorax = add((0, y0), (math.sin(lean) * 3, 0))
    cv.ellipse(thorax, 8, 10, black)
    cv.poly([add(thorax, (-6, -6)), add(thorax, (7, -7)), add(thorax, (6, 2)), add(thorax, (-5, 3))], amber)
    cv.limb(add(thorax, (-6, -1)), add(thorax, (7, -2)), 2, black, outline=False)
    # Braços com lâminas de plasma.
    arm_a = {'shoot': 1.4, 'dash': 1.9, 'hurt': -2.0}.get(anim, 0.6 + 0.15 * s)
    sh = add(thorax, (4, -5))
    el = add(sh, ang(arm_a, 9))
    hand = add(el, ang(arm_a + 0.5, 8))
    cv.limb(sh, el, 3, black)
    cv.limb(el, hand, 3, amber)
    blade = add(hand, ang(arm_a + 0.9, 12))
    cv.limb(hand, blade, 2.5, glow, glow=True)
    # Cabeça: olhos compostos enormes e mandíbulas.
    head = add(thorax, (math.sin(lean) * 8 + 4, -14))
    cv.ellipse(head, 7, 6, black)
    cv.ellipse(add(head, (3, -1)), 4, 4.5, rgb('ff6a1a'), glow=True)
    for dx, dy in ((2, -2), (4, 0), (3, 2)):
        cv.pixel(add(head, (dx, dy)), rgb('ffd0a0'))
    cv.limb(add(head, (5, 3)), add(head, (9, 6)), 1.5, rgb('d6cdb4'), outline=False)
    cv.limb(add(head, (-2, -5)), add(head, (-6, -14)), 1.2, black, outline=False)   # antenas
    cv.limb(add(head, (1, -5)), add(head, (3, -15)), 1.2, black, outline=False)


# --- Itens ------------------------------------------------------------------------

def item(cv, kind, t):
    pulse = math.sin(t * math.tau)
    if kind in ('health_small', 'health_big'):
        r = 3.5 if kind == 'health_small' else 6
        cv.ellipse((0, -r - 1), r, r, rgb('ff3a5a'), glow=True)
        cv.ellipse((-r * 0.3, -r * 1.3), r * 0.35, r * 0.35, rgb('ffd0dc'), glow=True, outline=False)
    elif kind in ('energy_small', 'energy_big'):
        r = 3.5 if kind == 'energy_small' else 6
        cv.poly([(0, -2 * r - 2), (r, -r - 1), (0, -1), (-r, -r - 1)], rgb('5ae8ff'), glow=True)
        cv.pixel((0, -r - 1), (230, 255, 255))
    elif kind == 'heart':
        # Coração Simbionte: aumenta a vida máxima.
        cv.ellipse((-3, -10), 4, 4, rgb('c8203a'))
        cv.ellipse((3, -10), 4, 4, rgb('c8203a'))
        cv.poly([(-7, -9), (7, -9), (0, -1)], rgb('c8203a'))
        cv.limb((-2, -13), (2, -6), 1, rgb('ff8aa0'), outline=False)
        cv.pixel((0, -9 - pulse), rgb('7affe0'), 2)
    elif kind == 'capsule':
        # Casulo de armadura: guarda uma peça da armadura simbionte.
        cv.ellipse((0, -14), 9, 13, rgb('3a6a5e'))
        cv.ellipse((0, -15), 5.5, 9, rgb('7affe0'), glow=True)
        cv.ellipse((0, -15), 3, 5 + pulse, rgb('e8fff8'), glow=True, outline=False)
        cv.limb((-9, 0), (9, 0), 3, rgb('2a3a34'))


SHEETS = {
    'hero': dict(frame=(64, 64), origin=(32, 60), draw=hero,
                 anims=dict(idle=(4, 5), run=(10, 18), jump=(2, 8), fall=(2, 8), dash=(2, 10), wall=(1, 1),
                            hurt=(1, 1), spin=(8, 24))),
    'crawler': dict(frame=(48, 32), origin=(20, 30), draw=crawler, anims=dict(walk=(4, 8), shoot=(1, 1))),
    'flyer': dict(frame=(48, 40), origin=(24, 22), draw=flyer, anims=dict(fly=(3, 18))),
    'turret': dict(frame=(32, 32), origin=(16, 30), draw=turret, anims=dict(closed=(1, 1), opening=(1, 1), open=(1, 1))),
    'wasp': dict(frame=(96, 96), origin=(48, 84), draw=wasp,
                 anims=dict(idle=(4, 10), dash=(2, 12), shoot=(2, 6), hurt=(1, 1))),
    'items': dict(frame=(32, 32), origin=(16, 30), draw=item,
                  anims={k: (4, 6) for k in ('health_small', 'health_big', 'energy_small', 'energy_big', 'heart', 'capsule')}),
}


def render_hero(spec):
    """VEX-9: pixel art por peças (tools/suit.py), paleta Marfim."""
    import suit
    fw, fh = spec['frame']
    origin = spec['origin']
    anims = list(spec['anims'].items())
    cols = max(n for n, _ in spec['anims'].values())
    sheet = Image.new('RGBA', (fw * max(cols, 2), fh * (len(anims) + 1)))
    meta = dict(frame=[fw, fh], origin=list(origin), anims={}, shoulders={})
    for row, (anim, (frames, fps)) in enumerate(anims):
        meta['anims'][anim] = dict(row=row, frames=frames, fps=fps)
        shoulders = []
        for k in range(frames):
            if anim == 'spin':
                # Cambalhota: a pose encolhida girada de 45 em 45 graus.
                frame, shoulder = suit.draw('spin', 0.0, fw, fh, origin)
                img = frame.image().rotate(-45 * k, resample=Image.NEAREST, center=(origin[0], origin[1] - 22))
            else:
                frame, shoulder = suit.draw(anim, k / frames, fw, fh, origin)
                img = frame.image()
            shoulders.append([shoulder[0] - origin[0], shoulder[1] - origin[1]])
            sheet.paste(img, (k * fw, row * fh))
        meta['shoulders'][anim] = shoulders
    row = len(anims)
    meta['arm_row'] = row
    meta['arm_origin'] = [32, 32]
    for kind in (0, 1):
        frame, muzzle = suit.cannon_layers(kind)
        meta['muzzle' if kind == 1 else 'muzzle_down'] = [muzzle[0] - 32, muzzle[1] - 32]
        sheet.paste(frame.image(), (kind * fw, row * fh))
    sheet.save(os.path.join(OUT, 'hero.png'))
    return meta


def render(name, spec):
    if name == 'hero':
        return render_hero(spec)
    fw, fh = spec['frame']
    anims = list(spec['anims'].items())
    cols = max(n for n, _ in spec['anims'].values())
    arm = name == 'hero'
    sheet = Image.new('RGBA', (fw * max(cols, 2), fh * (len(anims) + (1 if arm else 0))))
    meta = dict(frame=[fw, fh], origin=list(spec['origin']), anims={})
    if arm:
        meta['shoulders'] = {}
    for row, (anim, (frames, fps)) in enumerate(anims):
        meta['anims'][anim] = dict(row=row, frames=frames, fps=fps)
        shoulders = []
        for f in range(frames):
            cv = Canvas(fw, fh, spec['origin'])
            if name == 'items':
                spec['draw'](cv, anim, f / frames)
            else:
                r = spec['draw'](cv, anim, f / frames)
                if arm:
                    shoulders.append([round(r[0], 1), round(r[1], 1)])
            sheet.paste(cv.finish(), (f * fw, row * fh))
        if arm:
            meta['shoulders'][anim] = shoulders
    if arm:
        row = len(anims)
        meta['arm_row'] = row
        meta['arm_origin'] = [fw // 2, fh // 2]
        for kind in (0, 1):
            cv = Canvas(fw, fh, (fw // 2, fh // 2))
            tip = hero_arm(cv, kind)
            if kind == 1:
                meta['muzzle'] = [round(tip[0], 1), round(tip[1], 1)]
            sheet.paste(cv.finish(), (kind * fw, row * fh))
    sheet.save(os.path.join(OUT, f'{name}.png'))
    return meta


def to_gdscript(value, indent=1):
    tab = '\t' * indent
    if isinstance(value, dict):
        items = ',\n'.join(f'{tab}"{k}": {to_gdscript(v, indent + 1)}' for k, v in value.items())
        return '{\n' + items + '\n' + '\t' * (indent - 1) + '}'
    if isinstance(value, list):
        return '[' + ', '.join(to_gdscript(v, indent) for v in value) + ']'
    return str(value)


def main():
    os.makedirs(OUT, exist_ok=True)
    data = {name: render(name, spec) for name, spec in SHEETS.items()}
    with open(os.path.join(ROOT, 'scripts', 'sprite_data.gd'), 'w', encoding='utf-8') as f:
        f.write('class_name SpriteData\n## Gerado por tools/generate_sprites.py. Não edite à mão.\n\n')
        f.write('const SHEETS := ' + to_gdscript(data) + '\n')
    print(f'{len(data)} folhas geradas em art/sprites/')


if __name__ == '__main__':
    main()
