#!/usr/bin/env python3
"""Prova visual: rasteriza a fonte em PNG para conferência de desenho."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import freetype
from PIL import Image, ImageDraw

BG, FG = (20, 20, 20), (245, 240, 235)
RED = (192, 57, 43)


def render_line(face, text, px, x, y, img, color=FG, track=0):
    face.set_char_size(px * 64)
    pen_x = x
    prev = None
    for ch in text:
        gi = face.get_char_index(ord(ch))
        if prev is not None:
            k = face.get_kerning(prev, gi)
            pen_x += k.x / 64.0
        face.load_glyph(gi, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
        g = face.glyph
        bm = g.bitmap
        if bm.width and bm.rows:
            data = bytes(bm.buffer)
            gimg = Image.frombytes("L", (bm.width, bm.rows), data)
            layer = Image.new("RGB", gimg.size, color)
            img.paste(layer, (int(pen_x) + g.bitmap_left, int(y) - g.bitmap_top), gimg)
        pen_x += g.advance.x / 64.0 + track
        prev = gi
    return pen_x


def sheet(path, out, title=""):
    face = freetype.Face(path)
    W, H = 1500, 1450
    img = Image.new("RGB", (W, H), BG)
    y = 90
    render_line(face, title or os.path.basename(path), 26, 60, y, img, (150, 150, 150))
    y += 90
    for t in ["ABCDEFGHIJKLM", "NOPQRSTUVWXYZ",
              "abcdefghijklm", "nopqrstuvwxyz", "0123456789"]:
        render_line(face, t, 62, 60, y, img)
        y += 92
    y += 20
    render_line(face, "divide a mesa.", 92, 60, y, img, RED)
    y += 110
    render_line(face, "coletivo — o mercado que divide a mesa", 40, 60, y, img)
    y += 66
    render_line(face, "Não é um dono mais barato. É não ter dono.", 34, 60, y, img)
    y += 58
    for px in (28, 22, 17, 14, 12):
        render_line(face, "O restaurante fica com o que é dele; o entregador "
                          "ganha o justo. R$ 38,90 — 23% de taxa.", px, 60, y, img)
        y += px + 22
    img.save(out)
    print("→", out)


def waterfall(paths, out, text="Hamburguesa Ção 123"):
    img = Image.new("RGB", (1500, 120 * len(paths) + 60), BG)
    y = 90
    for p in paths:
        face = freetype.Face(p)
        render_line(face, text, 58, 60, y, img)
        render_line(face, os.path.basename(p).replace(".ttf", ""), 16, 1150, y,
                    img, (130, 130, 130))
        y += 120
    img.save(out)
    print("→", out)


if __name__ == "__main__":
    sheet(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "/tmp/p.png")
