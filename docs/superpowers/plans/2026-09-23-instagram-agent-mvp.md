# Instagram Agent MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o MVP do agente de conteúdo para Instagram (piloto Tropi): ferramentas de texto e imagem, site estático com acesso por e-mail, formulário de marca e página de aprovação, e as 7 skills que ligam tudo.

**Architecture:** Repositório público `instagram-agent`. Ferramentas em Python só com biblioteca padrão (`ferramentas/`), testadas com pytest. Site estático em HTML/CSS/JS sem framework e sem build (`site/`), com lógica pura em módulos testados por `node --test` e a parte de tela em módulos separados. Publicado no GitHub Pages via Actions. As skills em `.claude/skills/` orquestram o fluxo formulário → fichas → pauta → produção → entrega → retorno, rodando na sessão local do Claude Code de Lucas.

**Tech Stack:** Python 3.12+ (stdlib) + pytest via `uv`; Node 18+ (`node --test`); Chrome headless + `sips` (macOS) para imagens; JSZip 3.10.1 via cdnjs; GitHub Pages + Actions.

**Spec:** `docs/superpowers/specs/2026-09-23-instagram-agent-mvp-design.md`

## Global Constraints

- Nada conecta ao Instagram. Nenhuma chave de API, nenhum serviço de terceiros além do GitHub.
- Python: só biblioteca padrão em `ferramentas/`. pytest é dependência de desenvolvimento. Rodar com `uv run pytest`.
- Site: HTML/CSS/JS puro, módulos ES, sem build. Único script externo: `https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js`. Fontes via Google Fonts.
- Marca do site (consultoria, direção "Editorial direto"): fundo `#0A0A0A`, texto `#FAFAFA`, acento `#EF4C43` (1-2 elementos por tela), muted `#8C8C8C`; títulos Big Shoulders Display 800-900 caixa alta; corpo Public Sans 400-500.
- Textos da interface em PT-BR, sem emoji, sem exclamação.
- Imagens: 1080x1350, JPG qualidade 85.
- Legenda: máximo 2200 caracteres; corte do feed em 125; no máximo 5 hashtags.
- Carrossel: 2 a 10 imagens no manifesto (a skill mira 4 a 10 slides). Post estático: exatamente 1 imagem.
- Texto sempre normalizado em NFC antes de contar ou comparar.
- Arquivos derivados do pacote de Jake Schincariol citam a origem e o aviso MIT fica em `THIRD_PARTY.md`.
- Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Push no GitHub: `gh auth switch --user lucaslanzoni` antes e `gh auth switch --user lucaslanzoni-taqtile` depois.

## Review Focus

- Texto em NFD (comum ao copiar de arquivos no macOS) tem que contar "Ninguém" como 1 palavra e "ã" como 1 caractere; teste em Task 1.
- Navegador que bloqueia armazenamento (aba anônima do Safari) não pode quebrar formulário nem aprovação; o dado fica em memória e a página avisa; teste em Task 5.
- Pasta de post com acento, espaço ou maiúscula no nome quebra caminho de imagem no site; o manifesto tem que recusar com mensagem clara; teste em Task 4.
- Link de aprovação com `?mes=` inexistente ou cliente sem mês publicado tem que mostrar o mês mais recente ou uma mensagem, nunca tela vazia; teste em Task 7.
- Aprovação salva de uma versão anterior do mês (post removido depois de revisão) não pode reaparecer no `aprovacao.json`; teste em Task 7.

---

## Estrutura de arquivos

```
instagram-agent/
  README.md                         o que é, como rodar testes, como publicar
  LICENSE                           MIT, Lucas Lanzoni
  THIRD_PARTY.md                    aviso MIT de Jake Schincariol
  pyproject.toml                    pytest como dev; pythonpath "."
  package.json                      "type": "module", script de teste
  .gitignore
  .github/workflows/pages.yml       publica site/ no GitHub Pages
  ferramentas/
    __init__.py
    legenda.py                      verificação de legenda (Task 1)
    humanizar.py                    humanizador + proibidas do cliente (Task 2)
    lexico_base_pt.json             léxico PT-BR inicial (Task 2)
    renderizar.py                   HTML -> JPG (Task 3)
    manifesto.py                    posts -> manifesto.json + publicação no site (Task 4)
  modelos/
    ficha-marca.md                  molde da ficha da marca (Task 8)
    ficha-voz.md                    molde da ficha de voz (Task 8)
  .claude/skills/
    ig-onboarding/SKILL.md          (Task 8)
    ig-humano/SKILL.md              (Task 8)
    ig-legenda/SKILL.md             (Task 8)
    ig-pauta/SKILL.md + ganchos.md  (Task 9)
    ig-carrossel/SKILL.md           (Task 9)
    ig-post/SKILL.md                (Task 9)
    ig-entrega/SKILL.md             (Task 9)
  site/
    index.html                      tela de e-mail + menu do cliente (Task 5)
    acesso.json                     e-mail -> cliente (Task 5)
    assets/
      estilo.css                    (Tasks 5, 6, 7)
      armazenamento.js              localStorage tolerante (Task 5)
      sessao.js                     sessão do cliente (Task 5)
      baixar.js                     download de arquivo (Task 5)
      acesso-logica.js              lógica pura de acesso (Task 5)
      acesso.js                     tela de acesso (Task 5)
      perguntas.js                  17 perguntas + 12 arquétipos (Task 6)
      formulario-logica.js          lógica pura do formulário (Task 6)
      formulario.js                 tela do formulário (Task 6)
      aprovacao-logica.js           lógica pura da aprovação (Task 7)
      aprovacao.js                  tela da aprovação (Task 7)
    formulario/index.html           (Task 6)
    aprovacao/index.html            (Task 7)
    clientes/tropi/indice.json      nome, @, meses publicados (Task 5)
  clientes/tropi/
    cliente.json                    (Task 9)
    visual.md                       sistema visual para os slides (Task 9)
  tests/
    test_legenda.py  test_humanizar.py  test_renderizar.py  test_manifesto.py  test_skills.py
    js/acesso.test.js  js/armazenamento.test.js  js/formulario.test.js  js/aprovacao.test.js
    fixtures/demo/                  cliente de demonstração para testar a página (Task 7)
```

---

### Task 1: Base do repositório e verificação de legenda (`legenda.py`)

**Files:**
- Create: `README.md`, `LICENSE`, `THIRD_PARTY.md`, `pyproject.toml`, `.gitignore`, `ferramentas/__init__.py`, `ferramentas/legenda.py`
- Test: `tests/test_legenda.py`

**Interfaces:**
- Produces: `ferramentas.legenda.contar_palavras(texto: str) -> int`, `janela_visivel(texto: str, corte: int = 125) -> str`, `analisar(texto: str, corte: int = 125) -> dict` com chaves `caracteres, visivel, cortada, hashtags, pedidos, checagens (lista de {checagem, status, detalhe}), veredito` (`PRONTA` | `REVISAR` | `CORRIGIR`); status das checagens: `OK` | `ATENÇÃO` | `FALHA`. CLI: `uv run python -m ferramentas.legenda arquivo.md [--json]`, sai com 0 só se `PRONTA`.

- [ ] **Step 1: Criar a base do repositório**

`pyproject.toml`:
```toml
[project]
name = "instagram-agent"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = ["pytest>=8.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

`.gitignore`:
```
.DS_Store
__pycache__/
*.pyc
.venv/
.pytest_cache/
node_modules/
tests/fixtures/**/*.jpg
tests/fixtures/**/*.png
```

`ferramentas/__init__.py`:
```python
"""Ferramentas do agente de Instagram: legenda, humanizador, renderização e manifesto."""
```

`LICENSE`:
```
MIT License

Copyright (c) 2026 Lucas Lanzoni

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

`THIRD_PARTY.md`:
```markdown
# Código e conteúdo de terceiros

Partes deste projeto derivam do pacote **instagram-agent-skill**, de Jake
Schincariol (https://github.com/Jakeschincariol/instagram-agent-skill), sob
licença MIT:

- `ferramentas/legenda.py` — derivado de `skills/ig-caption/caption.py`
- `ferramentas/humanizar.py` e `ferramentas/lexico_base_pt.json` — derivados de
  `skills/ig-human/humanize.py` e `skills/ig-human/slop.json`
- `.claude/skills/ig-pauta`, `ig-carrossel`, `ig-legenda`, `ig-humano` — regras
  adaptadas de `ig-plan`, `ig-carousel`, `ig-caption` e `ig-human`

Aviso original:

MIT License

Copyright (c) 2026 Jake Schincariol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

`README.md`:
```markdown
# Instagram Agent

Braço de criação de conteúdo para Instagram da consultoria. O cliente responde
um formulário; Claude gera ficha da marca e ficha de voz, monta a pauta do mês,
produz posts estáticos e carrosséis e publica uma página de aprovação.

Nada se conecta ao Instagram. Quem publica é o humano.

Spec: `docs/superpowers/specs/2026-09-23-instagram-agent-mvp-design.md`

## Testes

    uv run pytest
    node --test

## Site local

    cd site && python3 -m http.server 8000
    # abrir http://localhost:8000

## Publicar

O site em `site/` é publicado no GitHub Pages a cada push no `main`
(`.github/workflows/pages.yml`). Aviso: repositório público; o portão de e-mail
filtra a tela, não protege os arquivos.
```

- [ ] **Step 2: Escrever os testes que falham**

`tests/test_legenda.py`:
```python
import unicodedata

from ferramentas.legenda import CORTE, analisar, contar_palavras, janela_visivel


def status(analise, nome):
    return next(c["status"] for c in analise["checagens"] if c["checagem"] == nome)


def test_conta_palavras_com_acento():
    assert contar_palavras("Ninguém te conta isso.") == 4


def test_conta_palavras_em_texto_nfd():
    nfd = unicodedata.normalize("NFD", "Ninguém te conta isso.")
    assert contar_palavras(nfd) == 4


def test_janela_corta_em_125():
    assert len(janela_visivel("a" * 200)) == CORTE


def test_janela_nfd_conta_caractere_composto_uma_vez():
    nfd = unicodedata.normalize("NFD", "ã" * 130)
    assert janela_visivel(nfd) == "ã" * 125


def test_hashtag_com_acento_e_uma_so():
    a = analisar("Disco novo na loja.\n\n#músicabrasileira #vinil")
    assert a["hashtags"] == ["#músicabrasileira", "#vinil"]


def test_seis_hashtags_falha():
    a = analisar("Disco novo.\n\n#a1 #b2 #c3 #d4 #e5 #f6")
    assert status(a, "HASHTAGS") == "FALHA"
    assert a["veredito"] == "CORRIGIR"


def test_um_pedido_passa():
    a = analisar("Afim, de Zé Ibarra, chegou em vinil vermelho.\n\nLink na bio.")
    assert status(a, "UM PEDIDO") == "OK"


def test_dois_pedidos_alerta():
    a = analisar("Afim chegou.\n\nSalva esse post e link na bio.")
    assert status(a, "UM PEDIDO") == "ATENÇÃO"


def test_primeira_linha_com_hashtag_falha():
    a = analisar("#vinil disco novo")
    assert status(a, "PRIMEIRA LINHA") == "FALHA"


def test_legenda_boa_fica_pronta():
    texto = (
        "Afim, o segundo disco de Zé Ibarra, chegou em vinil vermelho.\n\n"
        "Cordas, sopros e produção dele com Lucas Nunes.\n\n"
        "Link na bio.\n\n"
        "#zeibarra #vinil #mpb"
    )
    a = analisar(texto)
    assert a["veredito"] == "PRONTA", a["checagens"]
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `uv run pytest tests/test_legenda.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'ferramentas.legenda'`

- [ ] **Step 4: Implementar `ferramentas/legenda.py`**

```python
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

PALAVRA_RE = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*")
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
    (re.compile(r"\bconta pra gente\b|\bme conta\b|\bqual (?:é o |é a )?(?:seu|sua)\b", re.I),
     "responder"),
]

HASHTAGS_GENERICAS = {
    "#viral", "#fyp", "#explore", "#explorar", "#foryou", "#trending", "#instagood",
    "#love", "#amor", "#follow", "#sigam", "#like4like", "#reels", "#instadaily",
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

    add("TAMANHO", "FALHA" if caracteres > LIMITE else "OK",
        f"{caracteres} / {LIMITE} caracteres")

    if not primeira:
        add("PRIMEIRA LINHA", "FALHA", "a legenda começa com linha vazia")
    elif primeira.startswith(("#", "@")):
        add("PRIMEIRA LINHA", "FALHA", "começa com hashtag ou menção; é o lugar da frase de gancho")
    elif len(primeira) > corte:
        add("PRIMEIRA LINHA", "ATENÇÃO",
            f"{len(primeira)} caracteres; o feed corta em {corte} no meio da ideia")
    else:
        add("PRIMEIRA LINHA", "OK", f"{len(primeira)} caracteres, aparece inteira")

    concretos = CONCRETO_RE.findall(janela)
    add("GANCHO CONCRETO", "OK" if concretos else "ATENÇÃO",
        f"{len(concretos)} número(s) ou nome(s) antes do corte"
        + ("" if concretos else "; nada concreto antes do 'mais'"))

    if len(tags) > LIMITE_HASHTAGS:
        add("HASHTAGS", "FALHA", f"{len(tags)} hashtags; o limite é {LIMITE_HASHTAGS}")
    elif genericas:
        add("HASHTAGS", "ATENÇÃO", f"{len(genericas)} genérica(s): {', '.join(genericas[:3])}")
    else:
        add("HASHTAGS", "OK", f"{len(tags)} hashtag(s)")

    if tags and any(re.search(r"(?:^|\s)" + re.escape(t) + r"(?!\w)", janela) for t in tags):
        add("POSIÇÃO DAS TAGS", "ATENÇÃO", "hashtag dentro dos 125 caracteres visíveis")
    else:
        add("POSIÇÃO DAS TAGS", "OK", "hashtags depois do corte")

    add("LINKS", "ATENÇÃO" if links else "OK",
        f"{len(links)} link(s) no texto; link em legenda não é clicável, usar 'link na bio'"
        if links else "sem link no texto")

    if len(pedidos) == 1:
        add("UM PEDIDO", "OK", f"um pedido: {pedidos[0]}")
    elif not pedidos:
        add("UM PEDIDO", "ATENÇÃO", "nenhum pedido; decidir para que serve o post")
    else:
        add("UM PEDIDO", "ATENÇÃO", f"{len(pedidos)} pedidos ({', '.join(pedidos)}); dois pedidos valem nenhum")

    densidade = len(emoji) * 100 / max(caracteres, 1)
    add("EMOJI", "ATENÇÃO" if densidade > 4 else "OK",
        f"{len(emoji)} emoji, {densidade:.1f} a cada 100 caracteres")

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
    print(f"\nLEGENDA  ·  {a['caracteres']} / {LIMITE}  ·  {len(a['hashtags'])} hashtags", file=saida)
    print("\n  O QUE O FEED MOSTRA", file=saida)
    print("  +" + "-" * (largura + 2) + "+", file=saida)
    linhas = []
    for bruta in a["visivel"].split("\n"):
        linhas.extend(textwrap.wrap(bruta, largura) or [""])
    for linha in linhas[:8]:
        print(f"  | {linha:<{largura}} |", file=saida)
    print("  +" + "-" * (largura + 2) + ("+ ... mais" if a["cortada"] else "+"), file=saida)
    for c in a["checagens"]:
        print(f"  {c['status']:<8} {c['checagem']:<17} {c['detalhe']}", file=saida)
    print(f"  VEREDITO  {a['veredito']}\n", file=saida)


def main():
    ap = argparse.ArgumentParser(description="Verifica uma legenda de Instagram.")
    ap.add_argument("entrada", help="arquivo da legenda, ou - para stdin")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    texto = sys.stdin.read() if args.entrada == "-" else open(args.entrada, encoding="utf-8").read()
    a = analisar(texto)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        imprimir(a)
    sys.exit(0 if a["veredito"] == "PRONTA" else 1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Rodar e ver passar**

Run: `uv run pytest tests/test_legenda.py -v`
Expected: 10 passed

- [ ] **Step 6: Commit**

```bash
git add README.md LICENSE THIRD_PARTY.md pyproject.toml .gitignore uv.lock ferramentas/ tests/test_legenda.py
git commit -m "feat(ferramentas): verificação de legenda em PT-BR derivada de caption.py

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
(Se `uv.lock` não tiver sido criado, remover do `git add`.)

---

### Task 2: Humanizador com léxico PT-BR e proibidas do cliente (`humanizar.py`)

**Files:**
- Create: `ferramentas/humanizar.py`, `ferramentas/lexico_base_pt.json`
- Test: `tests/test_humanizar.py`

**Interfaces:**
- Produces: `carregar_lexico(caminho=LEXICO) -> dict`; `ler_proibidas(texto_voz: str) -> list[str]` (lê itens `- termo` sob o título exato `## Proibidas`); `humanizar(texto: str, lexico: dict, proibidas: list[str] = ()) -> tuple[str, dict]`, relatório com chaves `invisiveis, tipograficos, lexicais, estruturas, proibidas`; `proibidas` é lista de `{termo, ocorrencias}`; `estruturas` é lista de `{id, nome, ocorrencias, correcao}`. CLI: `uv run python -m ferramentas.humanizar entrada.txt --voz clientes/<slug>/voz.md [--saida arq] [--relatorio] [--json]`, sai com 1 se houver proibidas.

