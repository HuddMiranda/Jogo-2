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

HERO = dict(armor=rgb('2a8fa0'), armor2=rgb('e6dcc0'), suit=rgb('26243a'), glow=rgb('7affe0'),
            visor=rgb('5ae8ff'), gem=rgb('ff4a7a'), boot=rgb('1a6670'), skin=rgb('f0c8a8'),
            eye=rgb('2a3a8a'), hair=rgb('d04a7a'))


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
    """VEX-9: proporções de herói de ação (cabeça e capacete grandes, ombreiras,
    antebraços e botas grossas e arredondadas; cintura e coxas finas)."""
    p = hero_pose(anim, t)
    col = HERO
    hip = (0.0, -19.5 - p['bob'] + 3.5 * (1 - math.cos(min(p['knee_f'], p['knee_b']) * 0.5)))
    lean = p['lean']
    neck = add(hip, (math.sin(lean) * 10.5, -math.cos(lean) * 10.5))
    sh_f = add(neck, (3.0, 1.5))
    sh_b = add(neck, (-3.0, 1.0))
    head = add(neck, (math.sin(lean + p['head']) * 7.0 + 1.0, -math.cos(lean + p['head']) * 7.0))
    sway = math.sin(t * math.tau) * 1.0

    def leg(a, k, back):
        dim = -0.3 if back else 0.0
        knee = add(hip, ang(a, 8.5))
        foot = add(knee, ang(a - k, 9.5))
        cv.limb(hip, add(knee, ang(a - k, 1.0)), 4.5, shade(col['suit'], dim))
        # Bota grande: cano grosso arredondado, faixa clara no topo e pé em "ovo".
        top = add(knee, ang(a - k, 2.0))
        cv.limb(top, add(foot, (0, -2)), 8.5, shade(col['armor'], dim))
        cv.ellipse(add(foot, (2.0, -1.5)), 6.0, 3.6, shade(col['armor'], dim))
        d = ang(a - k, 1.0)
        side = (-d[1], d[0])
        cv.limb(add(top, (side[0] * 3.8, side[1] * 3.8)), add(top, (-side[0] * 3.8, -side[1] * 3.8)), 2.4,
                shade(col['armor2'], dim), outline=False)
        cv.pixel(add(foot, (4, -2)), col['glow'] if not back else shade(col['glow'], -0.5))

    def back_arm():
        dim = -0.3
        el = add(sh_b, ang(p['arm_b'], 6))
        hand = add(el, ang(p['arm_b'] + p['elbow_b'], 6))
        cv.limb(sh_b, el, 3.5, shade(col['suit'], dim))
        cv.limb(el, add(el, ang(p['arm_b'] + p['elbow_b'], 4.5)), 7.0, shade(col['armor'], dim))
        cv.ellipse(hand, 3.0, 3.0, shade(col['armor2'], dim))
        cv.ellipse(add(sh_b, (0, -0.5)), 4.8, 4.2, shade(col['armor'], dim))

    # Rabo de cavalo saindo do capacete (atrás de tudo).
    tail = add(head, (-6.5, 1.0))
    prev = tail
    for k in range(3):
        nxt = add(prev, (-2.5 - k * 0.5, 2.5 + sway * (k + 1) * 0.4 - p['bob'] * 0.2))
        cv.limb(prev, nxt, 3.6 - k * 0.8, col['hair'])
        prev = nxt
    back_arm()
    leg(p['thigh_b'], p['knee_b'], True)
    # Cintura fina e cinto com a gema.
    cv.limb(hip, add(neck, (0, 3)), 5.5, col['suit'])
    leg(p['thigh_f'], p['knee_f'], False)
    cv.rounded(hip[0] - 5, hip[1] - 2.5, 10, 4, 2, col['armor2'])
    cv.ellipse(add(hip, (1.5, -0.5)), 1.5, 1.5, col['gem'], glow=True)
    # Peitoral arredondado com a gema-núcleo.
    chest = add(neck, (1.0, 3.5))
    cv.ellipse(chest, 6.5, 5.0, col['armor'])
    cv.ellipse(add(chest, (2.0, 0.5)), 2.2, 2.2, col['gem'], glow=True)
    cv.pixel(add(chest, (1.5, 0)), (255, 225, 238))
    # Capacete grande: rosto à mostra, olho grande, disco na lateral e crista.
    cv.poly([add(head, (-1, -7)), add(head, (-11, -11)), add(head, (-9, -8)), add(head, (-4, -4))], col['armor2'])
    cv.ellipse(head, 8.2, 7.8, col['armor'])
    cv.ellipse(add(head, (3.6, 2.0)), 4.3, 4.4, col['skin'], spec=False)
    cv.limb(add(head, (0.5, -2.2)), add(head, (8.0, -2.2)), 3.2, col['armor'])       # aba do capacete
    cv.pixel(add(head, (4.5, 0.6)), (250, 250, 255), 2)                               # olho
    cv.pixel(add(head, (5.5, 1.6)), col['eye'])
    cv.pixel(add(head, (5.5, 0.6)), col['eye'])
    cv.ellipse(add(head, (-2.5, 1.0)), 3.2, 3.2, col['armor2'])                         # disco da orelha
    cv.pixel(add(head, (-3.0, 0.5)), col['glow'], 2)
    cv.ellipse(add(head, (5.0, -5.5)), 1.8, 1.8, col['gem'], glow=True)                # gema da testa
    return sh_f


