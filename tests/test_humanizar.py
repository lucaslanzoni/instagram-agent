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
