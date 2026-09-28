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
