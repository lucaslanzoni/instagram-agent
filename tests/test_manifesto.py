import json

import pytest

from ferramentas.manifesto import montar_manifesto, publicar

CLIENTE = {"slug": "demo", "nome": "Loja Demo", "arroba": "@demo"}


def criar_post(
    pasta_mes,
    pid,
    numero,
    formato="carrossel",
    n_imagens=3,
    legenda="Legenda boa.\n\nLink na bio.",
):
    pasta = pasta_mes / "posts" / pid
    pasta.mkdir(parents=True)
    (pasta / "post.json").write_text(
        json.dumps(
            {
                "numero": numero,
                "tema": "Lançamento",
                "formato": formato,
                "data_sugerida": "2026-10-07",
                "alt": "capa do disco",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
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
    assert m["posts"][1]["imagens"] == [
        "02-segundo/1.jpg",
        "02-segundo/2.jpg",
        "02-segundo/3.jpg",
    ]
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
        json.dumps({"nome": "Loja Demo", "arroba": "@demo", "meses": ["2026-09"]}),
        encoding="utf-8",
    )

    caminho = publicar(mes, site, CLIENTE)
    publicar(mes, site, CLIENTE)  # republicar não duplica mês

    assert caminho == site / "clientes" / "demo" / "2026-10" / "manifesto.json"
    assert (site / "clientes" / "demo" / "2026-10" / "01-a" / "1.jpg").exists()
    indice = json.loads(
        (site / "clientes" / "demo" / "indice.json").read_text(encoding="utf-8")
    )
    assert indice["meses"] == ["2026-09", "2026-10"]
