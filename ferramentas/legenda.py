#!/usr/bin/env python3
"""legenda.py - verifica uma legenda de Instagram em PT-BR.

Mostra o que o feed exibe antes do "mais" (cerca de 125 caracteres) e roda as
checagens que importam: tamanho, primeira linha, gancho concreto, hashtags,
posição das hashtags, links, pedido único e emoji.

Derivado de caption.py, do pacote instagram-agent-skill de Jake Schincariol
(MIT). Ver THIRD_PARTY.md.

Uso
  uv run python -m ferramentas.legenda legenda.md
  uv run python -m ferramentas.legenda legenda.md --json
"""

import argparse
import json
import re
import sys
import textwrap
import unicodedata

LIMITE = 2200
CORTE = 125
LIMITE_HASHTAGS = 5

PALAVRA_RE = re.compile("[^\\W_]+(?:['\\u2019'-][^\\W_]+)*")
HASHTAG_RE = re.compile(r"(?:^|\s)(#[^\W_]\w*)")
LINK_RE = re.compile(
    r"https?://\S+|\bwww\.\S+|\b[a-z0-9-]+\.(?:com\.br|com|br|io|net|org|app)\b(?:/\S*)?",
    re.IGNORECASE,
)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿️]")
CONCRETO_RE = re.compile(r"\d|(?<!^)\b[A-ZÀ-ÖØ-Þ][a-zß-öø-ÿ]{2,}", re.MULTILINE)

PEDIDOS = [
    (re.compile(r"\bcoment[ae]\b|\bcomentar\b", re.I), "comentar"),
    (re.compile(r"\b(?:dm|direct)\b", re.I), "chamar no direct"),
    (re.compile(r"\bsalv(?:a|e|ar)\b", re.I), "salvar"),
    (re.compile(r"\bcompartilh\w*|\bmanda pr[ao]\b", re.I), "compartilhar"),
    (re.compile(r"\b(?:segue|siga)\b", re.I), "seguir"),
    (re.compile(r"\blink na bio\b", re.I), "link na bio"),
    (re.compile(r"\barrast[ae]\b", re.I), "arrastar"),
    (
        re.compile(
            r"\bconta pra gente\b|\bme conta\b|\bqual (?:é o |é a )?(?:seu|sua)\b", re.I
        ),
        "responder",
    ),
]

HASHTAGS_GENERICAS = {
    "#viral",
    "#fyp",
    "#explore",
    "#explorar",
    "#foryou",
    "#trending",
    "#instagood",
    "#love",
    "#amor",
    "#follow",
    "#sigam",
    "#like4like",
    "#reels",
    "#instadaily",
}


def _nfc(texto):
    return unicodedata.normalize("NFC", texto or "")


def contar_palavras(texto):
    return len(PALAVRA_RE.findall(_nfc(texto)))


def janela_visivel(texto, corte=CORTE):
    """O que o feed mostra. O Instagram corta no meio da palavra, então aqui também."""
    plano = _nfc(texto).strip()
    return plano if len(plano) <= corte else plano[:corte]