- [ ] **Step 1: Escrever os testes que falham**

`tests/test_humanizar.py`:
```python
from ferramentas.humanizar import carregar_lexico, humanizar, ler_proibidas

LEX = carregar_lexico()

VOZ = """# Ficha de voz

## O que a marca não usa
- texto livre que não é lista de máquina

## Proibidas
- aproveite
- garanta o seu

## Exemplos
- Ruim: x | Bom: y
"""


def test_remove_caractere_invisivel():
    limpo, rel = humanizar("Dis​co novo.", LEX)
    assert limpo.strip() == "Disco novo."
    assert rel["invisiveis"]


def test_travessao_vira_virgula():
    limpo, _ = humanizar("Afim — o disco novo.", LEX)
    assert limpo.strip() == "Afim, o disco novo."


def test_troca_abertura_de_ia_preservando_maiuscula():
    limpo, rel = humanizar("No mundo de hoje, discos voltaram.", LEX)
    assert limpo.strip() == "Hoje, discos voltaram."
    assert rel["lexicais"][0]["buscar"] == "no mundo de hoje"


def test_apaga_muleta_e_recapitaliza():
    limpo, _ = humanizar("Vale ressaltar que o disco saiu em vinil.", LEX)
    assert limpo.strip() == "O disco saiu em vinil."


def test_texto_limpo_nao_muda():
    limpo, rel = humanizar("Disco novo na loja.", LEX)
    assert limpo.strip() == "Disco novo na loja."
    assert not any(rel.values())


def test_sinaliza_estrutura_nao_e_x_e_y():
    _, rel = humanizar("Não é só um disco, é uma história.", LEX)
    assert "nao-e-x-e-y" in [e["id"] for e in rel["estruturas"]]


def test_le_proibidas_so_do_bloco_certo():
    assert ler_proibidas(VOZ) == ["aproveite", "garanta o seu"]


def test_proibidas_sao_sinalizadas_e_nao_trocadas():
    texto = "Aproveite, garanta o seu hoje."
    limpo, rel = humanizar(texto, LEX, ler_proibidas(VOZ))
    assert limpo.strip() == texto
    assert rel["proibidas"] == [
        {"termo": "aproveite", "ocorrencias": 1},
        {"termo": "garanta o seu", "ocorrencias": 1},
    ]


def test_proibida_nao_casa_dentro_de_outra_palavra():
    _, rel = humanizar("O aproveitamento foi bom.", LEX, ["aproveita"])
    assert rel["proibidas"] == []
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/test_humanizar.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'ferramentas.humanizar'`

- [ ] **Step 3: Criar `ferramentas/lexico_base_pt.json`**

```json
{
  "versao": "1.0",
  "nota": "Léxico inicial em PT-BR. Invisíveis e tipográficos são corrigidos sozinhos; palavras e frases são trocadas por equivalentes simples; estruturas só são sinalizadas para reescrita. A tradução completa do léxico de Jake é a Fase 2.",
  "invisiveis": [
    {"cp": "U+200B", "nome": "ESPAÇO DE LARGURA ZERO", "acao": "apagar"},
    {"cp": "U+200C", "nome": "NÃO-JUNTOR DE LARGURA ZERO", "acao": "apagar"},
    {"cp": "U+200D", "nome": "JUNTOR DE LARGURA ZERO", "acao": "apagar"},
    {"cp": "U+2060", "nome": "JUNTOR DE PALAVRA", "acao": "apagar"},
    {"cp": "U+FEFF", "nome": "BOM / ESPAÇO SEM QUEBRA DE LARGURA ZERO", "acao": "apagar"},
    {"cp": "U+00AD", "nome": "HÍFEN SUAVE", "acao": "apagar"},
    {"cp": "U+180E", "nome": "SEPARADOR DE VOGAL MONGOL", "acao": "apagar"},
    {"cp": "U+E0000-U+E007F", "nome": "CARACTERES DE TAG UNICODE", "acao": "apagar"},
    {"cp": "U+00A0", "nome": "ESPAÇO SEM QUEBRA", "acao": "espaco"},
    {"cp": "U+202F", "nome": "ESPAÇO ESTREITO SEM QUEBRA", "acao": "espaco"},
    {"cp": "U+2007", "nome": "ESPAÇO DE ALGARISMO", "acao": "espaco"},
    {"cp": "U+2009", "nome": "ESPAÇO FINO", "acao": "espaco"},
    {"cp": "U+200A", "nome": "ESPAÇO CAPILAR", "acao": "espaco"}
  ],
  "tipograficos": [
    {"de": "—", "nome": "TRAVESSÃO", "para": ", "},
    {"de": "–", "nome": "MEIA-RISCA", "para": "-"},
    {"de": "“", "nome": "ASPA CURVA DE ABERTURA", "para": "\""},
    {"de": "”", "nome": "ASPA CURVA DE FECHAMENTO", "para": "\""},
    {"de": "‘", "nome": "APÓSTROFO CURVO DE ABERTURA", "para": "'"},
    {"de": "’", "nome": "APÓSTROFO CURVO DE FECHAMENTO", "para": "'"},
    {"de": "…", "nome": "RETICÊNCIAS DE UM CARACTERE", "para": "..."},
    {"de": "•", "nome": "MARCADOR", "para": "-"}
  ],
  "frases": [
    {"buscar": "no mundo de hoje", "trocar": "hoje", "familia": "aberturas"},
    {"buscar": "nos dias de hoje", "trocar": "hoje", "familia": "aberturas"},
    {"buscar": "no cenário atual", "trocar": "hoje", "familia": "aberturas"},
    {"buscar": "vale ressaltar que", "trocar": "", "familia": "muletas"},
    {"buscar": "vale destacar que", "trocar": "", "familia": "muletas"},
    {"buscar": "é importante destacar que", "trocar": "", "familia": "muletas"},
    {"buscar": "é importante ressaltar que", "trocar": "", "familia": "muletas"},
    {"buscar": "é importante lembrar que", "trocar": "", "familia": "muletas"},
    {"buscar": "sem sombra de dúvidas", "trocar": "", "familia": "muletas"},
    {"buscar": "não é exagero dizer que", "trocar": "", "familia": "muletas"},
    {"buscar": "mergulhar de cabeça", "trocar": "entrar", "familia": "verbos"}
  ],
  "palavras": [
    {"buscar": "alavancar", "trocar": "aumentar", "familia": "verbos"},
    {"buscar": "potencializar", "trocar": "aumentar", "familia": "verbos"},
    {"buscar": "desvendar", "trocar": "entender", "familia": "verbos"},
    {"buscar": "robusto", "trocar": "sólido", "familia": "adjetivos"},
    {"buscar": "crucial", "trocar": "importante", "familia": "adjetivos"},
    {"buscar": "imprescindível", "trocar": "necessário", "familia": "adjetivos"}
  ],
  "estruturas": [
    {"id": "nao-e-x-e-y", "regex": "(?i)\\bnão (?:é|era|foi) (?:só |apenas |somente )?[^.!?\\n]{2,60}[,;.] (?:é|era|foi)\\b", "nome": "\"Não é X, é Y\"", "correcao": "Dizer a única coisa que importa. Cortar a metade de preparação."},
    {"id": "nao-so-mas-tambem", "regex": "(?i)\\bnão (?:só|apenas|somente)\\b[^.!?\\n]{2,80}\\bmas também\\b", "nome": "\"Não só X, mas também Y\"", "correcao": "Separar em duas frases ou cortar a metade mais fraca."},
    {"id": "nao-e-sobre", "regex": "(?i)\\bnão é sobre [^.!?\\n]{2,60}[,;.] é sobre\\b", "nome": "\"Não é sobre X, é sobre Y\"", "correcao": "Afirmar direto o que é."},
    {"id": "exclamacoes", "regex": "!{2,}", "nome": "Exclamações em sequência", "correcao": "No máximo uma, e só se a marca usa."},
    {"id": "revelacao", "regex": "(?im)^(?:o resultado|a verdade|o segredo|a resposta)\\?\\s*$", "nome": "Pergunta de revelação (\"O resultado?\")", "correcao": "Dizer o resultado sem suspense fabricado."},
    {"id": "superlativos", "regex": "(?i)\\b(?:incrível|imperdível|sensacional|surpreendente|arrasador)\\b", "nome": "Superlativo vazio", "correcao": "Trocar por um fato: número, nome, detalhe."}
  ]
}
```

- [ ] **Step 4: Implementar `ferramentas/humanizar.py`**

```python
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
            achados.append({"nome": f"{item['cp']} {item['nome']}", "ocorrencias": n, "acao": item["acao"]})
            texto = re.sub(padrao, "" if item["acao"] == "apagar" else " ", texto)
    soltos = [c for c in texto if unicodedata.category(c) == "Cf" and c != "\x00"]
    if soltos:
        achados.append({"nome": "outros caracteres invisíveis", "ocorrencias": len(soltos), "acao": "apagar"})
        texto = "".join(c for c in texto if unicodedata.category(c) != "Cf" or c == "\x00")
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
    return re.compile(r"(?<!\w)" + re.escape(termo).replace(r"\ ", r"\s+") + r"(?!\w)", re.IGNORECASE)


def passe_lexical(texto, lexico):
    achados = []
    itens = sorted(lexico["frases"] + lexico["palavras"], key=lambda i: len(i["buscar"]), reverse=True)
    for item in itens:
        padrao = _padrao_termo(item["buscar"])
        encontrados = padrao.findall(texto)
        if not encontrados:
            continue
        achados.append({"buscar": item["buscar"], "trocar": item["trocar"] or "(apagado)",
                        "ocorrencias": len(encontrados), "familia": item["familia"]})
        texto = padrao.sub(lambda m, t=item["trocar"]: _mesma_caixa(m.group(0), t), texto)
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
            sinais.append({"id": item["id"], "nome": item["nome"], "ocorrencias": len(encontrados),
                           "correcao": item["correcao"]})
    tamanhos = [len(f.split()) for f in FRASE_RE.findall(texto) if len(f.split()) > 2]
    if len(tamanhos) >= 4:
        media = sum(tamanhos) / len(tamanhos)
        var = sum((n - media) ** 2 for n in tamanhos) / len(tamanhos)
        cv = (var ** 0.5) / media if media else 0
        if cv < 0.35:
            sinais.append({"id": "frases-iguais", "nome": f"Frases do mesmo tamanho (variação {cv:.2f})",
                           "ocorrencias": len(tamanhos),
                           "correcao": "Quebrar uma frase ao meio e deixar outra mais longa."})
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
    return re.sub(r"(^|[.!?]\s+|\n)(\s*)([^\W\d_])",
                  lambda m: m.group(1) + m.group(2) + m.group(3).upper(), texto)


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
        print(f"  {h['ocorrencias']:>3}x  invisível   {h['nome']} -> {h['acao']}", file=saida)
    for h in rel["tipograficos"]:
        print(f"  {h['ocorrencias']:>3}x  tipográfico {h['nome']}", file=saida)
    for h in rel["lexicais"]:
        print(f"  {h['ocorrencias']:>3}x  léxico      {h['buscar']} -> {h['trocar']}", file=saida)
    if rel["estruturas"]:
        titulo("ESTRUTURAS (reescrever à mão)")
        for h in rel["estruturas"]:
            print(f"  {h['ocorrencias']:>3}x  {h['nome']}\n        {h['correcao']}", file=saida)
    if rel["proibidas"]:
        titulo("PROIBIDAS DO CLIENTE (reescrever à mão)")
        for h in rel["proibidas"]:
            print(f"  {h['ocorrencias']:>3}x  {h['termo']}", file=saida)
    if not any(rel.values()):
        print("  Nada a corrigir.", file=saida)
    print("", file=saida)


def main():
    ap = argparse.ArgumentParser(description="Tira marcas de texto de máquina de um rascunho.")
    ap.add_argument("entrada", help="arquivo, ou - para stdin")
    ap.add_argument("--voz", help="voz.md do cliente, para ler o bloco ## Proibidas")
    ap.add_argument("--saida", help="grava o texto limpo aqui")
    ap.add_argument("--relatorio", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    texto = sys.stdin.read() if args.entrada == "-" else open(args.entrada, encoding="utf-8").read()
    proibidas = ler_proibidas(Path(args.voz).read_text(encoding="utf-8")) if args.voz else []
    limpo, rel = humanizar(texto, carregar_lexico(), proibidas)
    if args.json:
        print(json.dumps({"texto": limpo, "relatorio": rel}, indent=2, ensure_ascii=False))
    elif args.saida:
        Path(args.saida).write_text(limpo, encoding="utf-8")
    else:
        sys.stdout.write(limpo)
    if args.relatorio:
        imprimir_relatorio(rel)
    sys.exit(1 if rel["proibidas"] else 0)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Rodar e ver passar**

Run: `uv run pytest tests/test_humanizar.py -v`
Expected: 9 passed

- [ ] **Step 6: Commit**

```bash
git add ferramentas/humanizar.py ferramentas/lexico_base_pt.json tests/test_humanizar.py
git commit -m "feat(ferramentas): humanizador PT-BR com proibidas por cliente

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Renderização HTML → JPG (`renderizar.py`)

**Files:**
- Create: `ferramentas/renderizar.py`
- Test: `tests/test_renderizar.py`

**Interfaces:**
- Produces: `CHROME: str`; `ordenar_slides(arquivos: list[Path]) -> list[Path]` (só `slide-N.html`, ordem numérica); `renderizar(html: Path, saida: Path, largura=1080, altura=1350, qualidade=85) -> Path`; `dimensoes(imagem: Path) -> tuple[int, int]`; `renderizar_post(pasta: Path) -> list[Path]` (gera `1.jpg..N.jpg` e apaga JPG numerado além de N). CLI: `uv run python -m ferramentas.renderizar <pasta-do-post>`.

- [ ] **Step 1: Escrever os testes que falham**

`tests/test_renderizar.py`:
```python
import shutil
from pathlib import Path

import pytest

from ferramentas.renderizar import CHROME, dimensoes, ordenar_slides, renderizar, renderizar_post

TEM_CHROME = Path(CHROME).exists() and shutil.which("sips") is not None
HTML = ("<!DOCTYPE html><html><body style='margin:0;width:1080px;height:1350px;"
        "background:#FB5607'></body></html>")


def test_ordena_slides_por_numero_e_ignora_outros():
    arquivos = [Path("slide-10.html"), Path("slide-2.html"), Path("slide-1.html"), Path("capa.html")]
    assert [p.name for p in ordenar_slides(arquivos)] == ["slide-1.html", "slide-2.html", "slide-10.html"]


@pytest.mark.skipif(not TEM_CHROME, reason="precisa de Chrome e sips (macOS)")
def test_renderiza_jpg_1080x1350(tmp_path):
    html = tmp_path / "slide-1.html"
    html.write_text(HTML, encoding="utf-8")
    saida = renderizar(html, tmp_path / "1.jpg")
    assert saida.exists()
    assert not (tmp_path / "1.png").exists()
    assert dimensoes(saida) == (1080, 1350)


@pytest.mark.skipif(not TEM_CHROME, reason="precisa de Chrome e sips (macOS)")
def test_renderizar_post_apaga_jpg_sobrando(tmp_path):
    (tmp_path / "slide-1.html").write_text(HTML, encoding="utf-8")
    (tmp_path / "3.jpg").write_bytes(b"velho")
    saidas = renderizar_post(tmp_path)
    assert [p.name for p in saidas] == ["1.jpg"]
    assert not (tmp_path / "3.jpg").exists()


def test_post_sem_slides_da_erro(tmp_path):
    with pytest.raises(FileNotFoundError):
        renderizar_post(tmp_path)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/test_renderizar.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'ferramentas.renderizar'`

- [ ] **Step 3: Implementar `ferramentas/renderizar.py`**

```python
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

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
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
        [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
         f"--window-size={largura},{altura}", "--virtual-time-budget=5000",
         f"--screenshot={png}", html.resolve().as_uri()],
        check=True, capture_output=True, timeout=120,
    )
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(qualidade), str(png), "--out", str(saida)],
        check=True, capture_output=True, timeout=60,
    )
    png.unlink(missing_ok=True)
    return saida


def dimensoes(imagem):
    r = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(imagem)],
                       check=True, capture_output=True, text=True)
    largura = int(re.search(r"pixelWidth: (\d+)", r.stdout).group(1))
    altura = int(re.search(r"pixelHeight: (\d+)", r.stdout).group(1))
    return largura, altura


def renderizar_post(pasta):
    pasta = Path(pasta)
    slides = ordenar_slides(sorted(pasta.glob("slide-*.html")))
    if not slides:
        raise FileNotFoundError(f"nenhum slide-N.html em {pasta}")
    saidas = [renderizar(html, pasta / f"{i}.jpg") for i, html in enumerate(slides, start=1)]
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
```

- [ ] **Step 4: Rodar e ver passar**

Run: `uv run pytest tests/test_renderizar.py -v`
Expected: 4 passed (em macOS com Chrome; sem Chrome, 2 passed e 2 skipped)

- [ ] **Step 5: Commit**

