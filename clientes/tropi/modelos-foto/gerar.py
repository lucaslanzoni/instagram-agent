#!/usr/bin/env python3
"""Modelos de post com foto da Tropi (aprovados por Lucas em 2026-09-28).

Lê `post-foto.json` na pasta do post e escreve `slide-1.html` (post 1080x1350) e,
com --story, `story.html` (1080x1920). Depois é o fluxo normal:
`uv run python -m ferramentas.renderizar <pasta-do-post>`.

post-foto.json:
  {"modelo": "encarte", "foto": "foto.jpg", "posicao": "45% 40%",
   "textos": {"rotulo": "...", "titulo": "...", "apoio": "..."}}

Modelos e textos:
  foto-cheia    rotulo, titulo, apoio         disco disponível, garimpo, aviso rápido
  encarte       rotulo, titulo, apoio         indicação de disco, evento com texto
  meio-a-meio   rotulo, titulo, cta           lançamentos chegando, anúncio com data
  adesivos      etiqueta, pilula              evento ao vivo, bastidor, stories do dia
(O modelo "disco", foto dentro do vinil, foi descartado.)

Uso
  uv run python clientes/tropi/modelos-foto/gerar.py clientes/tropi/2026-10/posts/10-feira-de-discos [--story]
"""

import argparse
import html
import json
import pathlib
import sys

M = "file:///Users/Lucas/Documents/Freelas/tropi-discos/marca"
CSS = "file:///Users/Lucas/Code/freelas/instagram-agent/clientes/tropi/cafe-goiaba.css"
MODELOS = {
    "foto-cheia": ("rotulo", "titulo", "apoio"),
    "encarte": ("rotulo", "titulo", "apoio"),
    "meio-a-meio": ("rotulo", "titulo", "cta"),
    "adesivos": ("etiqueta", "pilula"),
}

ESTILO = """<style>
.foto { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; z-index:0; }
.cheia { padding:0 !important; }
.painel { position:absolute; left:0; right:0; background:var(--tropi-creme); color:var(--tropi-cafe);
  padding:44px 88px 56px; display:flex; flex-direction:column; gap:18px; z-index:3; }
.adesivo { position:absolute; z-index:4; font-family:var(--tropi-fonte-titulo); font-weight:800; font-size:44px; line-height:1;
  background:var(--tropi-goiaba); color:var(--tropi-cafe); border:5px solid var(--tropi-cafe); border-radius:999px;
  padding:22px 40px; box-shadow:0 10px 0 var(--tropi-cafe); }
.pilula { position:absolute; z-index:4; display:flex; align-items:center; gap:24px; background:var(--tropi-cafe);
  color:var(--tropi-creme); border-radius:999px; padding:20px 40px 20px 30px; font-weight:700; font-size:30px; }
.pilula img { height:40px; }
</style>"""


def cabecalho():
    return f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Hanken+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