def hero_arm(cv, kind):
    """Braço da frente com origem no ombro: 0 solto, 1 canhão apontado para a frente."""
    col = HERO
    if kind == 0:
        el = ang(0.2, 6)
        hand = add(el, ang(-0.15, 6.5))
        cv.limb((0, 1), el, 3.8, col['suit'])
        cv.limb(el, add(el, ang(-0.15, 4.5)), 7.2, col['armor'])
        cv.ellipse(hand, 3.2, 3.2, col['armor2'])
        cv.ellipse((0, 0.8), 4.4, 4.0, col['armor'])
        return hand
    el = (4.5, 2.5)
    cv.limb((0, 1), el, 3.8, col['suit'])
    # Canhão: cilindro grosso com anel claro e boca brilhante.
    cv.limb(add(el, (0, 0)), add(el, (9.5, 0)), 8.6, col['armor'])
    cv.limb(add(el, (3.5, -4.0)), add(el, (3.5, 4.0)), 2.4, col['armor2'], outline=False)
    cv.ellipse(add(el, (11.0, 0)), 2.6, 4.0, col['armor2'])
    cv.ellipse(add(el, (11.6, 0)), 1.5, 2.4, col['glow'], glow=True)
    cv.ellipse((0, 0.8), 4.4, 4.0, col['armor'])
    return add(el, (13.5, 0))


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
                 anims=dict(idle=(4, 5), run=(10, 16), jump=(2, 8), fall=(2, 8), dash=(2, 10), wall=(1, 1),
                            hurt=(1, 1))),
    'crawler': dict(frame=(48, 32), origin=(20, 30), draw=crawler, anims=dict(walk=(4, 8), shoot=(1, 1))),
    'flyer': dict(frame=(48, 40), origin=(24, 22), draw=flyer, anims=dict(fly=(3, 18))),
    'turret': dict(frame=(32, 32), origin=(16, 30), draw=turret, anims=dict(closed=(1, 1), opening=(1, 1), open=(1, 1))),
    'wasp': dict(frame=(96, 96), origin=(48, 84), draw=wasp,
                 anims=dict(idle=(4, 10), dash=(2, 12), shoot=(2, 6), hurt=(1, 1))),
    'items': dict(frame=(32, 32), origin=(16, 30), draw=item,
                  anims={k: (4, 6) for k in ('health_small', 'health_big', 'energy_small', 'energy_big', 'heart', 'capsule')}),
}


def render(name, spec):
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