```bash
git add ferramentas/renderizar.py tests/test_renderizar.py
git commit -m "feat(ferramentas): renderização de slides HTML em JPG 1080x1350

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: Manifesto do mês e publicação no site (`manifesto.py`)

**Files:**
- Create: `ferramentas/manifesto.py`
- Test: `tests/test_manifesto.py`

**Interfaces:**
- Consumes: estrutura de post `clientes/<slug>/<AAAA-MM>/posts/<id>/` com `post.json` (`numero`, `tema`, `formato` = `carrossel`|`estatico`, `data_sugerida`, `alt`), `legenda.md` e `1.jpg..N.jpg` (gerados pela Task 3). `clientes/<slug>/cliente.json` com `slug`, `nome`, `arroba`.
- Produces: `ler_post(pasta: Path) -> dict`; `validar_post(post: dict) -> list[str]`; `montar_manifesto(pasta_mes: Path, cliente: dict) -> dict` (lança `ValueError` com todas as mensagens juntas); `publicar(pasta_mes: Path, raiz_site: Path, cliente: dict) -> Path` (escreve `site/clientes/<slug>/<mes>/manifesto.json`, copia imagens para `site/clientes/<slug>/<mes>/<id>/N.jpg`, atualiza `site/clientes/<slug>/indice.json` = `{nome, arroba, meses}`). Manifesto: `{cliente, nome, arroba, mes, posts: [{id, numero, tema, formato, data_sugerida, alt, legenda, imagens: ["<id>/1.jpg", ...]}]}`. CLI: `uv run python -m ferramentas.manifesto clientes/tropi/2026-10 [--site site]`.

- [ ] **Step 1: Escrever os testes que falham**

`tests/test_manifesto.py`:
```python
import json

import pytest

from ferramentas.manifesto import montar_manifesto, publicar

CLIENTE = {"slug": "demo", "nome": "Loja Demo", "arroba": "@demo"}


def criar_post(pasta_mes, pid, numero, formato="carrossel", n_imagens=3, legenda="Legenda boa.\n\nLink na bio."):
    pasta = pasta_mes / "posts" / pid
    pasta.mkdir(parents=True)
    (pasta / "post.json").write_text(json.dumps(
        {"numero": numero, "tema": "Lançamento", "formato": formato,
         "data_sugerida": "2026-10-07", "alt": "capa do disco"}, ensure_ascii=False), encoding="utf-8")
    (pasta / "legenda.md").write_text(legenda, encoding="utf-8")
    for n in range(1, n_imagens + 1):
        (pasta / f"{n}.jpg").write_bytes(b"jpg")
    return pasta


def test_monta_manifesto_ordenado_por_numero(tmp_path):
    mes = tmp_path / "2026-10"
    criar_post(mes, "02-segundo", 2)
    criar_post(mes, "01-primeiro", 1, formato="estatico", n_imagens=1)
    m = montar_manifesto(mes, CLIENTE)
    assert m["mes"] == "2026-10"
    assert [p["id"] for p in m["posts"]] == ["01-primeiro", "02-segundo"]
    assert m["posts"][1]["imagens"] == ["02-segundo/1.jpg", "02-segundo/2.jpg", "02-segundo/3.jpg"]
    assert m["posts"][0]["legenda"] == "Legenda boa.\n\nLink na bio."


def test_carrossel_com_uma_imagem_e_recusado(tmp_path):
    mes = tmp_path / "2026-10"
    criar_post(mes, "01-curto", 1, n_imagens=1)
    with pytest.raises(ValueError, match="01-curto: carrossel precisa de 2 a 10"):
        montar_manifesto(mes, CLIENTE)


def test_formato_invalido_e_recusado(tmp_path):
    mes = tmp_path / "2026-10"
    criar_post(mes, "01-reel", 1, formato="reel")
    with pytest.raises(ValueError, match="formato deve ser carrossel ou estatico"):
        montar_manifesto(mes, CLIENTE)


def test_id_com_acento_ou_espaco_e_recusado(tmp_path):
    mes = tmp_path / "2026-10"
    criar_post(mes, "03-Afim Zé", 3)
    with pytest.raises(ValueError, match="id da pasta"):
        montar_manifesto(mes, CLIENTE)


def test_numero_repetido_e_recusado(tmp_path):
    mes = tmp_path / "2026-10"
    criar_post(mes, "01-a", 1)
    criar_post(mes, "01-b", 1)
    with pytest.raises(ValueError, match="numeros repetidos"):
        montar_manifesto(mes, CLIENTE)


def test_legenda_vazia_e_recusada(tmp_path):
    mes = tmp_path / "2026-10"
    criar_post(mes, "01-a", 1, legenda="   ")
    with pytest.raises(ValueError, match="legenda.md vazia"):
        montar_manifesto(mes, CLIENTE)


def test_publicar_copia_imagens_e_atualiza_indice(tmp_path):
    mes = tmp_path / "clientes" / "demo" / "2026-10"
    criar_post(mes, "01-a", 1, formato="estatico", n_imagens=1)
    site = tmp_path / "site"
    (site / "clientes" / "demo").mkdir(parents=True)
    (site / "clientes" / "demo" / "indice.json").write_text(
        json.dumps({"nome": "Loja Demo", "arroba": "@demo", "meses": ["2026-09"]}), encoding="utf-8")

    caminho = publicar(mes, site, CLIENTE)
    publicar(mes, site, CLIENTE)  # republicar não duplica mês

    assert caminho == site / "clientes" / "demo" / "2026-10" / "manifesto.json"
    assert (site / "clientes" / "demo" / "2026-10" / "01-a" / "1.jpg").exists()
    indice = json.loads((site / "clientes" / "demo" / "indice.json").read_text(encoding="utf-8"))
    assert indice["meses"] == ["2026-09", "2026-10"]
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/test_manifesto.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'ferramentas.manifesto'`

- [ ] **Step 3: Implementar `ferramentas/manifesto.py`**

```python
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
    legenda = arquivo_legenda.read_text(encoding="utf-8").strip() if arquivo_legenda.exists() else ""
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
        erros.append(f"{pid}: id da pasta deve ter só letras minúsculas sem acento, números e hífen")
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
            erros.append(f"{pid}: {post['formato']} precisa de {minimo} a {maximo} imagem(ns), tem {n}")
    legenda = post.get("legenda", "")
    if not legenda:
        erros.append(f"{pid}: legenda.md vazia ou ausente")
    elif len(legenda) > LIMITE_LEGENDA:
        erros.append(f"{pid}: legenda com {len(legenda)} caracteres, o limite é {LIMITE_LEGENDA}")
    data = post.get("data_sugerida", "")
    if data and not DATA_RE.match(data):
        erros.append(f"{pid}: data_sugerida deve ser AAAA-MM-DD")
    return erros


def montar_manifesto(pasta_mes, cliente):
    pasta_mes = Path(pasta_mes)
    mes = pasta_mes.name
    erros = [] if MES_RE.match(mes) else [f"a pasta do mês deve se chamar AAAA-MM, é {mes}"]
    pasta_posts = pasta_mes / "posts"
    posts = []
    if pasta_posts.is_dir():
        posts = [ler_post(p) for p in sorted(pasta_posts.iterdir()) if (p / "post.json").exists()]
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
    return {"cliente": cliente["slug"], "nome": cliente["nome"], "arroba": cliente["arroba"],
            "mes": mes, "posts": posts}


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
    saida.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    arquivo_indice = base_cliente / "indice.json"
    indice = json.loads(arquivo_indice.read_text(encoding="utf-8")) if arquivo_indice.exists() else {}
    meses = sorted(set(indice.get("meses", [])) | {manifesto["mes"]})
    arquivo_indice.write_text(json.dumps(
        {"nome": cliente["nome"], "arroba": cliente["arroba"], "meses": meses},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return saida


def main():
    ap = argparse.ArgumentParser(description="Publica os posts de um mês no site.")
    ap.add_argument("pasta_mes", help="clientes/<slug>/<AAAA-MM>")
    ap.add_argument("--site", default="site")
    args = ap.parse_args()
    pasta_mes = Path(args.pasta_mes)
    cliente = json.loads((pasta_mes.parent / "cliente.json").read_text(encoding="utf-8"))
    try:
        saida = publicar(pasta_mes, args.site, cliente)
    except ValueError as erro:
        sys.exit(f"manifesto recusado:\n{erro}")
    print(saida)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Rodar e ver passar**

Run: `uv run pytest tests/test_manifesto.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add ferramentas/manifesto.py tests/test_manifesto.py
git commit -m "feat(ferramentas): manifesto do mês e publicação no site

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Site base e acesso por e-mail

**Files:**
- Create: `package.json`, `site/index.html`, `site/acesso.json`, `site/clientes/tropi/indice.json`, `site/assets/estilo.css`, `site/assets/armazenamento.js`, `site/assets/sessao.js`, `site/assets/baixar.js`, `site/assets/acesso-logica.js`, `site/assets/acesso.js`
- Test: `tests/js/armazenamento.test.js`, `tests/js/acesso.test.js`

**Interfaces:**
- Produces:
  - `armazenamento.js`: `criarArmazenamento(backend) -> {ler(chave), gravar(chave, valor), remover(chave), persistente()}` (valores em JSON; se o backend lançar erro, passa a guardar em memória); `armazenamentoDoNavegador()`.
  - `sessao.js`: `armazenamento` (instância única), `lerSessao() -> {email, cliente} | null`, `salvarSessao({email, cliente})`, `limparSessao()`, `exigirSessao(raiz = '../') -> sessão | null` (redireciona para a raiz sem sessão).
  - `baixar.js`: `baixarBlob(nome, blob)`, `baixarJSON(nome, dados)`.
  - `acesso-logica.js`: `normalizarEmail(e) -> string`, `emailValido(e) -> boolean`, `clienteDoEmail(acesso, email) -> slug | null`.
  - `site/acesso.json`: `{"emails": {"<email>": "<slug>"}}`. `site/clientes/<slug>/indice.json`: `{nome, arroba, meses: []}`.

- [ ] **Step 1: Criar `package.json`**

```json
{
  "name": "instagram-agent-site",
  "private": true,
  "type": "module",
  "scripts": { "test": "node --test" }
}
```

- [ ] **Step 2: Escrever os testes que falham**

`tests/js/armazenamento.test.js`:
```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { criarArmazenamento } from '../../site/assets/armazenamento.js';

function fakeStorage() {
  const m = new Map();
  return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k) };
}

test('grava e lê pelo backend', () => {
  const fake = fakeStorage();
  criarArmazenamento(fake).gravar('k', { x: 1 });
  assert.deepEqual(criarArmazenamento(fake).ler('k'), { x: 1 });
});

test('backend que lança erro cai para memória sem quebrar', () => {
  const quebrado = {
    getItem() { throw new Error('bloqueado'); },
    setItem() { throw new Error('bloqueado'); },
    removeItem() { throw new Error('bloqueado'); },
  };
  const a = criarArmazenamento(quebrado);
  a.gravar('k', 'v');
  assert.equal(a.ler('k'), 'v');
  assert.equal(a.persistente(), false);
});

test('sem backend funciona em memória', () => {
  const a = criarArmazenamento(null);
  a.gravar('k', [1, 2]);
  assert.deepEqual(a.ler('k'), [1, 2]);
  assert.equal(a.persistente(), false);
});

test('valor corrompido volta null e continua persistente', () => {
  const fake = fakeStorage();
  fake.setItem('k', '{quebrado');
  const a = criarArmazenamento(fake);
  assert.equal(a.ler('k'), null);
  assert.equal(a.persistente(), true);
});

test('remover apaga', () => {
  const a = criarArmazenamento(fakeStorage());
  a.gravar('k', 1);
  a.remover('k');
  assert.equal(a.ler('k'), null);
});
```

`tests/js/acesso.test.js`:
```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { normalizarEmail, emailValido, clienteDoEmail } from '../../site/assets/acesso-logica.js';

test('normaliza espaços e maiúsculas', () => {
  assert.equal(normalizarEmail('  Lucas@Exemplo.COM '), 'lucas@exemplo.com');
  assert.equal(normalizarEmail(undefined), '');
});

test('valida formato de e-mail', () => {
  assert.equal(emailValido('a@b.co'), true);
  assert.equal(emailValido(' A@B.CO '), true);
  assert.equal(emailValido('sem-arroba.com'), false);
  assert.equal(emailValido('a@b'), false);
});

test('encontra o cliente ignorando caixa e espaços dos dois lados', () => {
  const acesso = { emails: { 'Lucas@Exemplo.com': 'tropi' } };
  assert.equal(clienteDoEmail(acesso, ' lucas@exemplo.COM'), 'tropi');
});

test('e-mail fora da lista devolve null', () => {
  assert.equal(clienteDoEmail({ emails: { 'a@b.co': 'tropi' } }, 'c@d.co'), null);
});

test('acesso sem lista devolve null', () => {
  assert.equal(clienteDoEmail({}, 'a@b.co'), null);
  assert.equal(clienteDoEmail(null, 'a@b.co'), null);
});
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `node --test`
Expected: FAIL com `Cannot find module '.../site/assets/armazenamento.js'`

- [ ] **Step 4: Implementar os módulos puros**

`site/assets/armazenamento.js`:
```js
// Guarda dados no navegador. Se o localStorage falhar (aba anônima, bloqueio),
// continua funcionando em memória e avisa por persistente() === false.
export function criarArmazenamento(backend) {
  const memoria = new Map();
  let usarMemoria = !backend;

  function lerBruto(chave) {
    if (usarMemoria) return memoria.has(chave) ? memoria.get(chave) : null;
    try {
      return backend.getItem(chave);
    } catch {
      usarMemoria = true;
      return memoria.has(chave) ? memoria.get(chave) : null;
    }
  }

  return {
    ler(chave) {
      const bruto = lerBruto(chave);
      if (bruto === null || bruto === undefined) return null;
      try {
        return JSON.parse(bruto);
      } catch {
        return null;
      }
    },
    gravar(chave, valor) {
      const bruto = JSON.stringify(valor);
      memoria.set(chave, bruto);
      if (usarMemoria) return;
      try {
        backend.setItem(chave, bruto);
      } catch {
        usarMemoria = true;
      }
    },
    remover(chave) {
      memoria.delete(chave);
      if (usarMemoria) return;
      try {
        backend.removeItem(chave);
      } catch {
        usarMemoria = true;
      }
    },
    persistente() {
      return !usarMemoria;
    },
  };
}

export function armazenamentoDoNavegador() {
  let backend = null;
  try {
    backend = globalThis.localStorage ?? null;
  } catch {
    backend = null;
  }
  return criarArmazenamento(backend);
}
```

`site/assets/acesso-logica.js`:
```js
// Portão visual por e-mail (fase de teste). Filtra a tela, não protege arquivos.
export const normalizarEmail = (email) => (email || '').trim().toLowerCase();

export const emailValido = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizarEmail(email));

export function clienteDoEmail(acesso, email) {
  const mapa = acesso?.emails || {};
  const alvo = normalizarEmail(email);
  for (const [cadastrado, cliente] of Object.entries(mapa)) {
    if (normalizarEmail(cadastrado) === alvo) return cliente;
  }
  return null;
}
```

- [ ] **Step 5: Rodar e ver passar**

Run: `node --test`
Expected: 10 tests, 10 pass

- [ ] **Step 6: Criar sessão, download, dados de acesso e índice**

`site/assets/sessao.js`:
```js
import { armazenamentoDoNavegador } from './armazenamento.js';

const CHAVE = 'ia_sessao';
export const armazenamento = armazenamentoDoNavegador();

export function lerSessao() {
  const s = armazenamento.ler(CHAVE);
  return s && s.email && s.cliente ? s : null;
}

export function salvarSessao(sessao) {
  armazenamento.gravar(CHAVE, sessao);
}

export function limparSessao() {
  armazenamento.remover(CHAVE);
}

export function exigirSessao(raiz = '../') {
  const s = lerSessao();
  if (!s) {
    location.href = raiz;
    return null;
  }
  return s;
}
```

`site/assets/baixar.js`:
```js
export function baixarBlob(nome, blob) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = nome;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function baixarJSON(nome, dados) {
  baixarBlob(nome, new Blob([JSON.stringify(dados, null, 2)], { type: 'application/json' }));
}
```

`site/acesso.json` (repositório público: este e-mail fica visível; decisão aceita por Lucas para a fase de teste):
```json
{
  "emails": {
    "lucaslanzoni.s@gmail.com": "tropi"
  }
}
```

`site/clientes/tropi/indice.json`:
```json
{
  "nome": "Tropi Discos",
  "arroba": "@tropi_discos",
  "meses": []
}
```

- [ ] **Step 7: Criar `site/assets/estilo.css`**

