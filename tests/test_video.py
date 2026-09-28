import json
import shutil
import subprocess

import pytest

from ferramentas.video import FFMPEG, aplicar_moldura, comando_moldura, montar_reels

TEM_FFMPEG = shutil.which(FFMPEG) is not None and shutil.which("ffprobe") is not None


def sondar(arquivo):
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,codec_name,width,height",
            "-of",
            "json",
            str(arquivo),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(r.stdout)["streams"]


def test_comando_ajusta_a_9x16_e_prepara_para_streaming():
    cmd = comando_moldura("in.mov", "moldura.png", "video.mp4")
    filtro = cmd[cmd.index("-filter_complex") + 1]
    assert "crop=1080:1920" in filtro and "overlay=0:0" in filtro
    assert cmd[cmd.index("-movflags") + 1] == "+faststart"
    assert "0:a?" in cmd  # áudio opcional
    assert cmd[-1] == "video.mp4"


def test_montar_reels_sem_video_no_json_da_erro(tmp_path):
    (tmp_path / "post-foto.json").write_text(
        json.dumps({"modelo": "adesivos"}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="video"):
        montar_reels(tmp_path)


@pytest.mark.skipif(not TEM_FFMPEG, reason="precisa de ffmpeg")
def test_aplica_moldura_em_video_horizontal_sem_audio(tmp_path):
    original = tmp_path / "in.mp4"
    subprocess.run(
        [
            FFMPEG,
            "-nostdin",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=640x360:rate=30:duration=1",
            str(original),
        ],
        check=True,
    )
    moldura = tmp_path / "moldura.png"
    subprocess.run(
        [
            FFMPEG,
            "-nostdin",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=black@0.0:size=1080x1920,format=rgba",
            "-frames:v",
            "1",
            str(moldura),
        ],
        check=True,
    )
    saida = aplicar_moldura(original, moldura, tmp_path / "video.mp4")
    streams = sondar(saida)
    video = [s for s in streams if s["codec_type"] == "video"][0]
    assert (video["codec_name"], video["width"], video["height"]) == (
        "h264",
        1080,
        1920,
    )
    assert not [s for s in streams if s["codec_type"] == "audio"]
