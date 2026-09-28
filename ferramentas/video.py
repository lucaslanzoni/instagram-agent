#!/usr/bin/env python3
"""video.py - aplica a moldura da marca a um vídeo de Reels (1080x1920) com ffmpeg.

Na pasta do post:
  moldura.html   camada da marca com fundo transparente (gerada pelo modelo do cliente)
  post-foto.json campo "video" com o arquivo original (ex.: "original.mov")
Saída: moldura.png e video.mp4 (H.264 + AAC, pronto para o Instagram).

Uso
  uv run python -m ferramentas.video clientes/tropi/2026-10/posts/12-tim-maia-video
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from ferramentas.renderizar import capturar

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
LARGURA, ALTURA = 1080, 1920


def comando_moldura(video, moldura, saida):
    """Monta o comando do ffmpeg: ajusta o vídeo a 9:16, sobrepõe a moldura no vídeo inteiro."""
    filtro = (
        f"[0:v]scale={LARGURA}:{ALTURA}:force_original_aspect_ratio=increase,"
        f"crop={LARGURA}:{ALTURA},setsar=1[v];"
        "[v][1:v]overlay=0:0:shortest=1:format=auto,format=yuv420p[saida]"
    )
    return [
        FFMPEG,
        "-nostdin",
        "-v",
        "error",
        "-y",
        "-i",
        str(video),
        "-loop",
        "1",
        "-i",
        str(moldura),
        "-filter_complex",
        filtro,
        "-map",
        "[saida]",
        "-map",
        "0:a?",
        "-shortest",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "21",
        "-profile:v",
        "high",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(saida),
    ]


def aplicar_moldura(video, moldura, saida):
    subprocess.run(
        comando_moldura(video, moldura, saida),
        check=True,
        capture_output=True,
        timeout=900,
    )
    return Path(saida)


def montar_reels(pasta):
    pasta = Path(pasta)
    spec = json.loads((pasta / "post-foto.json").read_text(encoding="utf-8"))
    if not spec.get("video"):
        raise ValueError("post-foto.json sem o campo video")
    original = pasta / spec["video"]
    if not original.exists():
        raise FileNotFoundError(original)
    html = pasta / "moldura.html"
    if not html.exists():
        raise FileNotFoundError(f"{html} (gere com o modelo do cliente antes)")
    png = capturar(html, pasta / "moldura.png", LARGURA, ALTURA, transparente=True)
    return aplicar_moldura(original, png, pasta / "video.mp4")


def main():
    if len(sys.argv) != 2:
        sys.exit("uso: python -m ferramentas.video <pasta-do-post>")
    try:
        print(montar_reels(sys.argv[1]))
    except (ValueError, FileNotFoundError) as erro:
        sys.exit(f"erro: {erro}")


if __name__ == "__main__":
    main()