```css
:root {
  color-scheme: dark;
  --bg: #0A0A0A;
  --fg: #FAFAFA;
  --muted: #8C8C8C;
  --acento: #EF4C43;
  --linha: #2A2A2A;
  --cartao: #141414;
  --titulo: "Big Shoulders Display", sans-serif;
  --corpo: "Public Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--bg); color: var(--fg); font-family: var(--corpo); line-height: 1.5; }
a { color: var(--fg); }
button { font: inherit; cursor: pointer; }
[hidden] { display: none !important; }

.titulo { font-family: var(--titulo); font-weight: 900; text-transform: uppercase; letter-spacing: .01em; line-height: 1.05; margin: 0; }
.muted { color: var(--muted); }
.botao { background: var(--fg); color: var(--bg); border: 0; padding: 12px 18px; font-weight: 600; }
.botao-secundario { background: transparent; color: var(--fg); border: 1px solid var(--linha); padding: 10px 14px; font-weight: 600; }
.botao:disabled, .botao-secundario:disabled { opacity: .5; cursor: default; }
.aviso { border: 1px solid var(--acento); padding: 12px 14px; margin: 12px 0; font-size: .9rem; }
.rodape { margin-top: 40px; padding-top: 16px; border-top: 1px solid var(--linha); color: var(--muted); font-size: .75rem; }

/* acesso */
.pagina-estreita { max-width: 520px; margin: 0 auto; padding: 48px 16px 80px; }
.acesso h1 { font-size: 2.4rem; margin-bottom: 8px; }
.form-acesso { display: flex; flex-direction: column; gap: 10px; margin-top: 24px; }
.campo { width: 100%; font: inherit; padding: 12px 14px; background: var(--cartao); color: var(--fg); border: 1px solid var(--linha); }
.campo:focus, textarea:focus { outline: 2px solid var(--acento); outline-offset: 0; }
.erro { color: var(--acento); min-height: 1.4em; font-weight: 600; }
.menu { margin-top: 32px; display: flex; flex-direction: column; gap: 10px; }
.menu a { display: block; padding: 16px; background: var(--cartao); border: 1px solid var(--linha); text-decoration: none; font-weight: 600; }
.menu a:hover { border-color: var(--fg); }

/* formulário */
.secao-titulo { font-family: var(--titulo); font-weight: 800; text-transform: uppercase; font-size: 1.5rem; margin: 36px 0 4px; }
.intro { color: var(--muted); margin: 0 0 16px; }
.pergunta { background: var(--cartao); border: 1px solid var(--linha); padding: 16px; margin-bottom: 14px; }
.pergunta .texto { font-weight: 600; margin: 0 0 4px; }
.pergunta .exemplo { color: var(--muted); font-size: .85rem; margin: 0 0 12px; }
textarea { width: 100%; min-height: 96px; font: inherit; padding: 10px; background: var(--bg); color: var(--fg); border: 1px solid var(--linha); resize: vertical; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { background: transparent; color: var(--fg); border: 1px solid var(--linha); padding: 8px 12px; text-align: left; }
.chip[aria-pressed="true"] { border-color: var(--acento); background: rgba(239, 76, 67, .12); }
.progresso { font-size: .85rem; color: var(--muted); position: sticky; top: 0; background: var(--bg); padding: 8px 0; margin: 0; z-index: 2; }
.acoes { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 24px; }

/* aprovação */
.layout { display: grid; grid-template-columns: 300px 1fr; min-height: 100vh; }
.lateral { border-right: 1px solid var(--linha); padding: 24px 16px; position: sticky; top: 0; height: 100vh; overflow-y: auto; }
.lateral .marca { font-size: .7rem; letter-spacing: .16em; text-transform: uppercase; color: var(--muted); }
.lateral h1 { font-size: 2rem; margin-top: 16px; }
.lista { list-style: none; padding: 0; margin: 20px 0; display: flex; flex-direction: column; gap: 6px; }
.item { width: 100%; display: grid; grid-template-columns: 28px 44px 1fr 12px; align-items: center; gap: 10px; background: transparent; color: var(--fg); border: 1px solid transparent; padding: 6px; text-align: left; }
.item:hover, .item:focus-visible { border-color: var(--linha); }
.item .num { font-size: .75rem; color: var(--muted); }
.item img { width: 44px; aspect-ratio: 4 / 5; object-fit: cover; display: block; }
.item .tema { font-weight: 600; font-size: .9rem; }
.item .formato { display: block; font-size: .75rem; color: var(--muted); font-weight: 400; }
.ponto-status { width: 10px; height: 10px; border-radius: 50%; border: 1px solid var(--muted); }
.ponto-status[data-status="aprovado"] { background: var(--fg); border-color: var(--fg); }
.ponto-status[data-status="revisar"] { background: var(--acento); border-color: var(--acento); }
.ponto-status[data-status="descartado"] { background: transparent; border-color: var(--linha); }
.resumo { font-size: .85rem; color: var(--muted); }
.principal { padding: 24px; }
.grade { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; max-width: 900px; margin: 0 auto; }
.celula { position: relative; padding: 0; border: 0; background: var(--cartao); aspect-ratio: 4 / 5; overflow: hidden; }
.celula img { width: 100%; height: 100%; object-fit: cover; display: block; }
.selo { position: absolute; top: 8px; background: rgba(10, 10, 10, .7); color: var(--fg); font-size: .72rem; padding: 2px 8px; border-radius: 999px; }
.selo.num { left: 8px; }
.selo.formato { right: 8px; }
.celula[data-status="descartado"] img { opacity: .35; }

dialog.janela { width: min(1000px, 100vw); max-height: 100vh; padding: 0; border: 1px solid var(--linha); background: var(--bg); color: var(--fg); }
dialog.janela::backdrop { background: rgba(0, 0, 0, .8); }
.janela-corpo { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); }
.palco { position: relative; background: #000; }
.carrossel { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; }
.carrossel::-webkit-scrollbar { display: none; }
.carrossel img { flex: 0 0 100%; width: 100%; aspect-ratio: 4 / 5; object-fit: cover; scroll-snap-align: start; display: block; }
.seta { position: absolute; top: 50%; transform: translateY(-50%); background: rgba(10, 10, 10, .7); color: var(--fg); border: 0; width: 40px; height: 40px; border-radius: 50%; }
.seta.anterior { left: 8px; }
.seta.proxima { right: 8px; }
.pontos { display: flex; justify-content: center; gap: 6px; padding: 10px; }
.pontos span { width: 6px; height: 6px; border-radius: 50%; background: var(--linha); }
.pontos span.ativo { background: var(--fg); }
.painel { padding: 20px; display: flex; flex-direction: column; gap: 12px; max-height: 90vh; overflow-y: auto; }
.painel h2 { font-size: 1.6rem; }
.status-botoes { display: flex; gap: 8px; flex-wrap: wrap; }
.status-botoes button { flex: 1; background: transparent; color: var(--fg); border: 1px solid var(--linha); padding: 10px; font-weight: 600; }
.status-botoes button[aria-pressed="true"] { border-color: var(--fg); background: var(--fg); color: var(--bg); }
.status-botoes button[data-status="revisar"][aria-pressed="true"] { border-color: var(--acento); background: var(--acento); color: var(--fg); }
.mensagem { max-width: 600px; margin: 40px auto; }

@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
  .lateral { position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--linha); }
  .lista { display: none; }
  .principal { padding: 8px 0; }
  .janela-corpo { grid-template-columns: 1fr; }
  .painel { max-height: none; }
}
```

- [ ] **Step 8: Criar a tela de acesso `site/index.html` e `site/assets/acesso.js`**

`site/index.html`:
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Conteúdo para Instagram</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/estilo.css">
</head>
<body>
  <main class="pagina-estreita acesso">
    <p class="muted">Lucas Lanzoni · Conteúdo</p>
    <h1 class="titulo">Conteúdo para Instagram</h1>

    <section id="tela-entrada">
      <p class="muted">Entre com o e-mail cadastrado pela consultoria.</p>
      <form id="form-acesso" class="form-acesso" novalidate>
        <input id="email" class="campo" type="email" inputmode="email" autocomplete="email" placeholder="seu@email.com" aria-label="Seu e-mail">
        <button class="botao" type="submit">Entrar</button>
      </form>
      <p id="erro" class="erro" role="alert"></p>
    </section>

    <section id="tela-menu" hidden>
      <h2 id="nome-cliente" class="titulo"></h2>
      <p id="arroba-cliente" class="muted"></p>
      <p id="aviso-memoria" class="aviso" hidden>Este navegador não está guardando dados entre páginas. Use uma janela normal (não anônima) para não perder o que for preenchido.</p>
      <nav class="menu" id="menu"></nav>
      <p id="sem-mes" class="muted" hidden>Nenhum mês de conteúdo publicado ainda.</p>
      <button id="sair" class="botao-secundario" type="button">Sair</button>
    </section>

    <p class="rodape">Acesso restrito aos e-mails liberados pela consultoria.</p>
  </main>
  <script type="module" src="assets/acesso.js"></script>
</body>
</html>
```

`site/assets/acesso.js`:
```js
import { normalizarEmail, emailValido, clienteDoEmail } from './acesso-logica.js';
import { lerSessao, salvarSessao, limparSessao, armazenamento } from './sessao.js';

const $ = (id) => document.getElementById(id);
const NOMES_MES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

function formatarMes(mes) {
  const [ano, m] = mes.split('-');
  return `${NOMES_MES[Number(m) - 1] || mes} ${ano}`;
}

async function buscarJSON(url) {
  const r = await fetch(url, { cache: 'no-store' });
  if (!r.ok) throw new Error(`${r.status} em ${url}`);
  return r.json();
}

async function carregarAcesso() {
  try {
    return await buscarJSON('acesso.json');
  } catch {
    return null;
  }
}

function link(texto, href) {
  const a = document.createElement('a');
  a.textContent = texto;
  a.href = href;
  return a;
}

async function mostrarMenu({ cliente }) {
  $('tela-entrada').hidden = true;
  $('tela-menu').hidden = false;
  $('aviso-memoria').hidden = armazenamento.persistente();
  const menu = $('menu');
  menu.replaceChildren(link('Formulário da marca', 'formulario/'));
  let indice = null;
  try {
    indice = await buscarJSON(`clientes/${cliente}/indice.json`);
  } catch {
    indice = null;
  }
  $('nome-cliente').textContent = indice?.nome || cliente;
  $('arroba-cliente').textContent = indice?.arroba || '';
  const meses = [...(indice?.meses || [])].sort().reverse();
  for (const mes of meses) menu.append(link(`Conteúdo de ${formatarMes(mes)}`, `aprovacao/?mes=${encodeURIComponent(mes)}`));
  $('sem-mes').hidden = meses.length > 0;
}

async function tentar(valor) {
  const erro = $('erro');
  erro.textContent = '';
  const email = normalizarEmail(valor);
  if (!emailValido(email)) {
    erro.textContent = 'Digite um e-mail válido.';
    return;
  }
  const acesso = await carregarAcesso();
  if (!acesso) {
    erro.textContent = 'Não foi possível conferir o acesso agora. Tente de novo.';
    return;
  }
  const cliente = clienteDoEmail(acesso, email);
  if (!cliente) {
    erro.textContent = 'Este e-mail ainda não tem acesso. Fale com a consultoria.';
    return;
  }
  salvarSessao({ email, cliente });
  mostrarMenu({ email, cliente });
}

async function iniciar() {
  $('sair').addEventListener('click', () => {
    limparSessao();
    location.reload();
  });
  $('form-acesso').addEventListener('submit', (e) => {
    e.preventDefault();
    tentar($('email').value);
  });
  const sessao = lerSessao();
  if (sessao) {
    const acesso = await carregarAcesso();
    if (acesso && clienteDoEmail(acesso, sessao.email) === sessao.cliente) {
      mostrarMenu(sessao);
      return;
    }
    if (acesso) limparSessao();
  }
  $('email').focus();
}

iniciar();
```

- [ ] **Step 9: Conferir no navegador**

Run: `cd site && python3 -m http.server 8000` (em segundo plano), abrir `http://localhost:8000` (Playwright MCP ou navegador).
Expected:
- `teste@naoexiste.com` mostra "Este e-mail ainda não tem acesso. Fale com a consultoria."
- `  LucasLanzoni.S@gmail.com ` entra e mostra "Tropi Discos", "@tropi_discos", o link "Formulário da marca" e "Nenhum mês de conteúdo publicado ainda."
- Recarregar a página mantém o menu; "Sair" volta para a tela de e-mail.
Parar o servidor depois.

- [ ] **Step 10: Commit**

```bash
git add package.json site/ tests/js/armazenamento.test.js tests/js/acesso.test.js
git commit -m "feat(site): base do site com acesso por e-mail e armazenamento tolerante

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Formulário da marca

**Files:**
- Create: `site/assets/perguntas.js`, `site/assets/formulario-logica.js`, `site/assets/formulario.js`, `site/formulario/index.html`
- Test: `tests/js/formulario.test.js`

**Interfaces:**
- Consumes: `exigirSessao`, `armazenamento` (Task 5); `baixarJSON` (Task 5).
- Produces:
  - `perguntas.js`: `SECOES` (3 seções, 17 perguntas; cada pergunta `{id, texto, exemplo, tipo?}`; a de arquétipo tem `tipo: 'arquetipo'`), `ARQUETIPOS` (12 itens `{id, descricao}`).
  - `formulario-logica.js`: `totalPerguntas(secoes)`, `contarRespondidas(secoes, respostas)`, `alternarArquetipo(lista, id, max = 2)`, `montarRespostas({cliente, email, respostas, agora}) -> {cliente, email, gerado_em, respostas}`, `validarSecoes(secoes, arquetipos) -> string[]`.
  - Arquivo exportado `respostas-<cliente>-<AAAA-MM-DD>.json` consumido pela skill `ig-onboarding` (Task 8).

- [ ] **Step 1: Escrever os testes que falham**

`tests/js/formulario.test.js`:
```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { SECOES, ARQUETIPOS } from '../../site/assets/perguntas.js';
import { totalPerguntas, contarRespondidas, alternarArquetipo, montarRespostas, validarSecoes } from '../../site/assets/formulario-logica.js';

test('o formulário tem 3 seções e 17 perguntas válidas', () => {
  assert.equal(SECOES.length, 3);
  assert.equal(totalPerguntas(SECOES), 17);
  assert.deepEqual(validarSecoes(SECOES, ARQUETIPOS), []);
});

test('validarSecoes acha id repetido e arquétipo ausente', () => {
  const ruins = [{ id: 's', titulo: 'T', intro: 'I', perguntas: [{ id: 'a', texto: 't', exemplo: 'e' }, { id: 'a', texto: 't', exemplo: 'e' }] }];
  const problemas = validarSecoes(ruins, ARQUETIPOS);
  assert.ok(problemas.some((p) => p.includes('repetido')));
  assert.ok(problemas.some((p) => p.includes('arquétipo')));
});

test('contarRespondidas ignora espaços e lista vazia', () => {
  const respostas = { marca_frase: '  ', marca_links: 'site', voz_arquetipo: [] };
  assert.equal(contarRespondidas(SECOES, respostas), 1);
});

test('alternarArquetipo aceita no máximo 2 e desmarca', () => {
  let lista = alternarArquetipo([], 'sabio');
  lista = alternarArquetipo(lista, 'criador');
  assert.deepEqual(alternarArquetipo(lista, 'heroi'), ['sabio', 'criador']);
  assert.deepEqual(alternarArquetipo(lista, 'sabio'), ['criador']);
});

