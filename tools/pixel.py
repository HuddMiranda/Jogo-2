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

    # Luz vinda de cima à esquerda (vetor unitário apontando PARA a luz).
    LIGHT = (-0.55, -0.83)

    def shaded(self, mask, tone, color, outline=True, spec=None):
        """Pinta `mask` em faixas de tom (estilo 16/32 bits): `tone` vai de -1
        (sombra) a 1 (luz). Opcionalmente, um brilho especular de 2 px."""
        if not mask.any():
            return
        bands = [(0.62, 0.42), (0.22, 0.16), (-0.3, 0.0), (-0.72, -0.28), (-9.0, -0.46)]
        for threshold, amount in reversed(bands):
            sel = mask & (tone >= threshold)
            self.color[sel] = np.array(shade(color, amount) + (255,), dtype=np.uint8)
        if spec is not None:
            x, y = int(round(spec[0])), int(round(spec[1]))
            sub = mask[y:y + 2, x:x + 2]
            self.color[y:y + 2, x:x + 2][sub] = np.array(shade(color, 0.75) + (255,), dtype=np.uint8)
        if outline:
            self.solid |= mask

    def limb(self, a, b, width, color, glow=False, outline=True, **kw):
        """Membro/cilindro: sombreado ao longo da largura (lado da luz claro)."""
        pa, pb = self._p(a), self._p(b)
        r = width / 2.0

        def fn(d):
            d.line([pa, pb], fill=255, width=max(1, int(round(width))))
            for (x, y) in (pa, pb) if r >= 1.0 else ():
                d.ellipse([x - r + 0.5, y - r + 0.5, x + r - 0.5, y + r - 0.5], fill=255)
        mask = self._mask(fn)
        if glow or width < 2.5:
            self.part(mask, color, glow=glow, outline=outline, **kw)
            return
        ys, xs = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        length = max(1e-3, (dx * dx + dy * dy) ** 0.5)
        nx, ny = -dy / length, dx / length
        if nx * self.LIGHT[0] + ny * self.LIGHT[1] < 0:
            nx, ny = -nx, -ny
        across = ((xs + 0.5 - pa[0]) * nx + (ys + 0.5 - pa[1]) * ny) / max(r, 0.5)
        self.shaded(mask, across * 0.95, color, outline)

    def ellipse(self, center, rx, ry, color, glow=False, outline=True, spec=True, **kw):
        """Esfera/elipse com volume: luz de cima à esquerda, borda escura e brilho."""
        cx, cy = self._p(center)
        mask = self._mask(lambda d: d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255))
        if glow or min(rx, ry) < 2.0:
            self.part(mask, color, glow=glow, outline=outline, **kw)
            return
        ys, xs = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        nx = (xs + 0.5 - cx) / rx
        ny = (ys + 0.5 - cy) / ry
        r2 = nx * nx + ny * ny
        tone = (nx * self.LIGHT[0] + ny * self.LIGHT[1]) * 0.85 + (1.0 - r2) * 0.45 - 0.2
        tone = np.where(r2 > 0.82, np.minimum(tone, -0.4), tone)
        highlight = (cx - rx * 0.45 - 1, cy - ry * 0.5 - 1) if spec and min(rx, ry) >= 3.5 else None
        self.shaded(mask, tone, color, outline, highlight)

    def rounded(self, x, y, w, h, radius, color, outline=True):
        """Retângulo de cantos arredondados com volume (placas de armadura)."""
        x0, y0 = self._p((x, y))
        mask = self._mask(lambda d: d.rounded_rectangle([x0, y0, x0 + w - 1, y0 + h - 1], radius=radius, fill=255))
        ys, xs = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        nx = (xs + 0.5 - (x0 + w / 2)) / (w / 2)
        ny = (ys + 0.5 - (y0 + h / 2)) / (h / 2)
        tone = (nx * self.LIGHT[0] + ny * self.LIGHT[1]) * 0.8 + (1 - np.maximum(abs(nx), abs(ny)) ** 4) * 0.3 - 0.15
        self.shaded(mask, tone, color, outline)

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
