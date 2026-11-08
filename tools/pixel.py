"""Base de pixel art usada pelos geradores de sprites e tiles do projeto.

Canvas: um quadro onde as peças são desenhadas em ordem com cores chapadas e,
no fim, viram pixel art: luz de cima à esquerda, sombra embaixo à direita e
contorno escuro em volta da silhueta.
"""
import math

import numpy as np
from PIL import Image, ImageDraw


def rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def shade(color, amount):
    """amount > 0 clareia, < 0 escurece (puxando um pouco para o roxo/azul)."""
    r, g, b = color
    if amount >= 0:
        return tuple(int(c + (255 - c) * amount) for c in (r, g, b))
    k = 1.0 + amount
    return (int(r * k * 0.95), int(g * k * 0.92), int(min(255, b * k * 1.05 + 6 * -amount)))


class Canvas:
    """Quadro de pixel art: peças desenhadas em ordem, cada uma com sua cor e
    sombreamento próprio; o contorno é feito no fim, em volta de tudo."""

    def __init__(self, w, h, origin):
        self.w, self.h = w, h
        self.ox, self.oy = origin
        self.color = np.zeros((h, w, 4), dtype=np.uint8)
        self.solid = np.zeros((h, w), dtype=bool)

    def _p(self, point):
        return (self.ox + point[0], self.oy + point[1])

    def _mask(self, draw_fn):
        img = Image.new('L', (self.w, self.h), 0)
        draw_fn(ImageDraw.Draw(img))
        return np.array(img) > 0

    def part(self, mask, color, light=0.18, dark=-0.32, outline=True, glow=False):
        if not mask.any():
            return
        up = np.zeros_like(mask); up[1:, :] = mask[:-1, :]
        left = np.zeros_like(mask); left[:, 1:] = mask[:, :-1]
        down = np.zeros_like(mask); down[:-1, :] = mask[1:, :]
        right = np.zeros_like(mask); right[:, :-1] = mask[:, 1:]
        down2 = np.zeros_like(mask); down2[:-2, :] = mask[2:, :]
        base = np.array(color + (255,), dtype=np.uint8)
        hi = np.array(shade(color, light) + (255,), dtype=np.uint8)
        lo = np.array(shade(color, dark) + (255,), dtype=np.uint8)
        lo2 = np.array(shade(color, dark * 0.5) + (255,), dtype=np.uint8)
        self.color[mask] = base
        if not glow:
            self.color[mask & ~down2] = lo2
            self.color[mask & (~down | ~right)] = lo
            self.color[mask & (~up | ~left) & down & right] = hi
        if outline:
            self.solid |= mask

    # Primitivas (coordenadas relativas aos pés; y para cima é negativo).
    def poly(self, points, color, **kw):
        pts = [self._p(p) for p in points]
        self.part(self._mask(lambda d: d.polygon(pts, fill=255)), color, **kw)

    def limb(self, a, b, width, color, **kw):
        pa, pb = self._p(a), self._p(b)
        r = width / 2.0

        def fn(d):
            d.line([pa, pb], fill=255, width=max(1, int(round(width))))
            for (x, y) in (pa, pb) if r >= 1.0 else ():
                d.ellipse([x - r + 0.5, y - r + 0.5, x + r - 0.5, y + r - 0.5], fill=255)
        self.part(self._mask(fn), color, **kw)

    def ellipse(self, center, rx, ry, color, **kw):
        cx, cy = self._p(center)
        self.part(self._mask(lambda d: d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)), color, **kw)

    def pixel(self, point, color, size=1):
        x, y = int(round(self.ox + point[0])), int(round(self.oy + point[1]))
        self.color[y:y + size, x:x + size] = np.array(color + (255,), dtype=np.uint8)
        self.solid[y:y + size, x:x + size] = True

    def finish(self, outline_color=(14, 9, 20)):
        """Contorno escuro de 1 px em volta da silhueta."""
        m = self.solid
        grown = m.copy()
        grown[1:, :] |= m[:-1, :]; grown[:-1, :] |= m[1:, :]
        grown[:, 1:] |= m[:, :-1]; grown[:, :-1] |= m[:, 1:]
        edge = grown & ~m & (self.color[:, :, 3] == 0)
        self.color[edge] = np.array(outline_color + (255,), dtype=np.uint8)
        return Image.fromarray(self.color, 'RGBA')


def ang(angle, length):
    """Vetor a partir de um ângulo medido da vertical para baixo (+ = para frente)."""
    return (math.sin(angle) * length, math.cos(angle) * length)


def add(a, b): return (a[0] + b[0], a[1] + b[1])