test('montarRespostas limpa vazios, apara texto e registra a data', () => {
  const dados = montarRespostas({
    cliente: 'tropi',
    email: 'a@b.co',
    respostas: { marca_frase: '  Loja de vinil  ', marca_links: '', voz_arquetipo: ['sabio'] },
    agora: new Date('2026-10-01T12:00:00Z'),
  });
  assert.deepEqual(dados, {
    cliente: 'tropi',
    email: 'a@b.co',
    gerado_em: '2026-10-01T12:00:00.000Z',
    respostas: { marca_frase: 'Loja de vinil', voz_arquetipo: ['sabio'] },
  });
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test`
Expected: FAIL com `Cannot find module '.../site/assets/perguntas.js'`

- [ ] **Step 3: Implementar `site/assets/perguntas.js`**

```js
// Perguntas do formulário de marca. Derivado do formulário Frameworks da Moxie,
// sem áudio e sem a seção de inventário.
export const ARQUETIPOS = [
  { id: 'inocente', descricao: 'A que é simples, otimista e passa confiança' },
  { id: 'explorador', descricao: 'A que busca liberdade, descoberta e o novo' },
  { id: 'sabio', descricao: 'A que sabe muito e ensina' },
  { id: 'heroi', descricao: 'A que supera desafios e inspira a vencer' },
  { id: 'fora_da_lei', descricao: 'A que provoca e quebra regra' },
  { id: 'mago', descricao: 'A que transforma e faz parecer mágico' },
  { id: 'cara_comum', descricao: 'A que é gente como a gente, sem pose' },
  { id: 'amante', descricao: 'A que seduz pelos sentidos, pela beleza e pelo prazer' },
  { id: 'bobo_da_corte', descricao: 'A que diverte e não se leva a sério' },
  { id: 'cuidador', descricao: 'A que cuida, acolhe e protege' },
  { id: 'criador', descricao: 'A que inventa e valoriza o que é feito com cuidado' },
  { id: 'governante', descricao: 'A que lidera, organiza e transmite status' },
];

export const SECOES = [
  {
    id: 'marca',
    titulo: 'A marca',
    intro: 'O básico, do jeito que você explicaria para alguém numa conversa.',
    perguntas: [
      { id: 'marca_frase', texto: 'O que é a marca e o que ela vende, em uma frase?', exemplo: 'Ex: uma loja online de discos de vinil de música brasileira, novos e usados.' },
      { id: 'marca_links', texto: 'Qual é o site e o @ do Instagram?', exemplo: 'Ex: minhaloja.com.br e @minhaloja' },
      { id: 'marca_objetivo', texto: 'O que o Instagram precisa fazer pela marca nos próximos meses?', exemplo: 'Ex: vender mais pelo site, ser lembrada como referência, formar uma comunidade.' },
    ],
  },
  {
    id: 'empatia',
    titulo: 'Quem consome o conteúdo',
    intro: 'Pense numa pessoa real, ou numa mistura de pessoas, que compraria da marca.',
    perguntas: [
      { id: 'empatia_pensa', texto: 'O que essa pessoa pensa e não fala em voz alta?', exemplo: 'Ex: quer ter bom gosto, mas tem medo de parecer que está se esforçando demais.' },
      { id: 'empatia_ve', texto: 'O que ela vê no feed, nos amigos, no que está em alta?', exemplo: 'Ex: amigos mostrando coleção, perfis de curadoria, lançamentos comentados.' },
      { id: 'empatia_influencia', texto: 'Quem influencia o que ela compra?', exemplo: 'Ex: um amigo que entende do assunto, um perfil que ela confia, o vendedor da loja.' },
      { id: 'empatia_fala', texto: 'Como ela fala desse assunto com os outros?', exemplo: 'Ex: comenta a história por trás do produto quando alguém pergunta.' },
      { id: 'empatia_frustra', texto: 'O que frustra essa pessoa hoje quando procura esse tipo de produto?', exemplo: 'Ex: tudo é caro demais ou genérico, ninguém explica o que está vendendo.' },
      { id: 'empatia_ganho', texto: 'O que faria ela sentir "achei a marca certa"?', exemplo: 'Ex: ser atendida por quem conhece e receber algo que ninguém mais tem.' },
      { id: 'empatia_nao_publico', texto: 'Quem não é o público da marca?', exemplo: 'Ex: quem só procura o mais barato, quem não liga para a história do produto.' },
    ],
  },
  {
    id: 'voz',
    titulo: 'Como a marca se comunica',
    intro: 'Não existe resposta certa. É a sua percepção da marca.',
    perguntas: [
      { id: 'voz_arquetipo', tipo: 'arquetipo', texto: 'Qual descrição mais combina com a marca? Escolha até 2.', exemplo: 'Pense em como a marca age, não em como gostaria de parecer.' },
      { id: 'voz_festa', texto: 'Se a marca chegasse numa festa, como agiria nos primeiros 5 minutos?', exemplo: 'Ex: observa antes de falar e solta um comentário que só alguns entendem.' },
      { id: 'voz_defende', texto: 'O que a marca defende mesmo que afaste gente? E o que nunca faria, nem vendendo mais?', exemplo: 'Ex: nunca vai falar de promoção antes de falar do produto.' },
      { id: 'voz_palavras', texto: 'Quais palavras e expressões a marca usa? E quais nunca usaria?', exemplo: 'Ex: usa "garimpo", "edição", "curadoria". Nunca usa "imperdível" ou "aproveite".' },
      { id: 'voz_frases', texto: 'Escreva uma frase que soa como a marca e uma que não soa.', exemplo: 'Ex: soa: "Chegou a edição que faltava na estante." Não soa: "Promoção imperdível, corre!"' },
      { id: 'posic_concorrentes', texto: 'Quais são 2 ou 3 concorrentes? O que cada um faz bem e mal?', exemplo: 'Ex: Loja X tem catálogo grande, mas atendimento frio.' },
      { id: 'posic_diferencial', texto: 'O que a marca faz que os concorrentes não fazem? E qual frase resume a marca?', exemplo: 'Ex: curadoria feita por quem ouve cada disco. "Disco escolhido a dedo."' },
    ],
  },
];
```

- [ ] **Step 4: Implementar `site/assets/formulario-logica.js`**

```js
export function totalPerguntas(secoes) {
  return secoes.reduce((n, s) => n + s.perguntas.length, 0);
}

function preenchida(valor) {
  if (Array.isArray(valor)) return valor.length > 0;
  return typeof valor === 'string' && valor.trim().length > 0;
}

export function contarRespondidas(secoes, respostas) {
  let n = 0;
  for (const secao of secoes) for (const p of secao.perguntas) if (preenchida(respostas?.[p.id])) n++;
  return n;
}

export function alternarArquetipo(lista, id, max = 2) {
  const atual = Array.isArray(lista) ? lista : [];
  if (atual.includes(id)) return atual.filter((x) => x !== id);
  if (atual.length >= max) return atual;
  return [...atual, id];
}

export function montarRespostas({ cliente, email, respostas, agora }) {
  const limpas = {};
  for (const [id, valor] of Object.entries(respostas || {})) {
    if (!preenchida(valor)) continue;
    limpas[id] = Array.isArray(valor) ? [...valor] : valor.trim();
  }
  return { cliente, email, gerado_em: agora.toISOString(), respostas: limpas };
}

export function validarSecoes(secoes, arquetipos) {
  const problemas = [];
  const ids = new Set();
  let arquetiposNoFormulario = 0;
  for (const secao of secoes) {
    if (!secao.titulo || !secao.intro) problemas.push(`seção ${secao.id} sem título ou intro`);
    for (const p of secao.perguntas || []) {
      if (ids.has(p.id)) problemas.push(`id repetido: ${p.id}`);
      ids.add(p.id);
      if (!p.texto || !p.exemplo) problemas.push(`pergunta ${p.id} sem texto ou exemplo`);
      if (p.tipo === 'arquetipo') arquetiposNoFormulario++;
    }
  }
  if (arquetiposNoFormulario !== 1) problemas.push('o formulário precisa de exatamente 1 pergunta de arquétipo');
  const idsArquetipo = new Set(arquetipos.map((a) => a.id));
  if (arquetipos.length !== 12 || idsArquetipo.size !== 12) problemas.push('a lista de arquétipos precisa de 12 ids únicos');
  return problemas;
}
```

- [ ] **Step 5: Rodar e ver passar**

Run: `node --test`
Expected: 15 tests, 15 pass

- [ ] **Step 6: Criar a tela `site/formulario/index.html` e `site/assets/formulario.js`**

`site/formulario/index.html`:
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Formulário da marca</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/estilo.css">
</head>
<body>
  <main class="pagina-estreita">
    <p class="muted"><a href="../">Voltar</a> · Lucas Lanzoni · Conteúdo</p>
    <h1 class="titulo">Formulário da marca</h1>
    <p class="muted">Sem jargão e sem resposta certa. O que você escrever fica salvo neste navegador; pode fechar e voltar depois. No fim, toque em "Enviar respostas" e mande o arquivo para o Lucas.</p>
    <p id="aviso-memoria" class="aviso" hidden>Este navegador não está guardando as respostas. Se fechar a página, elas se perdem. Use uma janela normal (não anônima) ou envie antes de sair.</p>
    <p id="progresso" class="progresso"></p>
    <div id="secoes"></div>
    <div class="acoes">
      <button id="enviar" class="botao" type="button">Enviar respostas</button>
    </div>
    <p id="enviado" class="aviso" hidden>Arquivo baixado. Mande esse arquivo para o Lucas por WhatsApp ou e-mail.</p>
  </main>
  <script type="module" src="../assets/formulario.js"></script>
</body>
</html>
```

`site/assets/formulario.js`:
```js
import { SECOES, ARQUETIPOS } from './perguntas.js';
import { contarRespondidas, montarRespostas, alternarArquetipo, totalPerguntas } from './formulario-logica.js';
import { exigirSessao, armazenamento } from './sessao.js';
import { baixarJSON } from './baixar.js';

const $ = (id) => document.getElementById(id);

function el(tag, texto, classe) {
  const e = document.createElement(tag);
  if (texto) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}

function iniciar({ email, cliente }) {
  const chave = `ia_form_${cliente}`;
  let respostas = armazenamento.ler(chave) || {};
  const campos = new Map();

  const atualizarProgresso = () => {
    $('progresso').textContent = `${contarRespondidas(SECOES, respostas)} de ${totalPerguntas(SECOES)} respondidas`;
  };
  const salvar = () => {
    armazenamento.gravar(chave, respostas);
    atualizarProgresso();
  };

  function campoTexto(p) {
    const caixa = el('section', null, 'pergunta');
    const area = document.createElement('textarea');
    area.value = typeof respostas[p.id] === 'string' ? respostas[p.id] : '';
    area.setAttribute('aria-label', p.texto);
    let espera;
    area.addEventListener('input', () => {
      clearTimeout(espera);
      espera = setTimeout(() => {
        respostas = { ...respostas, [p.id]: area.value };
        salvar();
      }, 400);
    });
    campos.set(p.id, area);
    caixa.append(el('p', p.texto, 'texto'), el('p', p.exemplo, 'exemplo'), area);
    return caixa;
  }

  function campoArquetipo(p) {
    const caixa = el('section', null, 'pergunta');
    const chips = el('div', null, 'chips');
    const aviso = el('p', '', 'exemplo');
    const desenhar = () => {
      const escolhidos = respostas[p.id] || [];
      for (const botao of chips.children) botao.setAttribute('aria-pressed', String(escolhidos.includes(botao.dataset.id)));
    };
    for (const a of ARQUETIPOS) {
      const botao = el('button', a.descricao, 'chip');
      botao.type = 'button';
      botao.dataset.id = a.id;
      botao.addEventListener('click', () => {
        const antes = respostas[p.id] || [];
        const depois = alternarArquetipo(antes, a.id);
        aviso.textContent = depois === antes ? 'Escolha no máximo 2. Desmarque uma para trocar.' : '';
        respostas = { ...respostas, [p.id]: depois };
        salvar();
        desenhar();
      });
      chips.append(botao);
    }
    desenhar();
    caixa.append(el('p', p.texto, 'texto'), el('p', p.exemplo, 'exemplo'), chips, aviso);
    return caixa;
  }

  const raiz = $('secoes');
  for (const secao of SECOES) {
    raiz.append(el('h2', secao.titulo, 'secao-titulo'), el('p', secao.intro, 'intro'));
    for (const p of secao.perguntas) raiz.append(p.tipo === 'arquetipo' ? campoArquetipo(p) : campoTexto(p));
  }

  $('enviar').addEventListener('click', () => {
    for (const [id, area] of campos) respostas = { ...respostas, [id]: area.value };
    salvar();
    const dados = montarRespostas({ cliente, email, respostas, agora: new Date() });
    baixarJSON(`respostas-${cliente}-${dados.gerado_em.slice(0, 10)}.json`, dados);
    $('enviado').hidden = false;
  });

  $('aviso-memoria').hidden = armazenamento.persistente();
  atualizarProgresso();
}

const sessao = exigirSessao('../');
if (sessao) iniciar(sessao);
```

- [ ] **Step 7: Conferir no navegador**

Run: `cd site && python3 -m http.server 8000`, entrar com `lucaslanzoni.s@gmail.com`, abrir "Formulário da marca".
Expected:
- 3 seções, 17 perguntas; progresso "0 de 17 respondidas".
- Escrever numa resposta, esperar meio segundo, recarregar: o texto continua lá e o progresso conta 1.
- Arquétipo: marcar 2 funciona; tentar o terceiro mostra "Escolha no máximo 2. Desmarque uma para trocar."
- "Enviar respostas" baixa `respostas-tropi-AAAA-MM-DD.json` com as respostas preenchidas e o aviso aparece.
- Abrir `http://localhost:8000/formulario/` numa janela anônima sem sessão redireciona para a tela de e-mail.
- Largura de 375px (celular): sem rolagem horizontal.

- [ ] **Step 8: Commit**

```bash
git add site/assets/perguntas.js site/assets/formulario-logica.js site/assets/formulario.js site/formulario/ tests/js/formulario.test.js
git commit -m "feat(site): formulário da marca com 17 perguntas e exportação de respostas

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Página de aprovação

**Files:**
- Create: `site/assets/aprovacao-logica.js`, `site/assets/aprovacao.js`, `site/aprovacao/index.html`, `tests/fixtures/demo/cliente.json`, `tests/fixtures/demo/2026-01/posts/01-capa-demo/{post.json,legenda.md,slide-1.html,slide-2.html}`, `tests/fixtures/demo/2026-01/posts/02-post-unico/{post.json,legenda.md,slide-1.html}`
- Test: `tests/js/aprovacao.test.js`

**Interfaces:**
- Consumes: manifesto da Task 4; `exigirSessao`, `armazenamento`, `baixarBlob`, `baixarJSON` da Task 5; `window.JSZip` (cdnjs 3.10.1).
- Produces: `aprovacao-logica.js` com `STATUS`, `validarManifesto(m) -> string[]`, `escolherMes(indice, pedido) -> mes | null`, `definirStatus(estado, id, status)`, `definirComentario(estado, id, texto)`, `editarLegenda(estado, id, texto, original)`, `legendaFinal(post, estado)`, `limparEstado(estado, posts)`, `resumo(estado, posts) -> {aprovado, revisar, descartado, pendente}`, `montarAprovacao({cliente, mes, email, estado, posts, agora})`, `arquivosDoPost(post, estado) -> {imagens: [{src, nome}], legenda: {nome, texto}}`. Arquivo exportado `aprovacao-<cliente>-<mes>.json` = `{cliente, mes, email, gerado_em, resumo, posts: {<id>: {status?, comentario?, legenda_editada?}}}`, consumido pela skill `ig-entrega` (Task 9).

- [ ] **Step 1: Escrever os testes que falham**

`tests/js/aprovacao.test.js`:
```js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  validarManifesto, escolherMes, definirStatus, definirComentario, editarLegenda,
  legendaFinal, limparEstado, resumo, montarAprovacao, arquivosDoPost,
} from '../../site/assets/aprovacao-logica.js';

const posts = [
  { id: '01-a', numero: 1, formato: 'carrossel', imagens: ['01-a/1.jpg', '01-a/2.jpg'], legenda: 'Legenda A' },
  { id: '02-b', numero: 2, formato: 'estatico', imagens: ['02-b/1.jpg'], legenda: 'Legenda B' },
];

test('manifesto válido não tem erros', () => {
  assert.deepEqual(validarManifesto({ cliente: 'demo', mes: '2026-01', posts }), []);
});

test('manifesto com id repetido e post sem imagem', () => {
  const erros = validarManifesto({ cliente: 'demo', mes: '2026-01', posts: [posts[0], { ...posts[0] }, { id: '03-c', formato: 'estatico', imagens: [] }] });
  assert.ok(erros.some((e) => e.includes('id repetido')));
  assert.ok(erros.some((e) => e.includes('03-c: sem imagens')));
});

test('manifesto ausente', () => {
  assert.deepEqual(validarManifesto(null), ['manifesto ausente']);
});

test('escolherMes usa o pedido se existir, senão o mais recente, senão null', () => {
  const indice = { meses: ['2026-09', '2026-11', '2026-10'] };
  assert.equal(escolherMes(indice, '2026-10'), '2026-10');
  assert.equal(escolherMes(indice, '2030-01'), '2026-11');
  assert.equal(escolherMes(indice, null), '2026-11');
  assert.equal(escolherMes({ meses: [] }, '2026-10'), null);
  assert.equal(escolherMes(null, null), null);
});

test('definirStatus marca, troca e desmarca clicando de novo', () => {
  let e = definirStatus({}, '01-a', 'aprovado');
  assert.deepEqual(e, { '01-a': { status: 'aprovado' } });
  e = definirStatus(e, '01-a', 'revisar');
  assert.equal(e['01-a'].status, 'revisar');
  e = definirStatus(e, '01-a', 'revisar');
  assert.deepEqual(e, {});
});

test('status inválido lança erro', () => {
  assert.throws(() => definirStatus({}, '01-a', 'talvez'), /status inválido/);
});

test('comentário vazio some; legenda igual à original some', () => {
  let e = definirComentario({}, '01-a', '  trocar a capa ');
  assert.equal(e['01-a'].comentario, 'trocar a capa');
  e = definirComentario(e, '01-a', '   ');
  assert.deepEqual(e, {});
  e = editarLegenda({}, '01-a', 'Nova', 'Legenda A');
  assert.equal(legendaFinal(posts[0], e), 'Nova');
  e = editarLegenda(e, '01-a', 'Legenda A', 'Legenda A');
  assert.deepEqual(e, {});
  assert.equal(legendaFinal(posts[0], e), 'Legenda A');
});

test('legenda editada para vazio continua valendo como edição', () => {
  const e = editarLegenda({}, '01-a', '', 'Legenda A');
  assert.equal(legendaFinal(posts[0], e), '');
});

test('limparEstado descarta posts que não estão mais no manifesto', () => {
  const estado = { '01-a': { status: 'aprovado' }, '99-velho': { status: 'revisar' } };
  assert.deepEqual(limparEstado(estado, posts), { '01-a': { status: 'aprovado' } });
});

test('resumo conta pendentes', () => {
  assert.deepEqual(resumo({ '01-a': { status: 'revisar' } }, posts), { aprovado: 0, revisar: 1, descartado: 0, pendente: 1 });
});

test('montarAprovacao exporta só posts atuais e com data', () => {
  const dados = montarAprovacao({
    cliente: 'demo', mes: '2026-01', email: 'a@b.co',
    estado: { '02-b': { status: 'aprovado' }, '99-velho': { status: 'revisar' } },
    posts, agora: new Date('2026-01-15T10:00:00Z'),
  });
  assert.deepEqual(dados, {
    cliente: 'demo', mes: '2026-01', email: 'a@b.co', gerado_em: '2026-01-15T10:00:00.000Z',
    resumo: { aprovado: 1, revisar: 0, descartado: 0, pendente: 1 },
    posts: { '02-b': { status: 'aprovado' } },
  });
});

test('arquivosDoPost nomeia imagens e legenda final', () => {
  const arq = arquivosDoPost(posts[0], { '01-a': { legenda_editada: 'Editada' } });
  assert.deepEqual(arq.imagens, [
    { src: '01-a/1.jpg', nome: '01-a/1.jpg' },
    { src: '01-a/2.jpg', nome: '01-a/2.jpg' },
  ]);
  assert.deepEqual(arq.legenda, { nome: '01-a/legenda.txt', texto: 'Editada' });
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `node --test`
Expected: FAIL com `Cannot find module '.../site/assets/aprovacao-logica.js'`

- [ ] **Step 3: Implementar `site/assets/aprovacao-logica.js`**

```js
export const STATUS = ['aprovado', 'revisar', 'descartado'];
const FORMATOS = ['carrossel', 'estatico'];

export function validarManifesto(m) {
  if (!m || typeof m !== 'object') return ['manifesto ausente'];
  const erros = [];
  for (const campo of ['cliente', 'mes', 'posts']) if (!m[campo]) erros.push(`sem ${campo}`);
  if (m.posts && !Array.isArray(m.posts)) return [...erros, 'posts não é lista'];
  const ids = new Set();
  (m.posts || []).forEach((p, i) => {
    if (!p.id) {
      erros.push(`post ${i + 1} sem id`);
      return;
    }
    if (ids.has(p.id)) erros.push(`id repetido: ${p.id}`);
    ids.add(p.id);
    if (!FORMATOS.includes(p.formato)) erros.push(`${p.id}: formato inválido`);
    if (!Array.isArray(p.imagens) || p.imagens.length === 0) erros.push(`${p.id}: sem imagens`);
  });
  return erros;
}

export function escolherMes(indice, pedido) {
  const meses = [...(indice?.meses || [])].sort();
  if (pedido && meses.includes(pedido)) return pedido;
  return meses.length ? meses[meses.length - 1] : null;
}

function limparEntrada(e) {
  const r = {};
  if (e.status) r.status = e.status;
  if (e.comentario) r.comentario = e.comentario;
  if (typeof e.legenda_editada === 'string') r.legenda_editada = e.legenda_editada;
  return r;
}

function comEntrada(estado, id, mudar) {
  const nova = limparEntrada(mudar({ ...(estado?.[id] || {}) }));
  const resto = { ...(estado || {}) };
  if (Object.keys(nova).length) resto[id] = nova;
  else delete resto[id];
  return resto;
}

export function definirStatus(estado, id, status) {
  if (!STATUS.includes(status)) throw new Error(`status inválido: ${status}`);
  return comEntrada(estado, id, (e) => ({ ...e, status: e.status === status ? undefined : status }));
}

export function definirComentario(estado, id, texto) {
  return comEntrada(estado, id, (e) => ({ ...e, comentario: (texto || '').trim() || undefined }));
}

export function editarLegenda(estado, id, texto, original) {
  return comEntrada(estado, id, (e) => ({ ...e, legenda_editada: texto === original ? undefined : texto }));
}

export function legendaFinal(post, estado) {
  const e = estado?.[post.id];
  return typeof e?.legenda_editada === 'string' ? e.legenda_editada : post.legenda;
}

export function limparEstado(estado, posts) {
  const ids = new Set(posts.map((p) => p.id));
  return Object.fromEntries(Object.entries(estado || {}).filter(([id]) => ids.has(id)));
}

export function resumo(estado, posts) {
  const r = { aprovado: 0, revisar: 0, descartado: 0, pendente: 0 };
  for (const p of posts) {
    const s = estado?.[p.id]?.status;
    if (s) r[s]++;
    else r.pendente++;
  }
  return r;
}

export function montarAprovacao({ cliente, mes, email, estado, posts, agora }) {
  return {
    cliente, mes, email,
    gerado_em: agora.toISOString(),
    resumo: resumo(estado, posts),
    posts: limparEstado(estado, posts),
  };
}

export function arquivosDoPost(post, estado) {
  return {
    imagens: post.imagens.map((src) => ({ src, nome: src })),
    legenda: { nome: `${post.id}/legenda.txt`, texto: legendaFinal(post, estado) },
  };
}
```

- [ ] **Step 4: Rodar e ver passar**

Run: `node --test`
Expected: 27 tests, 27 pass

- [ ] **Step 5: Criar a tela `site/aprovacao/index.html`**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Conteúdo do mês</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../assets/estilo.css">
</head>
<body>
  <div class="layout">
    <aside class="lateral">
      <p class="marca"><a href="../">Voltar</a> · Lucas Lanzoni · Conteúdo</p>
      <h1 id="cliente-nome" class="titulo"></h1>
      <p id="cliente-mes" class="muted"></p>
      <p id="cliente-arroba" class="muted"></p>
      <p id="resumo" class="resumo"></p>
      <p id="aviso-memoria" class="aviso" hidden>Este navegador não está guardando as avaliações. Envie antes de fechar a página.</p>
      <div class="acoes">
        <button id="enviar" class="botao" type="button">Enviar aprovação</button>
        <button id="baixar-tudo" class="botao-secundario" type="button">Baixar o mês</button>
      </div>
      <p id="enviado" class="aviso" hidden>Arquivo baixado. Mande esse arquivo para o Lucas por WhatsApp ou e-mail.</p>
      <ol id="lista" class="lista"></ol>
    </aside>
    <main class="principal">
      <p id="mensagem" class="mensagem aviso" hidden></p>
      <div id="grade" class="grade"></div>
    </main>
  </div>

  <dialog id="janela" class="janela">
    <div class="janela-corpo">
      <div class="palco">
        <div id="carrossel" class="carrossel"></div>
        <button id="anterior" class="seta anterior" type="button" aria-label="Slide anterior">&lsaquo;</button>
        <button id="proxima" class="seta proxima" type="button" aria-label="Próximo slide">&rsaquo;</button>
        <div id="pontos" class="pontos"></div>
      </div>
      <div class="painel">
        <p id="post-info" class="muted"></p>
        <h2 id="post-tema" class="titulo"></h2>
        <div class="status-botoes" id="status-botoes">
          <button type="button" data-status="aprovado">Aprovado</button>
          <button type="button" data-status="revisar">Revisar</button>
          <button type="button" data-status="descartado">Descartado</button>
        </div>
        <label for="comentario" id="rotulo-comentario" hidden>O que precisa mudar?</label>
        <textarea id="comentario" hidden></textarea>
        <label for="legenda">Legenda (pode editar)</label>
        <textarea id="legenda" rows="10"></textarea>
        <div class="acoes">
          <button id="copiar" class="botao-secundario" type="button">Copiar legenda</button>
          <button id="baixar-post" class="botao-secundario" type="button">Baixar este post</button>
          <button id="fechar" class="botao" type="button">Fechar</button>
        </div>
        <p id="copiado" class="muted" hidden>Legenda copiada.</p>
      </div>
    </div>
  </dialog>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
  <script type="module" src="../assets/aprovacao.js"></script>
</body>
</html>
```

- [ ] **Step 6: Criar `site/assets/aprovacao.js`**

```js
import { exigirSessao, armazenamento } from './sessao.js';
import {
  validarManifesto, escolherMes, definirStatus, definirComentario, editarLegenda,
  legendaFinal, limparEstado, resumo, montarAprovacao, arquivosDoPost,
} from './aprovacao-logica.js';
import { baixarBlob, baixarJSON } from './baixar.js';

const $ = (id) => document.getElementById(id);
const ROTULO_FORMATO = { carrossel: 'Carrossel', estatico: 'Post estático' };
const NOMES_MES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

function formatarMes(mes) {
  const [ano, m] = mes.split('-');
  return `${NOMES_MES[Number(m) - 1] || mes} ${ano}`;
}

function formatarData(data) {
  if (!data) return '';
  const [, m, d] = data.split('-');
  return `${d}/${m}`;
}

function el(tag, texto, classe) {
  const e = document.createElement(tag);
  if (texto) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}

function mostrarMensagem(texto, erro) {
  $('mensagem').textContent = texto;
  $('mensagem').hidden = false;
  if (erro) console.error(erro);
}

async function buscarJSON(url) {
  const r = await fetch(url, { cache: 'no-store' });
  if (!r.ok) throw new Error(`${r.status} em ${url}`);
  return r.json();
}

async function iniciar({ email, cliente }) {
  let indice;
  try {
    indice = await buscarJSON(`../clientes/${cliente}/indice.json`);
  } catch {
    indice = null;
  }
  const mes = escolherMes(indice, new URLSearchParams(location.search).get('mes'));
  if (!mes) {
    mostrarMensagem('Ainda não há conteúdo publicado para esta marca.');
    return;
  }
  const base = `../clientes/${cliente}/${mes}/`;
  const manifesto = await buscarJSON(`${base}manifesto.json`);
  const erros = validarManifesto(manifesto);
  if (erros.length) {
    mostrarMensagem(`O conteúdo deste mês está com problema: ${erros[0]}. Fale com o Lucas.`);
    return;
  }
  const posts = manifesto.posts;
  const chave = `ia_aprov_${cliente}_${mes}`;
  let estado = limparEstado(armazenamento.ler(chave) || {}, posts);
  let aberto = null;

  $('cliente-nome').textContent = manifesto.nome || cliente;
  $('cliente-mes').textContent = formatarMes(mes);
  $('cliente-arroba').textContent = `${manifesto.arroba || ''} · ${posts.length} publicações`;
  $('aviso-memoria').hidden = armazenamento.persistente();

  function salvar(novo) {
    estado = novo;
    armazenamento.gravar(chave, estado);
    desenharStatus();
  }

  function desenharStatus() {
    const r = resumo(estado, posts);
    $('resumo').textContent = `${r.aprovado} aprovados · ${r.revisar} para revisar · ${r.descartado} descartados · ${r.pendente} pendentes`;
    for (const no of document.querySelectorAll('[data-post]')) {
      const s = estado[no.dataset.post]?.status || '';
      no.dataset.status = s;
    }
    if (aberto) {
      const s = estado[aberto.id]?.status || '';
      for (const b of $('status-botoes').children) b.setAttribute('aria-pressed', String(b.dataset.status === s));
      const revisar = s === 'revisar';
      $('comentario').hidden = !revisar;
      $('rotulo-comentario').hidden = !revisar;
    }
  }

  function miniatura(post) {
    const img = document.createElement('img');
    img.src = base + post.imagens[0];
    img.alt = post.alt || post.tema || '';
    img.loading = 'lazy';
    return img;
  }

  posts.forEach((post, i) => {
    const item = el('button', null, 'item');
    item.type = 'button';
    const texto = el('span', post.tema || post.id, 'tema');
    texto.append(el('span', ROTULO_FORMATO[post.formato], 'formato'));
    const ponto = el('span', null, 'ponto-status');
    ponto.dataset.post = post.id;
    item.append(el('span', String(post.numero).padStart(2, '0'), 'num'), miniatura(post), texto, ponto);
    item.addEventListener('click', () => abrir(i));
    const li = document.createElement('li');
    li.append(item);
    $('lista').append(li);

    const celula = el('button', null, 'celula');
    celula.type = 'button';
    celula.dataset.post = post.id;
    celula.setAttribute('aria-label', `Abrir post ${post.numero}: ${post.tema || ''}`);
    celula.append(miniatura(post), el('span', String(post.numero).padStart(2, '0'), 'selo num'), el('span', ROTULO_FORMATO[post.formato], 'selo formato'));
    celula.addEventListener('click', () => abrir(i));
    $('grade').append(celula);
  });

  function slideAtual() {
    const c = $('carrossel');
    return Math.round(c.scrollLeft / Math.max(c.clientWidth, 1));
  }

  function desenharPontos() {
    const atual = slideAtual();
    [...$('pontos').children].forEach((p, i) => p.classList.toggle('ativo', i === atual));
  }

  function irPara(i) {
    const c = $('carrossel');
    c.scrollTo({ left: i * c.clientWidth, behavior: 'smooth' });
  }

  function abrir(i) {
    aberto = posts[i];
    const c = $('carrossel');
    c.replaceChildren(...aberto.imagens.map((src, n) => {
      const img = document.createElement('img');
      img.src = base + src;
      img.alt = n === 0 ? aberto.alt || '' : `Slide ${n + 1}`;
      return img;
    }));
    c.scrollLeft = 0;
    $('pontos').replaceChildren(...aberto.imagens.map(() => el('span')));
    const varios = aberto.imagens.length > 1;
    $('anterior').hidden = !varios;
    $('proxima').hidden = !varios;
    $('pontos').hidden = !varios;
    $('post-info').textContent = [String(aberto.numero).padStart(2, '0'), ROTULO_FORMATO[aberto.formato], formatarData(aberto.data_sugerida)].filter(Boolean).join(' · ');
    $('post-tema').textContent = aberto.tema || '';
    $('legenda').value = legendaFinal(aberto, estado);
    $('comentario').value = estado[aberto.id]?.comentario || '';
    $('copiado').hidden = true;
    desenharStatus();
    desenharPontos();
    $('janela').showModal();
  }

  $('carrossel').addEventListener('scroll', desenharPontos, { passive: true });
  $('anterior').addEventListener('click', () => irPara(Math.max(slideAtual() - 1, 0)));
  $('proxima').addEventListener('click', () => irPara(Math.min(slideAtual() + 1, aberto.imagens.length - 1)));
  $('janela').addEventListener('keydown', (e) => {
    if (e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowLeft') $('anterior').click();
    if (e.key === 'ArrowRight') $('proxima').click();
  });
  $('janela').addEventListener('close', () => { aberto = null; });
  $('fechar').addEventListener('click', () => $('janela').close());

  for (const botao of $('status-botoes').children) {
    botao.addEventListener('click', () => salvar(definirStatus(estado, aberto.id, botao.dataset.status)));
  }
  $('comentario').addEventListener('input', () => salvar(definirComentario(estado, aberto.id, $('comentario').value)));
  $('legenda').addEventListener('input', () => salvar(editarLegenda(estado, aberto.id, $('legenda').value, aberto.legenda)));
  $('copiar').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText($('legenda').value);
      $('copiado').textContent = 'Legenda copiada.';
    } catch {
      $('legenda').select();
      $('copiado').textContent = 'Selecionei a legenda. Use copiar do seu aparelho.';
    }
    $('copiado').hidden = false;
  });

  async function baixarZip(lista, nomeZip, botao) {
    if (!window.JSZip) {
      mostrarMensagem('Não foi possível preparar o download. Verifique a conexão e tente de novo.');
      return;
    }
    const rotulo = botao.textContent;
    botao.disabled = true;
    botao.textContent = 'Preparando...';
    try {
      const zip = new window.JSZip();
      for (const post of lista) {
        const arquivos = arquivosDoPost(post, estado);
        for (const img of arquivos.imagens) {
          const r = await fetch(base + img.src);
          if (!r.ok) throw new Error(`${r.status} em ${img.src}`);
          zip.file(img.nome, await r.blob());
        }
        zip.file(arquivos.legenda.nome, arquivos.legenda.texto);
      }
      baixarBlob(nomeZip, await zip.generateAsync({ type: 'blob' }));
    } catch (erro) {
      mostrarMensagem('O download falhou. Tente de novo.', erro);
    } finally {
      botao.disabled = false;
      botao.textContent = rotulo;
    }
  }

  $('baixar-post').addEventListener('click', () => baixarZip([aberto], `${cliente}-${mes}-${aberto.id}.zip`, $('baixar-post')));
  $('baixar-tudo').addEventListener('click', () => baixarZip(posts, `${cliente}-${mes}.zip`, $('baixar-tudo')));
  $('enviar').addEventListener('click', () => {
    baixarJSON(`aprovacao-${cliente}-${mes}.json`, montarAprovacao({ cliente, mes, email, estado, posts, agora: new Date() }));
    $('enviado').hidden = false;
  });

  desenharStatus();
}

const sessao = exigirSessao('../');
if (sessao) iniciar(sessao).catch((erro) => mostrarMensagem('Não foi possível carregar o conteúdo. Recarregue a página.', erro));
```

- [ ] **Step 7: Criar o cliente de demonstração em `tests/fixtures/demo/`**

`tests/fixtures/demo/cliente.json`:
```json
{ "slug": "demo", "nome": "Loja Demo", "arroba": "@lojademo" }
```

`tests/fixtures/demo/2026-01/posts/01-capa-demo/post.json`:
```json
{ "numero": 1, "tema": "Lançamento", "formato": "carrossel", "data_sugerida": "2026-01-07", "alt": "Slide laranja de demonstração" }
```

`tests/fixtures/demo/2026-01/posts/01-capa-demo/legenda.md`:
```
Legenda de demonstração com acento: coleção, edição, música.

Link na bio.

#demo #vinil
```

`tests/fixtures/demo/2026-01/posts/01-capa-demo/slide-1.html`:
```html
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"></head>
<body style="margin:0;width:1080px;height:1350px;background:#FB5607;color:#fff;font:bold 120px sans-serif;display:flex;align-items:center;justify-content:center">Capa 1</body></html>
```

`tests/fixtures/demo/2026-01/posts/01-capa-demo/slide-2.html`:
```html
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"></head>
<body style="margin:0;width:1080px;height:1350px;background:#1B1B7A;color:#fff;font:bold 120px sans-serif;display:flex;align-items:center;justify-content:center">Slide 2</body></html>
```

`tests/fixtures/demo/2026-01/posts/02-post-unico/post.json`:
```json
{ "numero": 2, "tema": "Bastidor", "formato": "estatico", "data_sugerida": "2026-01-10", "alt": "Post único de demonstração" }
```

`tests/fixtures/demo/2026-01/posts/02-post-unico/legenda.md`:
```
Post único de demonstração.

Salva esse post.
```

`tests/fixtures/demo/2026-01/posts/02-post-unico/slide-1.html`:
```html
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"></head>
<body style="margin:0;width:1080px;height:1350px;background:#F6EFE1;color:#2A2622;font:bold 120px sans-serif;display:flex;align-items:center;justify-content:center">Único</body></html>
```

- [ ] **Step 8: Conferir a página com o cliente de demonstração, num site temporário**

Run:
```bash
TMP=$(mktemp -d)
cp -R site "$TMP/site"
printf '{"emails":{"demo@exemplo.com":"demo"}}' > "$TMP/site/acesso.json"
uv run python -m ferramentas.renderizar tests/fixtures/demo/2026-01/posts/01-capa-demo
uv run python -m ferramentas.renderizar tests/fixtures/demo/2026-01/posts/02-post-unico
uv run python -m ferramentas.manifesto tests/fixtures/demo/2026-01 --site "$TMP/site"
cd "$TMP/site" && python3 -m http.server 8001
```
Abrir `http://localhost:8001`, entrar com `demo@exemplo.com`, abrir "Conteúdo de Janeiro 2026".
Expected:
- Lateral com "Loja Demo", "Janeiro 2026", "@lojademo · 2 publicações", lista com 2 itens e resumo "0 aprovados · 0 para revisar · 0 descartados · 2 pendentes".
- Grade com 2 células, selos "01 · Carrossel" e "02 · Post estático".
- Abrir o post 01: carrossel passa entre "Capa 1" e "Slide 2" pelas setas, pelas teclas e pelo gesto; pontos acompanham.
- "Revisar" mostra o campo de comentário; escrever, fechar, reabrir: comentário e status continuam; recarregar a página: continuam.
- Editar a legenda e usar "Baixar este post": o .zip tem `01-capa-demo/1.jpg`, `01-capa-demo/2.jpg` e `01-capa-demo/legenda.txt` com o texto editado.
- "Baixar o mês" gera um .zip com os 2 posts.
- "Enviar aprovação" baixa `aprovacao-demo-2026-01.json` no formato da interface.
- `http://localhost:8001/aprovacao/?mes=2030-01` abre Janeiro 2026 (mês mais recente).
- Largura de 375px: lista lateral some, grade em 3 colunas, janela do post em coluna única, sem rolagem horizontal.
Depois: parar o servidor e `rm -rf "$TMP"`.

- [ ] **Step 9: Commit**

```bash
git add site/assets/aprovacao-logica.js site/assets/aprovacao.js site/aprovacao/ tests/js/aprovacao.test.js tests/fixtures/demo/
git commit -m "feat(site): página de aprovação com prévia do perfil, edição e download

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Moldes das fichas e skills de onboarding, humanizador e legenda

**Files:**
- Create: `modelos/ficha-marca.md`, `modelos/ficha-voz.md`, `.claude/skills/ig-onboarding/SKILL.md`, `.claude/skills/ig-humano/SKILL.md`, `.claude/skills/ig-legenda/SKILL.md`
- Test: `tests/test_skills.py`

**Interfaces:**
- Consumes: `ler_proibidas` (Task 2); `respostas.json` (Task 6); `ferramentas.legenda`, `ferramentas.humanizar` (Tasks 1-2).
- Produces: `clientes/<slug>/marca.md` e `clientes/<slug>/voz.md` no formato dos moldes; `voz.md` sempre com os títulos exatos `## Proibidas` e `## Exemplos`.

- [ ] **Step 1: Escrever os testes que falham**

`tests/test_skills.py`:
```python
import re
from pathlib import Path

import pytest

from ferramentas.humanizar import ler_proibidas

RAIZ = Path(__file__).resolve().parent.parent
SKILLS = sorted((RAIZ / ".claude" / "skills").glob("*/SKILL.md"))


def frontmatter(texto):
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    assert m, "SKILL.md sem frontmatter"
    return dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.parent.name)
def test_frontmatter_valido(skill):
    campos = frontmatter(skill.read_text(encoding="utf-8"))
    assert campos.get("name") == skill.parent.name
    assert len(campos.get("description", "")) >= 40


def test_molde_de_voz_tem_blocos_de_maquina_vazios():
    texto = (RAIZ / "modelos" / "ficha-voz.md").read_text(encoding="utf-8")
    assert "\n## Proibidas\n" in texto
    assert "\n## Exemplos\n" in texto
    assert ler_proibidas(texto) == []


def test_molde_de_marca_tem_secoes():
    texto = (RAIZ / "modelos" / "ficha-marca.md").read_text(encoding="utf-8")
    for secao in ["## 1. Identidade", "## 2. Público", "## 3. Produto e oferta",
                  "## 4. Posicionamento", "## 5. Concorrentes", "## 6. Temas de conteúdo", "## 7. Insights"]:
        assert secao in texto
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/test_skills.py -v`
Expected: FAIL com `FileNotFoundError` em `modelos/ficha-voz.md`

- [ ] **Step 3: Criar `modelos/ficha-marca.md`**

```markdown
# Ficha da marca: {{nome}}

Fonte: formulário de {{data}}, site {{site}}{{, material de marca}}.
Legenda: o que o cliente disse vai sem marca; inferência de Claude vai marcada "(inferência)"; lacuna vai como {{a preencher}}.

## 1. Identidade

- O que é, em uma frase:
- O que vende:
- O que o Instagram precisa fazer pela marca agora:

## 2. Público

- Quem é (perfil):
- O que pensa e não fala:
- O que vê e consome:
- Quem influencia a compra:
- Como fala do assunto:
- Frustrações:
- O que faz sentir "achei a marca certa":
- Quem não é o público:

## 3. Produto e oferta

- Linhas ou categorias:
- Faixa de preço e política de desconto (nunca citar preço em post sem pedido do cliente):
- Canal de venda:

## 4. Posicionamento

- Diferencial:
- Frase que resume a marca:
- O que a marca defende mesmo que afaste gente:

## 5. Concorrentes

| Marca | Faz bem | Faz mal |
|---|---|---|

## 6. Temas de conteúdo

3 a 5 temas fixos (pilares) que a pauta usa. Cada um com uma linha do porquê.

-

## 7. Insights

Leituras de Claude que não saem de resposta direta. Todas marcadas "(inferência)".

-
```

- [ ] **Step 4: Criar `modelos/ficha-voz.md`**

```markdown
# Ficha de voz: {{nome}}

Fonte: formulário de {{data}}, site {{site}}{{, material de marca}}.

## 1. Personalidade

- Arquétipo (até 2):
- Se a marca fosse uma pessoa:
- Nos primeiros 5 minutos de uma festa:

## 2. Pilares de voz

Três ou quatro pilares. Cada um com o que ele NÃO é.

### Pilar 1:
Distingue de:

## 3. Voz e tom por contexto

A voz é constante; o tom muda.

| Contexto | Tom | Ajuste |
|---|---|---|
| Carrossel | | |
| Post estático | | |
| Legenda | | |

## 4. O que a marca fala

- Palavras e expressões que usa:
- Ritmo e pontuação:
- Emoji:
- Exclamação:

## 5. O que a marca nunca faz

-

## 6. Checklist antes de publicar

- [ ] Tem ponto de vista ou é só descrição?
- [ ] Soaria dito por essa marca?
- [ ] Tem palavra da lista Proibidas?
- [ ] Se tirar o logo, ainda parece a marca?

## 7. Frase-âncora

>

## Proibidas

## Exemplos
```

- [ ] **Step 5: Criar `.claude/skills/ig-onboarding/SKILL.md`**

```markdown
---
name: ig-onboarding
description: Transforma o respostas.json do formulário de um cliente em ficha da marca (marca.md) e ficha de voz (voz.md). Usar quando Lucas trouxer um respostas.json novo ou pedir para criar ou atualizar as fichas de um cliente.
---

# ig-onboarding

Entrada: `clientes/<slug>/respostas.json` (exportado pelo formulário do site) e
`clientes/<slug>/cliente.json`. Saída: `clientes/<slug>/marca.md` e
`clientes/<slug>/voz.md`, nos moldes de `modelos/ficha-marca.md` e
`modelos/ficha-voz.md`.

## Passos

1. Ler `respostas.json` e `cliente.json`. Listar perguntas sem resposta. Se faltar
   alguma de `marca_frase`, `empatia_*`, `voz_palavras`, `voz_frases` ou
   `posic_diferencial`, mostrar a lista a Lucas e perguntar se segue com lacunas.
2. Ler o site (`cliente.json` campo `site`) com WebFetch: o que vende, categorias,
   palavras que a marca já usa. Guardar as frases reais do site como exemplos.
3. Se `cliente.json` tiver `pasta_marca`, ler o `CLAUDE.md` e os documentos de
   branding dessa pasta. Eles têm prioridade sobre inferências.
4. Escrever `marca.md` a partir do molde, com este mapa:

   | Pergunta | Seção |
   |---|---|
   | marca_frase, marca_objetivo | 1. Identidade |
   | marca_links | cabeçalho (fonte) |
   | empatia_* | 2. Público |
   | site + pasta_marca | 3. Produto e oferta |
   | posic_diferencial, voz_defende | 4. Posicionamento |
   | posic_concorrentes | 5. Concorrentes |
   | todas | 6. Temas de conteúdo (3 a 5 pilares) |
   | leitura de Claude | 7. Insights, cada item marcado "(inferência)" |

5. Escrever `voz.md` a partir do molde, com este mapa:

   | Pergunta | Seção |
   |---|---|
   | voz_arquetipo (ids em ARQUETIPOS de `site/assets/perguntas.js`) | 1. Personalidade |
   | voz_festa, voz_defende | 1. Personalidade e 2. Pilares |
   | voz_palavras (parte "usa") | 4. O que a marca fala |
   | voz_palavras (parte "nunca usaria") + regras da marca | ## Proibidas, um termo por linha `- termo`, em minúsculas |
   | voz_frases | ## Exemplos, formato `- Ruim: <frase> \| Bom: <frase>` |

   Pares ruim/bom escritos por Claude levam "(Claude)" no fim da linha.
6. Regras: não inventar número, prêmio ou depoimento; o que faltar vira
   `{{a preencher}}`. Não mudar os títulos `## Proibidas` e `## Exemplos`: o
   humanizador lê o primeiro pelo título exato.
7. Comparar com o material de marca existente e listar a Lucas, em bullets, onde
   as respostas divergem ou deixam de fora algo que já está documentado. Isso
   mede se o formulário captura a marca.
8. Conferir: `uv run python -c "from ferramentas.humanizar import ler_proibidas; print(ler_proibidas(open('clientes/<slug>/voz.md').read()))"`
   devolve a lista esperada.
9. Mostrar a Lucas um resumo das duas fichas e ajustar. Commit das fichas.
```

- [ ] **Step 6: Criar `.claude/skills/ig-humano/SKILL.md`**

```markdown
---
name: ig-humano
description: Passa texto de slide ou legenda pelo humanizador em PT-BR com a lista de proibidas do cliente e reescreve o que a ferramenta só sinaliza. Usar antes de fechar qualquer texto que vai para um post.
---

# ig-humano

Adaptado de `ig-human` (Jake Schincariol, MIT; ver THIRD_PARTY.md).

## Passos

1. Salvar o rascunho num arquivo temporário na pasta do post (`rascunho.txt`).
2. Rodar:

       uv run python -m ferramentas.humanizar rascunho.txt --voz clientes/<slug>/voz.md --saida rascunho.txt --relatorio

3. Ler o relatório:
   - Invisíveis, tipográficos e léxico já foram corrigidos no arquivo.
   - **Estruturas** e **proibidas do cliente** NÃO são corrigidas pela ferramenta.
     Reescrever essas frases à mão, seguindo `voz.md` (pilares, exemplos, o que a
     marca nunca faz). Não trocar uma palavra proibida por sinônimo que diga o
     mesmo; mudar a frase.
4. Rodar de novo até sair com código 0 (nenhuma proibida). Estrutura que continuar
   sinalizada só fica se Claude conseguir justificar em uma linha por que ela é da
   voz da marca; registrar a justificativa no chat.
5. Apagar `rascunho.txt` depois de copiar o texto final para o slide ou para
   `legenda.md`.

## Limites

- O léxico em PT-BR é curto (Fase 2 traduz o do Jake inteiro). Ler o texto com os
  olhos da marca depois da ferramenta: ela pega marca de máquina, não pega texto
  genérico.
- Texto de slide é curto por natureza: não encher nem picotar slide por ritmo.
```

- [ ] **Step 7: Criar `.claude/skills/ig-legenda/SKILL.md`**

```markdown
---
name: ig-legenda
description: Escreve e verifica a legenda de um post de Instagram na voz do cliente, com gancho antes do corte de 125 caracteres, um pedido e de 3 a 5 hashtags. Usada por ig-carrossel e ig-post.
---

# ig-legenda

Adaptado de `ig-caption` (Jake Schincariol, MIT; ver THIRD_PARTY.md).

## Regras

- Os primeiros 125 caracteres são o que o feed mostra. O gancho mora ali: um fato,
  um nome, um número. Nada de "Oi, gente" nem hashtag na primeira linha.
- Carrossel: a legenda completa a capa, não repete a capa.
- Post estático: a legenda carrega mais contexto que a imagem.
- Um pedido só (salvar, comentar, link na bio, arrastar). Dois pedidos valem nenhum.
- Sem link no texto: link em legenda não é clicável; usar "link na bio".
- 3 a 5 hashtags no fim, específicas do assunto. Nenhuma genérica (#viral, #instagood).
- Tom, palavras, emoji e exclamação seguem `clientes/<slug>/voz.md`.
- Nunca citar preço, a não ser que a pauta peça.

## Passos

1. Escrever a legenda em `posts/<id>/legenda.md`.
2. Passar pelo `ig-humano`.
3. Verificar:

       uv run python -m ferramentas.legenda clientes/<slug>/<mes>/posts/<id>/legenda.md

4. Meta: veredito `PRONTA`. `REVISAR` só é aceito se o alerta for intencional
   (ex.: nome de artista que a ferramenta não vê como concreto); registrar o
   motivo no chat. `CORRIGIR` nunca vai para a entrega.
```

- [ ] **Step 8: Rodar e ver passar**

Run: `uv run pytest tests/test_skills.py -v`
Expected: 5 passed (3 frontmatter + 2 moldes)

- [ ] **Step 9: Commit**

```bash
git add modelos/ .claude/skills/ig-onboarding .claude/skills/ig-humano .claude/skills/ig-legenda tests/test_skills.py
git commit -m "feat(skills): moldes das fichas e skills de onboarding, humanizador e legenda

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Skills de pauta, produção e entrega, e o cliente Tropi

**Files:**
- Create: `.claude/skills/ig-pauta/SKILL.md`, `.claude/skills/ig-pauta/ganchos.md`, `.claude/skills/ig-carrossel/SKILL.md`, `.claude/skills/ig-post/SKILL.md`, `.claude/skills/ig-entrega/SKILL.md`, `clientes/tropi/cliente.json`, `clientes/tropi/visual.md`
- Modify: `tests/test_skills.py` (acrescentar teste das 7 skills e do cliente Tropi)

**Interfaces:**
- Consumes: fichas (Task 8), ferramentas (Tasks 1-4), manifesto e site (Tasks 4-7).
- Produces: `clientes/<slug>/<mes>/pauta.md`; pastas `posts/<nn>-<slug>/` com `post.json` (Task 4); `clientes/<slug>/<mes>/retorno.md`. `clientes/tropi/cliente.json` = `{slug, nome, arroba, site, pasta_marca, catalogo, visual}`.

- [ ] **Step 1: Escrever os testes que falham**

Em `tests/test_skills.py`, acrescentar `import json` junto dos outros imports no topo e estes testes no fim:

```python
def test_existem_as_sete_skills():
    nomes = {p.parent.name for p in SKILLS}
    assert nomes == {"ig-onboarding", "ig-pauta", "ig-carrossel", "ig-post",
                     "ig-legenda", "ig-humano", "ig-entrega"}


def test_cliente_tropi_valido():
    cliente = json.loads((RAIZ / "clientes" / "tropi" / "cliente.json").read_text(encoding="utf-8"))
    for campo in ["slug", "nome", "arroba", "site", "pasta_marca", "visual"]:
        assert cliente.get(campo), campo
    assert cliente["slug"] == "tropi"
    assert (RAIZ / cliente["visual"]).exists()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `uv run pytest tests/test_skills.py -v`
Expected: FAIL em `test_existem_as_sete_skills` e `test_cliente_tropi_valido`

- [ ] **Step 3: Criar `.claude/skills/ig-pauta/ganchos.md`**

```markdown
# Fórmulas de gancho (MVP, PT-BR)

Subconjunto adaptado das 26 fórmulas de `hooks.json` (Jake Schincariol, MIT) e
das fórmulas de carrossel de `instagram-skills` (Serge Bulaev, MIT). A tradução
completa é a Fase 2. A pauta usa o código na coluna "Gancho".

| Código | Nome | Molde | Quando usar | Como estraga |
|---|---|---|---|---|
| G1 | Número primeiro | "{número} {coisa} que {resultado}" | lista, dado real | número inventado ou redondo demais |
| G2 | Ninguém conta | "Ninguém conta que {fato contraintuitivo}" | bastidor, curiosidade | fato que todo mundo sabe |
| G3 | História com custo | "{coisa} custou {preço ou esforço} e {virada}" | origem de produto, garimpo | custo sem número ou sem virada |
| G4 | Contraponto | "{crença comum}? {o que a marca vê}" | opinião da marca | contrariar só por contrariar |
| G5 | Antes e depois | "De {estado A} a {estado B}" | transformação, restauro, coleção | antes genérico |
| G6 | Lista para guardar | "{n} {itens} para {situação}" | curadoria, guia | lista sem critério |
| G7 | Mito | "Não, {mito}. {verdade curta}." | corrigir crença do nicho | tom de professor |
| G8 | Detalhe que só a marca sabe | "{detalhe específico} deste {produto}" | produto, lançamento | detalhe que está na ficha técnica de qualquer loja |

Regra: o gancho da capa tem até 6 palavras. O molde é ponto de partida; a frase
final segue `voz.md`.
```

- [ ] **Step 4: Criar `.claude/skills/ig-pauta/SKILL.md`**

```markdown
---
name: ig-pauta
description: Monta a pauta mensal de Instagram de um cliente (8 a 12 posts entre estáticos e carrosséis) a partir das fichas, do histórico e das fontes do cliente, e cria as pastas dos posts depois da aprovação de Lucas. Usar quando Lucas pedir a pauta ou o conteúdo de um mês.
---

# ig-pauta

Adaptado de `ig-plan` (Jake Schincariol, MIT; ver THIRD_PARTY.md), de semana para
mês e de criador para marca.

## Entradas

- `clientes/<slug>/marca.md` e `voz.md` (obrigatórias; se faltarem, rodar `ig-onboarding`).
- Pautas e `aprovacao.json` dos dois meses anteriores, se existirem.
- `cliente.json` campo `catalogo` (na Tropi, exportação da loja em CSV): produtos
  novos e destaques viram ideias.
- Datas do mês que importam ao setor (Lucas confirma no chat).
- Fórmulas de gancho: `ganchos.md` nesta pasta.

## Regras

- 8 a 12 posts. Mistura de `carrossel` e `estatico`; carrossel é o formato principal
  (pelo menos metade).
- Temas vêm da seção 6 de `marca.md`. Não repetir o mesmo tema em posts seguidos.
- No máximo 2 posts seguidos no mesmo formato.
- No máximo 1 a 2 posts de oferta no mês.
- Não repetir ideia já usada nos dois meses anteriores.
- A ideia é um fato específico, não um assunto. "Vinil" não é pauta; "o lote de
  prensagens japonesas que chegou na terça" é.
- Toda ideia diz de onde veio (catálogo, data, ficha, Lucas).

## Saída

`clientes/<slug>/<AAAA-MM>/pauta.md`:

    # Pauta <Mês AAAA> · <Nome>

    | Nº | Data | Formato | Tema | Gancho | Ideia | Fonte |
    |---|---|---|---|---|---|---|
    | 01 | 07/10 | carrossel | Lançamento | G8 | ... | catálogo |

## Passos

1. Ler as entradas. Perguntar a Lucas, numa mensagem só, datas e novidades do mês
   que não estão nos arquivos.
2. Escrever `pauta.md` e mostrar a tabela a Lucas.
3. Ajustar até Lucas aprovar. Não produzir nada antes da aprovação.
4. Depois de aprovada, criar para cada linha `posts/<nn>-<slug-da-ideia>/post.json`:

       {"numero": 1, "tema": "Lançamento", "formato": "carrossel",
        "data_sugerida": "2026-10-07", "alt": ""}

   O nome da pasta: número com 2 dígitos, hífen, slug em minúsculas sem acento
   (ex.: `01-afim-ze-ibarra`). O manifesto recusa outro formato.
5. Commit da pauta e das pastas.
```

- [ ] **Step 5: Criar `.claude/skills/ig-carrossel/SKILL.md`**

```markdown
---
name: ig-carrossel
description: Produz um carrossel da pauta aprovada, com texto dos slides, slides HTML no sistema visual do cliente, imagens JPG 1080x1350 e legenda. Usar para cada post de formato carrossel em clientes/<slug>/<mes>/posts/.
---

# ig-carrossel

Adaptado de `ig-carousel` (Jake Schincariol, MIT; ver THIRD_PARTY.md).

## Estrutura (4 a 10 slides)

    1         CAPA      o gancho, até 6 palavras, legível na miniatura da grade
    2         O PORQUÊ  por que isso importa, em uma frase (funciona como segunda capa)
    3 a N-1   UMA IDEIA POR SLIDE  título de 3 a 7 palavras + até 25 palavras
    N         FECHO     resumo ou citação, o slide que dá vontade de guardar
    (último)  PEDIDO    um só: arrastar, salvar, link na bio

Nunca encher para chegar num número. Menos de 4 slides vira post estático.

## Passos

1. Ler a linha da pauta, `post.json`, `marca.md`, `voz.md` e o `visual` do
   `cliente.json` (na Tropi, `clientes/tropi/visual.md`).
2. Escrever o texto de todos os slides numa lista numerada em `posts/<id>/texto.md`.
3. Passar `texto.md` pelo `ig-humano`.
4. Escrever `slide-1.html` ... `slide-N.html` na pasta do post seguindo o
   `visual.md` do cliente (cabeçalho, classes, fundos, contador). Se o post usa
   imagem de produto, seguir a seção "Imagem de produto" do `visual.md`.
5. Renderizar:

       uv run python -m ferramentas.renderizar clientes/<slug>/<mes>/posts/<id>

6. Abrir cada JPG com Read e conferir: texto cortado, fonte que não carregou,
   alinhamento, contraste, miniatura legível. Corrigir e renderizar de novo.
7. Preencher `alt` no `post.json` (descrição da capa em uma frase).
8. Escrever a legenda com `ig-legenda`.
9. Apagar `texto.md` só depois que os slides estiverem fechados (manter se Lucas
   quiser revisar o texto sem abrir HTML).
```

- [ ] **Step 6: Criar `.claude/skills/ig-post/SKILL.md`**

```markdown
---
name: ig-post
description: Produz um post estático (uma imagem) da pauta aprovada, com slide HTML no sistema visual do cliente, JPG 1080x1350 e legenda. Usar para cada post de formato estatico em clientes/<slug>/<mes>/posts/.
---

# ig-post

## Estrutura

Uma imagem 1080x1350 com:
- título de até 8 palavras (o gancho);
- apoio opcional de até 20 palavras;
- marca e @ do cliente, como no `visual.md`.

A legenda carrega o contexto que a imagem não cabe.

## Passos

1. Ler a linha da pauta, `post.json`, `marca.md`, `voz.md` e o `visual.md` do cliente.
2. Escrever título e apoio; passar pelo `ig-humano`.
3. Escrever `slide-1.html` seguindo o `visual.md`.
4. Renderizar:

       uv run python -m ferramentas.renderizar clientes/<slug>/<mes>/posts/<id>

5. Abrir o JPG com Read e conferir (mesmos critérios do `ig-carrossel`).
6. Preencher `alt` no `post.json`.
7. Escrever a legenda com `ig-legenda`.
```

- [ ] **Step 7: Criar `.claude/skills/ig-entrega/SKILL.md`**

```markdown
---
name: ig-entrega
description: Publica o mês de um cliente na página de aprovação (manifesto, imagens, GitHub Pages) e depois aplica o retorno do aprovacao.json. Usar quando todos os posts do mês estiverem prontos, ou quando Lucas trouxer um aprovacao.json.
---

# ig-entrega

## Publicar

1. Conferir que todo post da pauta tem `post.json`, JPGs e `legenda.md` com
   veredito `PRONTA` (ou `REVISAR` justificado).
2. Gerar o manifesto e copiar para o site:

       uv run python -m ferramentas.manifesto clientes/<slug>/<AAAA-MM> --site site

   Se recusar, corrigir o que a mensagem aponta e rodar de novo.
3. Rodar os testes: `uv run pytest` e `node --test`.
4. Conferir localmente: `cd site && python3 -m http.server 8000`, entrar com o
   e-mail do cliente e abrir o mês (mesmos pontos do Step 8 da Task 7 do plano).
5. Commit e push:

       git add clientes/<slug>/<AAAA-MM> site/clientes/<slug>
       git commit -m "conteudo(<slug>): <AAAA-MM> publicado para aprovação"
       gh auth switch --user lucaslanzoni
       git push origin main
       gh auth switch --user lucaslanzoni-taqtile

6. Esperar o deploy (`gh run watch` no workflow "Publicar site"), abrir
   `https://lucaslanzoni.github.io/instagram-agent/` e conferir o mês no ar.
7. Mandar a Lucas o link e o e-mail cadastrado.

## Aplicar o retorno

1. Lucas coloca `aprovacao-<slug>-<mes>.json` em `clientes/<slug>/<AAAA-MM>/aprovacao.json`.
2. Para cada post:
   - `aprovado`: nada a fazer.
   - `descartado`: registrar em `retorno.md`; não apagar a pasta.
   - `revisar`: aplicar o `comentario` (texto, slide ou legenda), renderizar de
     novo e passar por `ig-humano`/`ig-legenda`.
   - `legenda_editada`: gravar em `legenda.md` como está, sem reescrever.
3. Escrever `clientes/<slug>/<AAAA-MM>/retorno.md`: o que mudou em cada post e
   padrões que se repetem (palavra trocada sempre, tipo de post recusado).
4. Propor a Lucas ajustes em `voz.md` ou `marca.md` a partir desses padrões.
   Só editar as fichas com aprovação.
5. Republicar seguindo "Publicar". O estado de aprovação guardado no navegador do
   cliente continua valendo para os posts que seguem no manifesto.
```

- [ ] **Step 8: Criar `clientes/tropi/cliente.json`**

```json
{
  "slug": "tropi",
  "nome": "Tropi Discos",
  "arroba": "@tropi_discos",
  "site": "https://www.tropidiscos.com.br",
  "pasta_marca": "/Users/Lucas/Documents/Freelas/tropi-discos",
  "catalogo": "/Users/Lucas/Documents/Freelas/tropi-discos/referencias/tiendanube-2149810-17757457361647180769126740978.csv",
  "visual": "clientes/tropi/visual.md"
}
```

- [ ] **Step 9: Criar `clientes/tropi/visual.md`**

````markdown
# Sistema visual da Tropi para slides

Fonte canônica: `~/Documents/Freelas/tropi-discos/branding/` (identidade "Duas
Estações") e o carrossel de referência `branding/carrossel/afim-ze-ibarra/`. Não
copiar o CSS para este repositório: os slides apontam para ele.

## Cabeçalho de todo slide

```html
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,900;1,9..144,500&family=Inter:wght@400;500;600;700&family=Archivo:wght@700;900&display=swap" rel="stylesheet">
<link href="file:///Users/Lucas/Documents/Freelas/tropi-discos/branding/carrossel/afim-ze-ibarra/base-retrato.css" rel="stylesheet">
</head>
```

## Fundos (classe no `<body>`)

- `bg-papel`: capa e slides de conteúdo (texto grafite).
- `bg-sunset` (com `<div class="rays"></div>`): citação, fecho e pedido.
- `bg-night`: alternativa escura para conteúdo, no máximo 1 por carrossel.
- `bg-orange`: destaque pontual, no máximo 1 por carrossel.

## Estrutura de cada slide

- Topo: `<div class="row"><span class="brand">Tropi Discos</span> ... </div>`.
  Na capa e no pedido, à direita vai um `kicker`; nos demais, o contador
  `<span class="count"><b>02</b> / 06</span>`.
- Meio: `<div class="block">` com `kicker`, `ttl` ou `ttl-xl`, `body`, `quote` +
  `cite`, `names` + `tag`, `cta`.
- Rodapé: `<div class="row"><span class="handle">@tropi_discos</span></div>`; na
  capa, acrescentar `<span class="handle" style="opacity:.8">arrasta →</span>`.

## Imagem de produto (disco)

Usar a skill `carrossel-disco` para baixar a capa e gerar `disco-cutout.png`
(`~/.claude/skills/carrossel-disco/scripts/prepare_images.py`), salvando na pasta
do post. Na capa: `<img class="cutout" src="disco-cutout.png" style="width:920px">`.

## Regras da marca que valem nos slides

- Sem preço (varia com promoção).
- Sem exclamação.
- Sem "não é X, é Y".
- Fala de obra, artista e edição, nunca de "oferta".
- No slide de pedido de post de disco, o `taghint` no canto inferior direito marca
  onde ancorar a tag de produto no app.
````

- [ ] **Step 10: Rodar e ver passar**

Run: `uv run pytest -v && node --test`
Expected: pytest com todos os testes passando (skips só se faltar Chrome); node com 27 pass

- [ ] **Step 11: Commit**

```bash
git add .claude/skills/ig-pauta .claude/skills/ig-carrossel .claude/skills/ig-post .claude/skills/ig-entrega clientes/tropi tests/test_skills.py
git commit -m "feat(skills): pauta, carrossel, post, entrega e cliente Tropi

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: Publicação no GitHub Pages

**Files:**
- Create: `.github/workflows/pages.yml`

**Interfaces:**
- Produces: site público em `https://lucaslanzoni.github.io/instagram-agent/`; deploy a cada push em `main` que mexa em `site/`.

- [ ] **Step 1: Criar `.github/workflows/pages.yml`**

```yaml
name: Publicar site

on:
  push:
    branches: [main]
    paths: ["site/**", ".github/workflows/pages.yml"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  publicar:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site
      - id: deploy
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Rodar todos os testes antes de publicar**

Run: `uv run pytest && node --test`
Expected: tudo passando

- [ ] **Step 3: Commit do workflow**

```bash
git add .github/workflows/pages.yml
git commit -m "ci: publica site/ no GitHub Pages

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Criar o repositório público, ativar o Pages e enviar (ação externa aprovada por Lucas: repositório público na conta pessoal)**

```bash
gh auth switch --user lucaslanzoni
gh repo create lucaslanzoni/instagram-agent --public --source . --remote origin --push
gh api -X POST repos/lucaslanzoni/instagram-agent/pages -f build_type=workflow
gh workflow run pages.yml
gh run watch "$(gh run list --workflow pages.yml --limit 1 --json databaseId -q '.[0].databaseId')"
gh auth switch --user lucaslanzoni-taqtile
```
Expected: repositório criado, workflow "Publicar site" termina com sucesso.

- [ ] **Step 5: Conferir no ar**

Run: `curl -s -o /dev/null -w "%{http_code}\n" https://lucaslanzoni.github.io/instagram-agent/ && curl -s https://lucaslanzoni.github.io/instagram-agent/acesso.json`
Expected: `200` e o JSON de acesso.
Abrir o endereço no navegador, entrar com `lucaslanzoni.s@gmail.com`, abrir o formulário. Mesmo comportamento da Task 6.

---

### Task 11: Piloto Tropi, do formulário ao mês aprovado

Tarefa operacional, feita com Lucas. Não cria código novo; valida o MVP contra os critérios de sucesso da spec (seção 9).

**Files:**
- Create (gerados pelo fluxo): `clientes/tropi/respostas.json`, `clientes/tropi/marca.md`, `clientes/tropi/voz.md`, `clientes/tropi/<AAAA-MM>/pauta.md`, `clientes/tropi/<AAAA-MM>/posts/*`, `clientes/tropi/<AAAA-MM>/aprovacao.json`, `clientes/tropi/<AAAA-MM>/retorno.md`, `site/clientes/tropi/<AAAA-MM>/*`

- [ ] **Step 1: Formulário**

Lucas responde o formulário no site publicado, pelo celular, e manda o arquivo baixado. Salvar como `clientes/tropi/respostas.json`.
Registrar: tempo de preenchimento e qualquer dúvida de uso que Lucas tiver.

- [ ] **Step 2: Fichas**

Rodar a skill `ig-onboarding` para `tropi`. Lucas revisa `marca.md` e `voz.md`.
Critério 2 da spec: a lista de divergências do passo 7 da skill não pode ter item que já estava documentado na pasta da Tropi e ficou de fora das fichas. Se tiver, anotar qual pergunta faltou no formulário.

- [ ] **Step 3: Pauta**

Rodar a skill `ig-pauta` para o próximo mês. Lucas aprova a pauta no chat.

- [ ] **Step 4: Produção**

Para cada post: `ig-carrossel` ou `ig-post`. Registrar o tempo total (critério 3: o mês inteiro numa sessão de trabalho).

- [ ] **Step 5: Entrega**

Rodar a skill `ig-entrega` (Publicar). Lucas abre o link no celular, aprova, edita, baixa e envia `aprovacao.json`.
Critério 4: Lucas consegue fazer tudo sem ajuda. Anotar cada ponto de atrito.

- [ ] **Step 6: Retorno e medição**

Rodar a skill `ig-entrega` (Aplicar o retorno). Contar quantos posts Lucas publicaria com pouca ou nenhuma edição (critério 1: pelo menos 7 de 10).
Escrever `clientes/tropi/<AAAA-MM>/retorno.md` com os quatro critérios, o resultado de cada um e a lista de ajustes para a próxima rodada.

- [ ] **Step 7: Commit**

```bash
git add clientes/tropi site/clientes/tropi
git commit -m "conteudo(tropi): piloto do primeiro mês e medição do MVP

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
gh auth switch --user lucaslanzoni && git push origin main && gh auth switch --user lucaslanzoni-taqtile
```
