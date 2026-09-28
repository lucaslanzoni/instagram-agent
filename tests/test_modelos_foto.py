import importlib.util
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("modelos_foto", RAIZ / "clientes" / "tropi" / "modelos-foto" / "gerar.py")
modelos_foto = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(modelos_foto)


def preparar(tmp_path, modelo, textos):
    (tmp_path / "foto.jpg").write_bytes(b"jpg")
    (tmp_path / "post-foto.json").write_text(
        json.dumps({"modelo": modelo, "foto": "foto.jpg", "posicao": "40% 30%", "textos": textos}), encoding="utf-8")


def test_modelo_disco_foi_descartado():
    assert set(modelos_foto.MODELOS) == {"foto-cheia", "encarte", "meio-a-meio", "adesivos"}


def test_gera_post_e_story_e_escapa_texto(tmp_path):
    preparar(tmp_path, "encarte", {"rotulo": "Na feira", "titulo": "A <Tropi>", "apoio": "Segue a gente"})
    saidas = modelos_foto.gerar(tmp_path, story=True)
    assert [s.name for s in saidas] == ["slide-1.html", "story.html"]
    html = (tmp_path / "slide-1.html").read_text(encoding="utf-8")
    assert "A &lt;Tropi&gt;" in html
    assert "height:1920px" in (tmp_path / "story.html").read_text(encoding="utf-8")


def test_texto_faltando_e_recusado(tmp_path):
    preparar(tmp_path, "meio-a-meio", {"rotulo": "Chegando", "titulo": "Lançamentos"})
    with pytest.raises(ValueError, match="cta"):
        modelos_foto.gerar(tmp_path)


def test_modelo_desconhecido_e_recusado(tmp_path):
    preparar(tmp_path, "disco", {"rotulo": "x", "titulo": "y"})
    with pytest.raises(ValueError, match="modelo desconhecido"):
        modelos_foto.gerar(tmp_path)


def preparar_reels(tmp_path, modelo="adesivos", capa=True):
    (tmp_path / "original.mov").write_bytes(b"mov")
    (tmp_path / "capa-foto.jpg").write_bytes(b"jpg")
    spec = {"modelo": modelo, "video": "original.mov", "textos": {"etiqueta": "Parabéns, Tim!", "pilula": "84 anos"}}
    if capa:
        spec["capa"] = {"modelo": "encarte", "foto": "capa-foto.jpg",
                        "textos": {"rotulo": "Reels", "titulo": "Tim Maia", "apoio": "Aperta o play"}}
    (tmp_path / "post-foto.json").write_text(json.dumps(spec), encoding="utf-8")


def test_reels_gera_moldura_transparente_e_capa_vertical(tmp_path):
    preparar_reels(tmp_path)
    saidas = modelos_foto.gerar(tmp_path)
    assert [s.name for s in saidas] == ["moldura.html", "slide-1.html"]
    moldura = (tmp_path / "moldura.html").read_text(encoding="utf-8")
    assert "background:transparent" in moldura and 'class="foto"' not in moldura
    assert "Parabéns, Tim!" in moldura
    assert "height:1920px" in (tmp_path / "slide-1.html").read_text(encoding="utf-8")


def test_reels_sem_capa_ou_com_modelo_que_cobre_o_video_e_recusado(tmp_path):
    preparar_reels(tmp_path, capa=False)
    with pytest.raises(ValueError, match="capa"):
        modelos_foto.gerar(tmp_path)
    preparar_reels(tmp_path, modelo="encarte")
    with pytest.raises(ValueError, match="adesivos"):
        modelos_foto.gerar(tmp_path)


def test_adesivos_leva_o_sol_para_baixo_quando_pedido(tmp_path):
    (tmp_path / "foto.jpg").write_bytes(b"jpg")
    (tmp_path / "post-foto.json").write_text(json.dumps({"modelo": "adesivos", "foto": "foto.jpg", "elemento": "embaixo",
        "textos": {"etiqueta": "Oi", "pilula": "Tropi"}}), encoding="utf-8")
    modelos_foto.gerar(tmp_path)
    html = (tmp_path / "slide-1.html").read_text(encoding="utf-8")
    assert "right:40px;bottom:50px" in html
