#!/usr/bin/env python3
"""humanizar.py - tira as marcas de texto de máquina de um rascunho em PT-BR.

Passes, nesta ordem:
  1. INVISÍVEIS    apaga ou normaliza caracteres que teclado nenhum produz.
  2. TIPOGRÁFICOS  travessão -> vírgula, aspas curvas -> retas, etc.
  3. LEXICAIS      troca frases e palavras do léxico por equivalentes simples.
Depois SINALIZA, sem reescrever:
  - estruturas de texto de máquina ("não é X, é Y", superlativos, etc.)
  - termos proibidos do cliente (bloco "## Proibidas" do voz.md)

Derivado de humanize.py, do pacote instagram-agent-skill de Jake Schincariol
(MIT). Ver THIRD_PARTY.md.

Uso
  uv run python -m ferramentas.humanizar rascunho.txt --voz clientes/tropi/voz.md --relatorio
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

LEXICO = Path(__file__).with_name("lexico_base_pt.json")
URL_RE = re.compile(r"https?://\S+|www\.\S+|\S+@\S+\.\S+")
FRASE_RE = re.compile(r"[^.!?\n]+[.!?]*")


def carregar_lexico(caminho=LEXICO):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def ler_proibidas(texto_voz):
    proibidas, dentro = [], False
    for linha in texto_voz.splitlines():
        if linha.startswith("## "):
            dentro = linha[3:].strip().lower() == "proibidas"
            continue
        item = linha.strip()
        if dentro and item.startswith("- "):
            termo = item[2:].strip()
            if termo:
                proibidas.append(termo)
    return proibidas


def _cp(spec):
    if "-" in spec:
        a, b = spec.split("-")
        return (int(a[2:], 16), int(b[2:], 16))
    return int(spec[2:], 16)


def _proteger_urls(texto):
    achadas = []

    def guardar(m):
        achadas.append(m.group(0))
        return f"\x00URL{len(achadas) - 1}\x00"

    return URL_RE.sub(guardar, texto), achadas


def _restaurar_urls(texto, achadas):
    for i, url in enumerate(achadas):
        texto = texto.replace(f"\x00URL{i}\x00", url)
    return texto


def passe_invisiveis(texto, lexico):
    achados = []
    for item in lexico["invisiveis"]:
        cp = _cp(item["cp"])
        if isinstance(cp, tuple):
            padrao = "[" + re.escape(chr(cp[0])) + "-" + re.escape(chr(cp[1])) + "]"
        else:
            padrao = re.escape(chr(cp))
        n = len(re.findall(padrao, texto))
        if n:
            achados.append(
                {
                    "nome": f"{item['cp']} {item['nome']}",
                    "ocorrencias": n,
                    "acao": item["acao"],
                }
            )
            texto = re.sub(padrao, "" if item["acao"] == "apagar" else " ", texto)
    soltos = [c for c in texto if unicodedata.category(c) == "Cf" and c != "\x00"]
    if soltos:
        achados.append(
            {
                "nome": "outros caracteres invisíveis",
                "ocorrencias": len(soltos),
                "acao": "apagar",
            }
        )
        texto = "".join(
            c for c in texto if unicodedata.category(c) != "Cf" or c == "\x00"
        )
    return texto, achados


def passe_tipografico(texto, lexico):
    achados = []
    for item in lexico["tipograficos"]:
        ch = item["de"]
        n = texto.count(ch)
        if not n:
            continue
        achados.append({"nome": f"{ch} {item['nome']}", "ocorrencias": n})
        if ch == "—":
            texto = re.sub(r"\s*—\s*", ", ", texto)
        elif ch == "–":
            texto = re.sub(r"\s*–\s*(?=\d)", "-", texto)
            texto = re.sub(r"\s+–\s+", ", ", texto)
            texto = texto.replace("–", "-")
        else:
            texto = texto.replace(ch, item["para"])
    texto = re.sub(r",\s*([,.;:!?])", r"\1", texto)
    texto = re.sub(r",\s*\n", "\n", texto)
    return texto, achados


def _mesma_caixa(origem, troca):
    if not troca:
        return troca
    if origem.isupper() and len(origem) > 1:
        return troca.upper()
    if origem[0].isupper():
        return troca[0].upper() + troca[1:]
    return troca


def _padrao_termo(termo):
    return re.compile(
        r"(?<!\w)" + re.escape(termo).replace(r"\ ", r"\s+") + r"(?!\w)", re.IGNORECASE
    )


def passe_lexical(texto, lexico):
    achados = []
    itens = sorted(
        lexico["frases"] + lexico["palavras"],
        key=lambda i: len(i["buscar"]),
        reverse=True,
    )
    for item in itens:
        padrao = _padrao_termo(item["buscar"])
        encontrados = padrao.findall(texto)
        if not encontrados:
            continue
        achados.append(
            {
                "buscar": item["buscar"],
                "trocar": item["trocar"] or "(apagado)",
                "ocorrencias": len(encontrados),
                "familia": item["familia"],
            }
        )
        texto = padrao.sub(
            lambda m, t=item["trocar"]: _mesma_caixa(m.group(0), t), texto
        )
    texto = re.sub(r"[ \t]{2,}", " ", texto)
    texto = re.sub(r"(?m)^[ \t]*(?:[,.;:]+[ \t]*)+", "", texto)
    texto = re.sub(r"(?m)^[ \t](?=\S)", "", texto)
    texto = re.sub(r"\s+([,.;:!?])", r"\1", texto)
    texto = re.sub(r",\s*([,.;:!?])", r"\1", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto, achados


def varrer_estruturas(texto, lexico):
    sinais = []
    for item in lexico["estruturas"]:
        encontrados = re.findall(item["regex"], texto)
        if encontrados:
            sinais.append(
                {
                    "id": item["id"],
                    "nome": item["nome"],
                    "ocorrencias": len(encontrados),
                    "correcao": item["correcao"],
                }
            )
    tamanhos = [len(f.split()) for f in FRASE_RE.findall(texto) if len(f.split()) > 2]
    if len(tamanhos) >= 4:
        media = sum(tamanhos) / len(tamanhos)
        var = sum((n - media) ** 2 for n in tamanhos) / len(tamanhos)
        cv = (var**0.5) / media if media else 0
        if cv < 0.35:
            sinais.append(
                {
                    "id": "frases-iguais",
                    "nome": f"Frases do mesmo tamanho (variação {cv:.2f})",
                    "ocorrencias": len(tamanhos),
                    "correcao": "Quebrar uma frase ao meio e deixar outra mais longa.",
                }
            )
    return sinais


def buscar_proibidas(texto, proibidas):
    achados = []
    for termo in proibidas:
        n = len(_padrao_termo(termo).findall(texto))
        if n:
            achados.append({"termo": termo, "ocorrencias": n})
    return achados


def restaurar_maiusculas(original, texto):
    inicios = re.findall(r"(?:^|[.!?]\s+|\n)\s*([^\W\d_])", original)
    if not inicios or sum(1 for c in inicios if c.isupper()) * 2 < len(inicios):
        return texto
    return re.sub(
        r"(^|[.!?]\s+|\n)(\s*)([^\W\d_])",
        lambda m: m.group(1) + m.group(2) + m.group(3).upper(),
        texto,
    )


def humanizar(texto, lexico, proibidas=()):
    original = unicodedata.normalize("NFC", texto)
    texto, urls = _proteger_urls(original)
    texto, inv = passe_invisiveis(texto, lexico)
    texto, tipo = passe_tipografico(texto, lexico)
    texto, lexi = passe_lexical(texto, lexico)
    if lexi:
        texto = restaurar_maiusculas(original, texto)
    texto = _restaurar_urls(texto, urls)
    return texto.strip() + "\n", {
        "invisiveis": inv,
        "tipograficos": tipo,
        "lexicais": lexi,
        "estruturas": varrer_estruturas(texto, lexico),
        "proibidas": buscar_proibidas(texto, list(proibidas)),
    }


def imprimir_relatorio(rel, saida=sys.stderr):
    def titulo(t):
        print(f"\n{t}\n" + "-" * len(t), file=saida)

    titulo("RELATÓRIO DO HUMANIZADOR")
    for h in rel["invisiveis"]:
        print(
            f"  {h['ocorrencias']:>3}x  invisível   {h['nome']} -> {h['acao']}",
            file=saida,
        )
    for h in rel["tipograficos"]:
        print(f"  {h['ocorrencias']:>3}x  tipográfico {h['nome']}", file=saida)
    for h in rel["lexicais"]:
        print(
            f"  {h['ocorrencias']:>3}x  léxico      {h['buscar']} -> {h['trocar']}",
            file=saida,
        )
    if rel["estruturas"]:
        titulo("ESTRUTURAS (reescrever à mão)")
        for h in rel["estruturas"]:
            print(
                f"  {h['ocorrencias']:>3}x  {h['nome']}\n        {h['correcao']}",
                file=saida,
            )
    if rel["proibidas"]:
        titulo("PROIBIDAS DO CLIENTE (reescrever à mão)")
        for h in rel["proibidas"]:
            print(f"  {h['ocorrencias']:>3}x  {h['termo']}", file=saida)
    if not any(rel.values()):
        print("  Nada a corrigir.", file=saida)
    print("", file=saida)


def main():
    ap = argparse.ArgumentParser(
        description="Tira marcas de texto de máquina de um rascunho."
    )
    ap.add_argument("entrada", help="arquivo, ou - para stdin")
    ap.add_argument("--voz", help="voz.md do cliente, para ler o bloco ## Proibidas")
    ap.add_argument("--saida", help="grava o texto limpo aqui")
    ap.add_argument("--relatorio", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    texto = (
        sys.stdin.read()
        if args.entrada == "-"
        else open(args.entrada, encoding="utf-8").read()
    )
    proibidas = (
        ler_proibidas(Path(args.voz).read_text(encoding="utf-8")) if args.voz else []
    )
    limpo, rel = humanizar(texto, carregar_lexico(), proibidas)
    if args.json:
        print(
            json.dumps({"texto": limpo, "relatorio": rel}, indent=2, ensure_ascii=False)
        )
    elif args.saida:
        Path(args.saida).write_text(limpo, encoding="utf-8")
    else:
        sys.stdout.write(limpo)
    if args.relatorio:
        imprimir_relatorio(rel)
    sys.exit(1 if rel["proibidas"] else 0)


if __name__ == "__main__":
    main()
