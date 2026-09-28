# Posts com foto · Tropi

Aprovados por Lucas em 2026-09-28. Complementam os posts ilustrados: humanizam o feed
com gente e disco de vinil. Página de aprovação: https://claude.ai/artifact/GaWpy1YUdDd7gBK92BcCiX

## Modelos aprovados

| Modelo | Como é | Serve para | Textos |
|---|---|---|---|
| `foto-cheia` | Foto quase inteira, faixa creme embaixo com rótulo, título e logo | Disco disponível, garimpo da semana, aviso rápido | rótulo · título até 5 palavras · uma linha de apoio |
| `encarte` | Foto emoldurada em traço café, mascote colado no canto, texto embaixo | Indicação de disco, evento com um recado | rótulo · título até 7 palavras · uma linha de apoio |
| `meio-a-meio` | Foto em cima, bloco café embaixo com título e botão | Lançamentos chegando, anúncio com data, chamada para o site | rótulo · título até 6 palavras · botão (ex.: o site) |
| `adesivos` | Foto inteira com etiqueta goiaba, sol-disco e pílula café com o logo | Evento ao vivo, bastidor, stories do dia | etiqueta até 4 palavras · pílula curta |

Descartado: `disco` (foto dentro do rótulo do vinil).

## De onde vem a foto

- Fotos enviadas por Lucas (eventos, loja, bastidor).
- Bancos gratuitos de imagem com licença de uso comercial, com o tema da conversa: pessoas com disco de
  vinil, toca-discos, loja de discos, feira. Conferir a licença de cada imagem e registrar a fonte em
  `post-foto.json` (campo `fonte`).
- Imagens e vídeos do Canva que tenham pessoas com disco de vinil, baixados pela conta de Lucas.
- Vídeo: vira Reels com moldura da marca (ver "Reels" abaixo).

## Regras de composição

- Só as quatro cores da marca; nenhum filtro de cor na foto.
- Texto nunca em cima do rosto nem do disco que é assunto do post. Ajustar `posicao` (object-position)
  até o assunto ficar livre.
- No story, nada importante nas faixas de cima e de baixo que o Instagram cobre.
- Um elemento da marca por peça, no máximo.
- No `adesivos`, se o sol-disco cobrir um rosto no canto de cima, usar `"elemento": "embaixo"` no
  `post-foto.json`: o sol vai para o canto de baixo, ao lado da pílula.

## Reels (vídeo com moldura)

Aprovado por Lucas em 2026-09-28: a moldura fica **o vídeo inteiro**, e todo Reels tem uma **capa** desenhada.

- Moldura: modelo `adesivos` (etiqueta goiaba em cima, sol-disco, pílula café com o logo embaixo), em camada
  transparente 1080x1920 sobre o vídeo. É o modelo que menos cobre o vídeo; os outros não servem de moldura.
- Capa: 1080x1920 com qualquer modelo de foto, feita com um quadro nítido do vídeo
  (`ffmpeg -ss <segundo> -i original.mov -frames:v 1 -q:v 2 capa-foto.jpg`). Logo e título ficam dentro do
  corte 4:5 da grade (entre 285 e 1635 px de altura).
- Saída: `video.mp4` (H.264 + AAC, 1080x1920, `+faststart`) e `1.jpg` (a capa). O post leva `"formato": "reels"`.

```
{"modelo": "adesivos", "video": "original.mov", "fonte": "enviado por Lucas",
 "textos": {"etiqueta": "...", "pilula": "..."},
 "capa": {"modelo": "encarte", "foto": "capa-foto.jpg", "posicao": "50% 35%",
          "textos": {"rotulo": "...", "titulo": "...", "apoio": "..."}}}
```

1. `uv run python clientes/tropi/modelos-foto/gerar.py <pasta-do-post>` (gera `moldura.html` e `slide-1.html`)
2. `uv run python -m ferramentas.renderizar <pasta-do-post>` (capa)
3. `uv run python -m ferramentas.video <pasta-do-post>` (moldura em PNG transparente + `video.mp4`)
4. Assistir ao `video.mp4` e conferir um quadro: nada importante coberto, texto fora das faixas do Reels.

Os vídeos (`original.*`, `video.mp4`) ficam fora do git na pasta do post; só a cópia publicada no site entra.

## Como gerar

1. Salvar a foto na pasta do post (`foto.jpg`) e escrever `post-foto.json`
   (`modelo`, `foto`, `posicao`, `textos`, `fonte`).
2. `uv run python clientes/tropi/modelos-foto/gerar.py <pasta-do-post> [--story]`
3. `uv run python -m ferramentas.renderizar <pasta-do-post>` e conferir o JPG.
4. Legenda com `ig-legenda`, texto com `ig-humano`, publicação com `ig-entrega`.
