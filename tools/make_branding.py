#!/usr/bin/env python3
"""Build lms.wad: a small patch WAD that rebrands Freedoom as LAST MARINE STANDING.

Replaces TITLEPIC (title screen) and M_DOOM (main-menu logo).
Usage: make_branding.py <freedoom1.wad> <out.wad>
"""
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def read_wad(path):
    data = open(path, "rb").read()
    count, offset = struct.unpack("<4xii", data[:12])
    lumps = {}
    for i in range(count):
        pos, size, name = struct.unpack("<ii8s", data[offset + 16 * i: offset + 16 * i + 16])
        lumps.setdefault(name.rstrip(b"\0").decode(), data[pos:pos + size])
    return lumps


def decode_picture(lump, palette):
    w, h, _, _ = struct.unpack("<hhhh", lump[:8])
    img = np.zeros((h, w, 3), np.uint8)
    for x in range(w):
        (p,) = struct.unpack("<i", lump[8 + 4 * x: 12 + 4 * x])
        while lump[p] != 0xFF:
            top, length = lump[p], lump[p + 1]
            for i in range(length):
                img[top + i, x] = palette[lump[p + 3 + i]]
            p += length + 4
    return Image.fromarray(img)


def quantize(img, palette):
    rgb = np.asarray(img.convert("RGB"), np.int32)
    pal = palette.astype(np.int32)
    dist = ((rgb[:, :, None, :] - pal[None, None, :, :]) ** 2).sum(-1)
    return dist.argmin(-1).astype(np.uint8)


def encode_picture(indices, mask=None, xoff=0, yoff=0):
    """Encode palette indices as a Doom patch; mask=False pixels are transparent."""
    h, w = indices.shape
    if mask is None:
        mask = np.ones((h, w), bool)
    columns = []
    for x in range(w):
        col = bytearray()
        y = 0
        while y < h:
            if not mask[y, x]:
                y += 1
                continue
            start = y
            while y < h and mask[y, x] and y - start < 128:
                y += 1
            run = indices[start:y, x]
            col += bytes([start, len(run), run[0]]) + run.tobytes() + bytes([run[-1]])
        col.append(0xFF)
        columns.append(bytes(col))
    header = struct.pack("<hhhh", w, h, xoff, yoff)
    offset = 8 + 4 * w
    table = b""
    for c in columns:
        table += struct.pack("<i", offset)
        offset += len(c)
    return header + table + b"".join(columns)


def write_wad(path, lumps):
    body = b""
    directory = b""
    pos = 12
    for name, data in lumps:
        directory += struct.pack("<ii8s", pos, len(data), name.encode())
        body += data
        pos += len(data)
    open(path, "wb").write(b"PWAD" + struct.pack("<ii", len(lumps), pos) + body + directory)


def glow_text(size, lines, fill, glow, outline=(20, 0, 0)):
    """Render stacked, centered title text with a fiery glow on transparent RGBA."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    boxes = []
    for text, pt, y in lines:
        font = ImageFont.truetype(FONT, pt)
        tw = d.textlength(text, font=font)
        boxes.append((text, font, (w - tw) / 2, y))
    halo = Image.new("RGBA", size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for text, font, x, y in boxes:
        hd.text((x, y), text, font=font, fill=glow + (255,), stroke_width=3, stroke_fill=glow + (255,))
    halo = halo.filter(ImageFilter.GaussianBlur(3))
    layer = Image.alpha_composite(layer, halo)
    d = ImageDraw.Draw(layer)
    for text, font, x, y in boxes:
        d.text((x, y), text, font=font, fill=fill + (255,), stroke_width=2, stroke_fill=outline + (255,))
    return layer


def main(iwad, out):
    lumps = read_wad(iwad)
    palette = np.frombuffer(lumps["PLAYPAL"][:768], np.uint8).reshape(256, 3)

    # Title screen: darkened, red-tinted Freedoom intermission art + new logo.
    bg = decode_picture(lumps["INTERPIC"], palette).convert("RGB")
    arr = np.asarray(bg, np.float32)
    arr = arr * np.array([0.55, 0.22, 0.18])
    yy = np.linspace(0, 1, 200)[:, None, None]
    arr = arr * (0.35 + 0.65 * yy)  # fade to black at the top
    bg = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
    logo = glow_text((320, 200), [("LAST MARINE", 38, 28), ("STANDING", 46, 72)],
                     fill=(235, 200, 120), glow=(200, 40, 0))
    title = Image.alpha_composite(bg, logo)
    tag = ImageDraw.Draw(title)
    font = ImageFont.truetype(FONT, 9)
    msg = "ONE MARINE. ONE BASE. NO BACKUP."
    tag.text(((320 - tag.textlength(msg, font=font)) / 2, 182), msg, font=font, fill=(200, 160, 140, 255))
    titlepic = encode_picture(quantize(title, palette))

    # Main-menu logo (drawn at the top of the menu, transparent background).
    menu = glow_text((200, 52), [("LAST MARINE", 20, 2), ("STANDING", 24, 24)],
                     fill=(235, 200, 120), glow=(170, 30, 0))
    alpha = np.asarray(menu)[:, :, 3] > 90
    flat = Image.alpha_composite(Image.new("RGBA", menu.size, (0, 0, 0, 255)), menu)
    # The engine draws M_DOOM at (94, 2); a left offset of 34 centers our 200px-wide logo.
    m_doom = encode_picture(quantize(flat, palette), alpha, xoff=34, yoff=0)

    write_wad(out, [("TITLEPIC", titlepic), ("M_DOOM", m_doom)])
    title.convert("RGB").save(out.rsplit(".", 1)[0] + "-title-preview.png")


if __name__ == "__main__":
    main(*sys.argv[1:3])
