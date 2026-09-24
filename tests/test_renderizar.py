import shutil
from pathlib import Path

import pytest

from ferramentas.renderizar import (
    CHROME,
    dimensoes,
    ordenar_slides,
    renderizar,
    renderizar_post,
)

TEM_CHROME = Path(CHROME).exists() and shutil.which("sips") is not None
HTML = (
    "<!DOCTYPE html><html><body style='margin:0;width:1080px;height:1350px;"
    "background:#FB5607'></body></html>"
)


def test_ordena_slides_por_numero_e_ignora_outros():
    arquivos = [
        Path("slide-10.html"),
        Path("slide-2.html"),
        Path("slide-1.html"),
        Path("capa.html"),
    ]
    assert [p.name for p in ordenar_slides(arquivos)] == [
        "slide-1.html",
        "slide-2.html",
        "slide-10.html",
    ]


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
