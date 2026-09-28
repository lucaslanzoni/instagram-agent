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

Reels (vídeo): em vez de "foto", o post-foto.json traz "video" e "capa":
  {"modelo": "adesivos", "video": "original.mov", "textos": {"etiqueta": "...", "pilula": "..."},
   "capa": {"modelo": "encarte", "foto": "capa-foto.jpg", "posicao": "50% 40%", "textos": {...}}}
Gera moldura.html (camada transparente 1080x1920, fica o vídeo inteiro) e slide-1.html (capa
1080x1920). Depois: `uv run python -m ferramentas.video <pasta>` e `... -m ferramentas.renderizar <pasta>`.
Só o modelo "adesivos" serve de moldura: é o que menos cobre o vídeo.

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
MODELOS_VIDEO = {"adesivos"}

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


def pagina(classe, conteudo, altura, padding=None, transparente=False):
    estilo = (
        f"height:{altura}px"
        + (f";padding:{padding}" if padding else "")
        + (";background:transparent" if transparente else "")
    )
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
        "300px 88px 380px" if story else "88px 88px 80px",
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


def adesivos(foto, pos, t, story, elemento="em-cima"):
    """Sem foto (foto=None), vira a moldura transparente de um vídeo.
    elemento="embaixo" leva o sol-disco para o canto de baixo, quando em cima ele cobre um rosto."""
    h = 1920 if story else 1350
    y_ad, y_pil = (330, 440) if story else (110, 90)
    sol = f"top:{y_ad - 40}px" if elemento != "embaixo" else f"bottom:{y_pil - 40}px"
    imagem = f'<img class="foto" src="{foto}" style="object-position:{pos}">' if foto else ""
    return pagina(
        "bg-creme cheia" if foto else "cheia",
        f'''
{imagem}
<div class="adesivo" style="left:70px;top:{y_ad}px;transform:rotate(-6deg)">{t["etiqueta"]}</div>
<img class="elemento" src="{M}/elementos/sol-disco/fundo-creme/sol-02-sol-inteiro.svg" style="width:230px;right:40px;{sol};z-index:4" alt="">
<div class="pilula" style="left:70px;bottom:{y_pil}px">{logo("creme", 40)}<span>{t["pilula"]}</span></div>''',
        h,
        transparente=not foto,
    )


GERADORES = {
    "foto-cheia": foto_cheia,
    "encarte": encarte,
    "meio-a-meio": meio_a_meio,
    "adesivos": adesivos,
}


def _conferir(pasta, spec, com_foto=True):
    modelo = spec.get("modelo")
    if modelo not in MODELOS:
        raise ValueError(f"modelo desconhecido: {modelo}. Use um de {sorted(MODELOS)}")
    faltando = [k for k in MODELOS[modelo] if not spec.get("textos", {}).get(k)]
    if faltando:
        raise ValueError(f"textos faltando para {modelo}: {faltando}")
    textos = {k: html.escape(v) for k, v in spec["textos"].items()}
    if not com_foto:
        return GERADORES[modelo], None, textos
    foto = pasta / spec["foto"]
    if not foto.exists():
        raise FileNotFoundError(foto)
    return GERADORES[modelo], foto.resolve().as_uri(), textos


def gerar_reels(pasta, spec):
    if spec["modelo"] not in MODELOS_VIDEO:
        raise ValueError(f"moldura de vídeo só com {sorted(MODELOS_VIDEO)}")
    if not (pasta / spec["video"]).exists():
        raise FileNotFoundError(pasta / spec["video"])
    if not spec.get("capa"):
        raise ValueError("reels precisa do campo capa (modelo, foto, textos)")
    fn, _, textos = _conferir(pasta, spec, com_foto=False)
    fn_capa, foto_capa, textos_capa = _conferir(pasta, spec["capa"])
    moldura, capa = pasta / "moldura.html", pasta / "slide-1.html"
    moldura.write_text(fn(None, "", textos, True), encoding="utf-8")
    capa.write_text(
        fn_capa(foto_capa, spec["capa"].get("posicao", "50% 40%"), textos_capa, True),
        encoding="utf-8",
    )
    return [moldura, capa]


def gerar(pasta, story=False):
    pasta = pathlib.Path(pasta)
    spec = json.loads((pasta / "post-foto.json").read_text(encoding="utf-8"))
    if spec.get("video"):
        return gerar_reels(pasta, spec)
    fn, foto, textos = _conferir(pasta, spec)
    extra = {"elemento": spec["elemento"]} if spec.get("elemento") else {}
    saidas = [pasta / "slide-1.html"]
    saidas[0].write_text(
        fn(foto, spec.get("posicao", "50% 40%"), textos, False, **extra),
        encoding="utf-8",
    )
    if story:
        saidas.append(pasta / "story.html")
        saidas[1].write_text(
            fn(foto, spec.get("posicao", "50% 40%"), textos, True, **extra),
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