<link href="{CSS}" rel="stylesheet">
{ESTILO}
</head>
"""


def logo(cor, h=58):
    return f'<img class="logo" style="height:{h}px" src="{M}/logo/final/logo/tropi-logo-{cor}.svg" alt="Tropi Discos">'


def pagina(classe, conteudo, altura, padding=None):
    estilo = f"height:{altura}px" + (f";padding:{padding}" if padding else "")
    return (
        cabecalho()
        + f'<body class="{classe}" style="{estilo}">\n{conteudo}\n</body></html>\n'
    )


def foto_cheia(foto, pos, t, story):
    h = 1920 if story else 1350
    return pagina(
        "bg-creme cheia",
        f'''
<img class="foto" src="{foto}" style="object-position:{pos};height:{"1180px" if story else "100%"}">
<div class="painel" style="bottom:0;padding-bottom:{"440px" if story else "56px"}">
  <div class="topo"><span class="rotulo">{t["rotulo"]}</span>{logo("cafe", 46)}</div>
  <h1 class="ttl" style="max-width:none">{t["titulo"]}</h1>
  <span class="micro">{t["apoio"]}</span>
</div>''',
        h,
    )


def encarte(foto, pos, t, story):
    h = 1920 if story else 1350
    alt_foto = 880 if story else 740
    return pagina(
        "bg-creme",
        f'''
<div class="topo">{logo("cafe")}<span class="rotulo">{t["rotulo"]}</span></div>
<div style="position:relative">
  <div style="height:{alt_foto}px;border:6px solid var(--tropi-cafe);border-radius:26px;overflow:hidden;box-shadow:0 26px 50px rgba(60,39,34,.28)">
    <img src="{foto}" style="width:100%;height:100%;object-fit:cover;object-position:{pos};display:block">
  </div>
  <img src="{M}/elementos/mascote-disco/fundo-creme/mascote-02-piscadinha.svg" style="position:absolute;width:210px;right:-40px;bottom:-60px;z-index:4" alt="">
</div>
<div class="bloco" style="gap:14px"><h2 class="ttl" style="max-width:18ch">{t["titulo"]}</h2><span class="micro">{t["apoio"]}</span></div>
<div class="rodape"><span class="handle">@tropi_discos</span></div>''',
        h,
        "260px 88px 420px" if story else "88px 88px 80px",
    )


def meio_a_meio(foto, pos, t, story):
    h = 1920 if story else 1350
    alt_foto = 1000 if story else 780
    return pagina(
        "bg-cafe cheia",
        f'''
<img src="{foto}" style="position:absolute;left:0;top:0;width:100%;height:{alt_foto}px;object-fit:cover;object-position:{pos}">
<div style="position:absolute;left:0;right:0;top:{alt_foto}px;bottom:0;padding:48px 88px {"420px" if story else "80px"};display:flex;flex-direction:column;gap:20px">
  <div class="topo">{logo("creme", 46)}<span class="rotulo">{t["rotulo"]}</span></div>
  <h2 class="ttl" style="max-width:none">{t["titulo"]}</h2>
  <span class="cta" style="font-size:30px;padding:20px 40px">{t["cta"]}</span>
</div>''',
        h,
    )


def adesivos(foto, pos, t, story):
    h = 1920 if story else 1350
    y_ad, y_pil = (330, 440) if story else (110, 90)
    return pagina(
        "bg-creme cheia",
        f'''
<img class="foto" src="{foto}" style="object-position:{pos}">
<div class="adesivo" style="left:70px;top:{y_ad}px;transform:rotate(-6deg)">{t["etiqueta"]}</div>
<img class="elemento" src="{M}/elementos/sol-disco/fundo-creme/sol-02-sol-inteiro.svg" style="width:230px;right:40px;top:{y_ad - 40}px;z-index:4" alt="">
<div class="pilula" style="left:70px;bottom:{y_pil}px">{logo("creme", 40)}<span>{t["pilula"]}</span></div>''',
        h,
    )


GERADORES = {
    "foto-cheia": foto_cheia,
    "encarte": encarte,
    "meio-a-meio": meio_a_meio,
    "adesivos": adesivos,
}


def gerar(pasta, story=False):
    pasta = pathlib.Path(pasta)
    spec = json.loads((pasta / "post-foto.json").read_text(encoding="utf-8"))
    modelo = spec["modelo"]
    if modelo not in MODELOS:
        raise ValueError(f"modelo desconhecido: {modelo}. Use um de {sorted(MODELOS)}")
    faltando = [k for k in MODELOS[modelo] if not spec.get("textos", {}).get(k)]
    if faltando:
        raise ValueError(f"textos faltando para {modelo}: {faltando}")
    foto = pasta / spec["foto"]
    if not foto.exists():
        raise FileNotFoundError(foto)
    textos = {k: html.escape(v) for k, v in spec["textos"].items()}
    fn = GERADORES[modelo]
    saidas = [pasta / "slide-1.html"]
    saidas[0].write_text(
        fn(foto.resolve().as_uri(), spec.get("posicao", "50% 40%"), textos, False),
        encoding="utf-8",
    )
    if story:
        saidas.append(pasta / "story.html")
        saidas[1].write_text(
            fn(foto.resolve().as_uri(), spec.get("posicao", "50% 40%"), textos, True),
            encoding="utf-8",
        )
    return saidas


def main():
    ap = argparse.ArgumentParser(
        description="Gera o slide de um post com foto da Tropi."
    )
    ap.add_argument("pasta")
    ap.add_argument(
        "--story", action="store_true", help="gera também story.html (1080x1920)"
    )
    args = ap.parse_args()
    try:
        for s in gerar(args.pasta, args.story):
            print(s)
    except (ValueError, FileNotFoundError) as erro:
        sys.exit(f"erro: {erro}")


if __name__ == "__main__":
    main()