def analisar(texto, corte=CORTE):
    limpo = _nfc(texto).strip()
    caracteres = len(limpo)
    linhas = limpo.split("\n")
    primeira = linhas[0].strip() if linhas else ""
    tags = HASHTAG_RE.findall(limpo)
    links = LINK_RE.findall(limpo)
    emoji = EMOJI_RE.findall(limpo)
    janela = janela_visivel(limpo, corte)
    pedidos = [nome for padrao, nome in PEDIDOS if padrao.search(limpo)]
    genericas = [t for t in tags if t.lower() in HASHTAGS_GENERICAS]

    checagens = []

    def add(nome, status, detalhe):
        checagens.append({"checagem": nome, "status": status, "detalhe": detalhe})

    add(
        "TAMANHO",
        "FALHA" if caracteres > LIMITE else "OK",
        f"{caracteres} / {LIMITE} caracteres",
    )

    if not primeira:
        add("PRIMEIRA LINHA", "FALHA", "a legenda começa com linha vazia")
    elif primeira.startswith(("#", "@")):
        add(
            "PRIMEIRA LINHA",
            "FALHA",
            "começa com hashtag ou menção; é o lugar da frase de gancho",
        )
    elif len(primeira) > corte:
        add(
            "PRIMEIRA LINHA",
            "ATENÇÃO",
            f"{len(primeira)} caracteres; o feed corta em {corte} no meio da ideia",
        )
    else:
        add("PRIMEIRA LINHA", "OK", f"{len(primeira)} caracteres, aparece inteira")

    concretos = CONCRETO_RE.findall(janela)
    add(
        "GANCHO CONCRETO",
        "OK" if concretos else "ATENÇÃO",
        f"{len(concretos)} número(s) ou nome(s) antes do corte"
        + ("" if concretos else "; nada concreto antes do 'mais'"),
    )

    if len(tags) > LIMITE_HASHTAGS:
        add("HASHTAGS", "FALHA", f"{len(tags)} hashtags; o limite é {LIMITE_HASHTAGS}")
    elif genericas:
        add(
            "HASHTAGS",
            "ATENÇÃO",
            f"{len(genericas)} genérica(s): {', '.join(genericas[:3])}",
        )
    else:
        add("HASHTAGS", "OK", f"{len(tags)} hashtag(s)")

    if tags and any(
        re.search(r"(?:^|\s)" + re.escape(t) + r"(?!\w)", janela) for t in tags
    ):
        add("POSIÇÃO DAS TAGS", "ATENÇÃO", "hashtag dentro dos 125 caracteres visíveis")
    else:
        add("POSIÇÃO DAS TAGS", "OK", "hashtags depois do corte")

    add(
        "LINKS",
        "ATENÇÃO" if links else "OK",
        f"{len(links)} link(s) no texto; link em legenda não é clicável, usar 'link na bio'"
        if links
        else "sem link no texto",
    )

    if len(pedidos) == 1:
        add("UM PEDIDO", "OK", f"um pedido: {pedidos[0]}")
    elif not pedidos:
        add("UM PEDIDO", "ATENÇÃO", "nenhum pedido; decidir para que serve o post")
    else:
        add(
            "UM PEDIDO",
            "ATENÇÃO",
            f"{len(pedidos)} pedidos ({', '.join(pedidos)}); dois pedidos valem nenhum",
        )

    densidade = len(emoji) * 100 / max(caracteres, 1)
    add(
        "EMOJI",
        "ATENÇÃO" if densidade > 4 else "OK",
        f"{len(emoji)} emoji, {densidade:.1f} a cada 100 caracteres",
    )

    falhas = sum(1 for c in checagens if c["status"] == "FALHA")
    atencoes = sum(1 for c in checagens if c["status"] == "ATENÇÃO")
    veredito = "CORRIGIR" if falhas else ("REVISAR" if atencoes else "PRONTA")

    return {
        "caracteres": caracteres,
        "visivel": janela,
        "cortada": caracteres > corte,
        "hashtags": tags,
        "pedidos": pedidos,
        "checagens": checagens,
        "veredito": veredito,
    }


def imprimir(a, saida=sys.stdout, largura=52):
    print(
        f"\nLEGENDA  ·  {a['caracteres']} / {LIMITE}  ·  {len(a['hashtags'])} hashtags",
        file=saida,
    )
    print("\n  O QUE O FEED MOSTRA", file=saida)
    print("  +" + "-" * (largura + 2) + "+", file=saida)
    linhas = []
    for bruta in a["visivel"].split("\n"):
        linhas.extend(textwrap.wrap(bruta, largura) or [""])
    for linha in linhas[:8]:
        print(f"  | {linha:<{largura}} |", file=saida)
    print(
        "  +" + "-" * (largura + 2) + ("+ ... mais" if a["cortada"] else "+"),
        file=saida,
    )
    for c in a["checagens"]:
        print(f"  {c['status']:<8} {c['checagem']:<17} {c['detalhe']}", file=saida)
    print(f"  VEREDITO  {a['veredito']}\n", file=saida)


def main():
    ap = argparse.ArgumentParser(description="Verifica uma legenda de Instagram.")
    ap.add_argument("entrada", help="arquivo da legenda, ou - para stdin")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    texto = (
        sys.stdin.read()
        if args.entrada == "-"
        else open(args.entrada, encoding="utf-8").read()
    )
    a = analisar(texto)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        imprimir(a)
    sys.exit(0 if a["veredito"] == "PRONTA" else 1)


if __name__ == "__main__":
    main()
