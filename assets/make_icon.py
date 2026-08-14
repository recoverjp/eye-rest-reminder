"""Gera assets/icon.ico (o olho azul) usado como ícone do executável.

Rode com:  python assets/make_icon.py
Só precisa rodar de novo se você quiser mudar o desenho do ícone.
"""

import os

from PIL import Image, ImageDraw


def draw_eye(size: int) -> Image.Image:
    """Desenha o olho num canvas quadrado do tamanho pedido."""
    s = 64  # desenhamos em 64x64 e reduzimos (antialias)
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 20, 60, 44), fill=(245, 245, 245, 255),
              outline=(40, 40, 40, 255), width=2)       # contorno do olho
    d.ellipse((25, 20, 44, 44), fill=(60, 120, 220, 255))   # íris
    d.ellipse((30, 26, 39, 38), fill=(20, 20, 20, 255))     # pupila
    d.ellipse((32, 27, 36, 31), fill=(255, 255, 255, 255))  # brilho
    if size != s:
        img = img.resize((size, size), Image.LANCZOS)
    return img


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "icon.ico")
    sizes = [16, 24, 32, 48, 64, 128, 256]
    base = draw_eye(256)
    base.save(out, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"Ícone salvo em {out}")


if __name__ == "__main__":
    main()
