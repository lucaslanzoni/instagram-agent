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
    for secao in [
        "## 1. Identidade",
        "## 2. Público",
        "## 3. Produto e oferta",
        "## 4. Posicionamento",
        "## 5. Concorrentes",
        "## 6. Temas de conteúdo",
        "## 7. Insights",
    ]:
        assert secao in texto
