#!/usr/bin/env python3
"""manifesto.py - junta os posts de um mês num manifesto.json e publica no site.

Uso
  uv run python -m ferramentas.manifesto clientes/tropi/2026-10 --site site
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

FORMATOS = {"carrossel": (2, 10), "estatico": (1, 1)}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATA_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MES_RE = re.compile(r"^\d{4}-\d{2}$")
LIMITE_LEGENDA = 2200


def _imagens(pasta):
    numeros = sorted(int(p.stem) for p in pasta.glob("*.jpg") if p.stem.isdigit())
    return [f"{pasta.name}/{n}.jpg" for n in numeros]


def ler_post(pasta):
    pasta = Path(pasta)
    meta = json.loads((pasta / "post.json").read_text(encoding="utf-8"))
    arquivo_legenda = pasta / "legenda.md"
    legenda = (
        arquivo_legenda.read_text(encoding="utf-8").strip()
        if arquivo_legenda.exists()
        else ""
    )
    return {
        "id": pasta.name,
        "numero": meta.get("numero"),
        "tema": meta.get("tema", ""),
        "formato": meta.get("formato"),
        "data_sugerida": meta.get("data_sugerida", ""),
        "alt": meta.get("alt", ""),
        "legenda": legenda,
        "imagens": _imagens(pasta),
    }


def validar_post(post):
    erros = []
    pid = post.get("id") or "?"
    if not ID_RE.match(pid):
        erros.append(
            f"{pid}: id da pasta deve ter só letras minúsculas sem acento, números e hífen"
        )
    numero = post.get("numero")
    if not isinstance(numero, int) or isinstance(numero, bool) or numero < 1:
        erros.append(f"{pid}: numero deve ser inteiro maior que zero")
    faixa = FORMATOS.get(post.get("formato"))
    if faixa is None:
        erros.append(f"{pid}: formato deve ser carrossel ou estatico")
    else:
        minimo, maximo = faixa
        n = len(post.get("imagens", []))
        if not minimo <= n <= maximo:
            erros.append(
                f"{pid}: {post['formato']} precisa de {minimo} a {maximo} imagem(ns), tem {n}"
            )
    legenda = post.get("legenda", "")
    if not legenda:
        erros.append(f"{pid}: legenda.md vazia ou ausente")
    elif len(legenda) > LIMITE_LEGENDA:
        erros.append(
            f"{pid}: legenda com {len(legenda)} caracteres, o limite é {LIMITE_LEGENDA}"
        )
    data = post.get("data_sugerida", "")
    if data and not DATA_RE.match(data):
        erros.append(f"{pid}: data_sugerida deve ser AAAA-MM-DD")
    return erros


def montar_manifesto(pasta_mes, cliente):
    pasta_mes = Path(pasta_mes)
    mes = pasta_mes.name
    erros = (
        [] if MES_RE.match(mes) else [f"a pasta do mês deve se chamar AAAA-MM, é {mes}"]
    )
    pasta_posts = pasta_mes / "posts"
    posts = []
    if pasta_posts.is_dir():
        posts = [
            ler_post(p)
            for p in sorted(pasta_posts.iterdir())
            if (p / "post.json").exists()
        ]
    if not posts:
        erros.append("nenhum post com post.json em posts/")
    for post in posts:
        erros.extend(validar_post(post))
    numeros = [p["numero"] for p in posts if isinstance(p["numero"], int)]
    repetidos = sorted({n for n in numeros if numeros.count(n) > 1})
    if repetidos:
        erros.append(f"numeros repetidos: {repetidos}")
    if erros:
        raise ValueError("\n".join(erros))
    posts.sort(key=lambda p: p["numero"])
    return {
        "cliente": cliente["slug"],
        "nome": cliente["nome"],
        "arroba": cliente["arroba"],
        "mes": mes,
        "posts": posts,
    }


def publicar(pasta_mes, raiz_site, cliente):
    pasta_mes, raiz_site = Path(pasta_mes), Path(raiz_site)
    manifesto = montar_manifesto(pasta_mes, cliente)
    base_cliente = raiz_site / "clientes" / cliente["slug"]
    destino = base_cliente / manifesto["mes"]
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)
    for post in manifesto["posts"]:
        for relativo in post["imagens"]:
            alvo = destino / relativo
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pasta_mes / "posts" / relativo, alvo)
    saida = destino / "manifesto.json"
    saida.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    arquivo_indice = base_cliente / "indice.json"
    indice = (
        json.loads(arquivo_indice.read_text(encoding="utf-8"))
        if arquivo_indice.exists()
        else {}
    )
    meses = sorted(set(indice.get("meses", [])) | {manifesto["mes"]})
    arquivo_indice.write_text(
        json.dumps(
            {"nome": cliente["nome"], "arroba": cliente["arroba"], "meses": meses},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return saida


def main():
    ap = argparse.ArgumentParser(description="Publica os posts de um mês no site.")
    ap.add_argument("pasta_mes", help="clientes/<slug>/<AAAA-MM>")
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    pasta_mes = Path(args.pasta_mes)
    cliente = json.loads(
        (pasta_mes.parent / "cliente.json").read_text(encoding="utf-8")
    )
    try:
        saida = publicar(pasta_mes, args.site, cliente)
    except ValueError as erro:
        sys.exit(f"manifesto recusado:\n{erro}")
    print(saida)


if __name__ == "__main__":
    main()
