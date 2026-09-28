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
- Vídeo: permitido como fonte, mas o fluxo de renderização atual só gera imagem (JPG). Vídeo entra quando
  o agente passar a produzir Reels.

## Regras de composição

- Só as quatro cores da marca; nenhum filtro de cor na foto.
- Texto nunca em cima do rosto nem do disco que é assunto do post. Ajustar `posicao` (object-position)
  até o assunto ficar livre.
- No story, nada importante nas faixas de cima e de baixo que o Instagram cobre.
- Um elemento da marca por peça, no máximo.

## Como gerar

1. Salvar a foto na pasta do post (`foto.jpg`) e escrever `post-foto.json`
   (`modelo`, `foto`, `posicao`, `textos`, `fonte`).
2. `uv run python clientes/tropi/modelos-foto/gerar.py <pasta-do-post> [--story]`
3. `uv run python -m ferramentas.renderizar <pasta-do-post>` e conferir o JPG.
4. Legenda com `ig-legenda`, texto com `ig-humano`, publicação com `ig-entrega`.
