#!/usr/bin/env python3
"""renderizar.py - transforma slides HTML em JPG com Chrome headless.

A altura vem do `height:<n>px` no style do <body> (1920 para capa de Reels e story);
sem ele, 1080x1350.

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
ALTURA_RE = re.compile(r"<body[^>]*style=[\"'][^\"']*height:\s*(\d+)px")


def altura_do_slide(texto, padrao=1350):
    m = ALTURA_RE.search(texto)
    return int(m.group(1)) if m else padrao


def ordenar_slides(arquivos):
    numerados = []
    for arquivo in arquivos:
        m = SLIDE_RE.match(Path(arquivo).name)
        if m:
            numerados.append((int(m.group(1)), Path(arquivo)))
    return [a for _, a in sorted(numerados)]


def capturar(html, png, largura=1080, altura=1350, transparente=False):
    """Screenshot do HTML em PNG; com transparente=True, o fundo sem cor fica transparente."""
    html, png = Path(html), Path(png)
    subprocess.run(
        [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            f"--window-size={largura},{altura}",
            "--virtual-time-budget=5000",
            *(["--default-background-color=00000000"] if transparente else []),
            f"--screenshot={png}",
            html.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        timeout=120,
    )
    return png


def renderizar(html, saida, largura=1080, altura=1350, qualidade=85):
    html, saida = Path(html), Path(saida)
    png = capturar(html, saida.with_suffix(".png"), largura, altura)
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
        renderizar(
            html,
            pasta / f"{i}.jpg",
            altura=altura_do_slide(html.read_text(encoding="utf-8")),
        )
        for i, html in enumerate(slides, start=1)
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
