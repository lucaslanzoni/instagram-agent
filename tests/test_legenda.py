import unicodedata

from ferramentas.legenda import CORTE, analisar, contar_palavras, janela_visivel


def status(analise, nome):
    return next(c["status"] for c in analise["checagens"] if c["checagem"] == nome)


def test_conta_palavras_com_acento():
    assert contar_palavras("Ninguém te conta isso.") == 4


def test_conta_palavras_em_texto_nfd():
    nfd = unicodedata.normalize("NFD", "Ninguém te conta isso.")
    assert contar_palavras(nfd) == 4


def test_conta_palavras_com_apostrofo_curvo():
    assert contar_palavras("rock'n'roll é bom") == 3


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
