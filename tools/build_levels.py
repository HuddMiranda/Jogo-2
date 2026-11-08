#!/usr/bin/env python3
"""Monta os mapas das fases (levels/*.gd) a partir de trechos descritos aqui.

    python tools/build_levels.py

Cada mapa é uma grade de caracteres (legenda em scenes/level/level.gd); este
script só ajuda a desenhá-la com retângulos e marcadores, em vez de digitar
centenas de colunas à mão. Dá para editar os .gd gerados diretamente também.
"""
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
H = 23
FLOOR = 19   # primeira linha do chão


class Map:
    def __init__(self, width):
        self.w = width
        self.g = [[' '] * width for _ in range(H)]

    def fill(self, x1, x2, y1, y2, ch='#'):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if 0 <= x < self.w and 0 <= y < H:
                    self.g[y][x] = ch

    def ground(self, x1, x2):
        self.fill(x1, x2, FLOOR, H - 1)

    def put(self, x, y, ch):
        self.g[y][x] = ch

    def text(self):
        return '\n'.join(''.join(row).rstrip() for row in self.g)


def write(name, title, biome, mp, boss='', armor='legs'):
    body = mp.text()
    lines = [f'## Mapa gerado por tools/build_levels.py (legenda em scenes/level/level.gd).',
             f'const NAME := "{title}"', f'const BIOME := "{biome}"', f'const ARMOR := &"{armor}"']
    if boss:
        lines.append(f'const BOSS := &"{boss}"')
    lines.append('const MAP := """\n' + body + '\n"""')
    with open(os.path.join(ROOT, 'levels', f'{name}.gd'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def intro():
    """Abertura: Ruínas da Nave-Semente. Ensina pulo, dash-pulo e parede."""
    m = Map(232)
    m.fill(0, 0, 0, H - 1)
    m.ground(0, 31)
    m.put(3, 18, 'P')
    m.put(16, 18, 'c')
    m.fill(22, 25, 17, 18)
    # Abismo com plataformas vazadas.
    m.fill(34, 37, 15, 15, '=')
    m.fill(40, 43, 13, 13, '=')
    m.put(39, 8, 'f')
    m.ground(46, 99)
    m.put(58, 18, 't')
    m.fill(64, 69, 15, 18)
    m.put(66, 14, 'e')
    m.put(75, 18, 'c')
    m.put(82, 18, 'C')
    # Muro alto: suba pela parede (com um degrau de ajuda).
    m.fill(92, 94, 15, 15, '=')
    m.fill(96, 99, 9, 18)
    # Coração: escale a coluna fina acima do muro e pule para a beirada.
    m.fill(99, 99, 2, 8)
    m.fill(100, 103, 3, 3, '=')
    m.put(101, 2, 'L')
    m.ground(100, 140)
    m.fill(110, 113, 18, 18, '^')
    m.fill(124, 128, 18, 18, '^')
    m.fill(110, 113, 14, 14, '=')
    m.put(117, 9, 'f')
    m.put(131, 10, 'f')
    m.put(120, 18, 'h')
    m.put(141, 18, 'C')
    m.ground(141, 231)
    # Escada de blocos e, lá no alto, o casulo das Pernas (dash-pulo no vão).
    m.fill(146, 149, 17, 18)
    m.fill(150, 153, 15, 18)
    m.fill(154, 157, 13, 18)
    m.fill(167, 170, 13, 13)
    m.put(168, 12, 'A')
    m.put(162, 18, 'c')
    m.put(180, 18, 't')
    m.put(190, 9, 'f')
    m.fill(186, 189, 15, 15, '=')
    m.put(200, 18, 'c')
    m.put(206, 18, 'H')
    m.put(212, 10, 'f')
    m.put(218, 18, 't')
    m.put(228, 18, 'G')
    m.fill(231, 231, 0, H - 1)
    write('intro', 'Ruínas da Nave-Semente', 'ruins', m, armor='legs')


def hive():
    """Colmeia de Plasma: fase da Vespa. Zumbidores, favos e um túnel."""
    m = Map(300)
    m.fill(0, 0, 0, H - 1)
    m.ground(0, 30)
    m.put(3, 18, 'P')
    m.put(20, 8, 'f')
    m.put(26, 18, 'c')
    # Favos sobre um fosso de espinhos.
    m.fill(31, 60, 21, 22)
    m.fill(31, 60, 20, 20, '^')
    for x, y in ((33, 16), (39, 14), (45, 16), (51, 13), (56, 15)):
        m.fill(x, x + 2, y, y, '=')
    m.put(48, 7, 'f')
    m.ground(61, 120)
    m.put(70, 18, 't')
    m.fill(76, 80, 15, 18)
    m.put(78, 14, 'e')
    m.put(88, 18, 't')
    m.put(95, 9, 'f')
    # Chaminé entre dois favos pendurados: escale até o Coração.
    m.fill(104, 105, 3, 14)
    m.fill(110, 111, 3, 14)
    m.fill(106, 109, 3, 3, '=')
    m.put(107, 2, 'L')
    m.put(114, 18, 'C')
    m.ground(115, 170)
    # Túnel de teto baixo cheio de Zumbidores.
    m.fill(122, 160, 0, 10)
    for x in (128, 140, 152):
        m.put(x, 14, 'f')
    m.put(135, 18, 'c')
    m.put(147, 18, 'c')
    m.put(158, 18, 'h')
    m.put(166, 18, 't')
    # Espinhos com degraus vazados.
    m.ground(171, 257)
    m.fill(176, 195, 18, 18, '^')
    for x in (178, 185, 192):
        m.fill(x, x + 2, 15, 15, '=')
    m.put(188, 8, 'f')
    m.put(205, 18, 'c')
    # Casulo dos Braços: no alto, depois de um dash-pulo.
    m.fill(215, 218, 12, 18)
    m.fill(229, 232, 12, 12)
    m.put(230, 11, 'A')
    m.put(222, 18, 't')
    m.put(240, 18, 'c')
    m.put(246, 18, 'E')
    m.put(252, 18, 'C')
    # Porta da Besta e a arena (40 colunas = uma tela).
    m.fill(258, 258, 0, 14)
    m.fill(258, 258, 15, 18, 'D')
    m.ground(259, 299)
    m.fill(299, 299, 0, H - 1)
    m.put(290, 10, 'B')
    write('hive', 'Colmeia de Plasma', 'hive', m, boss='wasp', armor='arms')


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'levels'), exist_ok=True)
    intro()
    hive()
    print('fases geradas em levels/')
