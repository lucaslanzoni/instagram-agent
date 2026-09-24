#!/usr/bin/env python3
"""renderizar.py - transforma slides HTML em JPG 1080x1350 com Chrome headless.

Uso
  uv run python -m ferramentas.renderizar clientes/tropi/2026-10/posts/03-afim-ze-ibarra
"""

import os
import re
import subprocess
import sys
from pathlib import Path

CHROME = os.environ.get(
    "CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)
SLIDE_RE = re.compile(r"^slide-(\d+)\.html$")


def ordenar_slides(arquivos):
    numerados = []
    for arquivo in arquivos:
        m = SLIDE_RE.match(Path(arquivo).name)
        if m:
            numerados.append((int(m.group(1)), Path(arquivo)))
    return [a for _, a in sorted(numerados)]


def renderizar(html, saida, largura=1080, altura=1350, qualidade=85):
    html, saida = Path(html), Path(saida)
    png = saida.with_suffix(".png")
    subprocess.run(
        [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--window-size={largura},{altura}",
            "--virtual-time-budget=5000",
            f"--screenshot={png}",
            html.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        timeout=120,
    )
    subprocess.run(
        [
            "sips",
            "-s",
            "format",
            "jpeg",
            "-s",
            "formatOptions",
            str(qualidade),
            str(png),
            "--out",
            str(saida),
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )
    png.unlink(missing_ok=True)
    return saida


def dimensoes(imagem):
    r = subprocess.run(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(imagem)],
        check=True,
        capture_output=True,
        text=True,
    )
    largura = int(re.search(r"pixelWidth: (\d+)", r.stdout).group(1))
    altura = int(re.search(r"pixelHeight: (\d+)", r.stdout).group(1))
    return largura, altura


def renderizar_post(pasta):
    pasta = Path(pasta)
    slides = ordenar_slides(sorted(pasta.glob("slide-*.html")))
    if not slides:
        raise FileNotFoundError(f"nenhum slide-N.html em {pasta}")
    saidas = [
        renderizar(html, pasta / f"{i}.jpg") for i, html in enumerate(slides, start=1)
    ]
    for velho in pasta.glob("*.jpg"):
        if velho.stem.isdigit() and int(velho.stem) > len(slides):
            velho.unlink()
    return saidas


def main():
    if len(sys.argv) != 2:
        sys.exit("uso: python -m ferramentas.renderizar <pasta-do-post>")
    for saida in renderizar_post(sys.argv[1]):
        print(saida, dimensoes(saida))


if __name__ == "__main__":
    main()
