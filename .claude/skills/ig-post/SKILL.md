---
name: ig-post
description: Produz um post estático (uma imagem) da pauta aprovada, com slide HTML no sistema visual do cliente, JPG 1080x1350 e legenda. Usar para cada post de formato estatico em clientes/<slug>/<mes>/posts/.
---

# ig-post

## Estrutura

Uma imagem 1080x1350 com:
- título de até 8 palavras (o gancho);
- apoio opcional de até 20 palavras;
- marca e @ do cliente, como no `visual.md`.

A legenda carrega o contexto que a imagem não cabe.

## Passos

1. Ler a linha da pauta, `post.json`, `marca.md`, `voz.md` e o `visual.md` do cliente.
2. Escrever título e apoio; passar pelo `ig-humano`.
3. Escrever `slide-1.html` seguindo o `visual.md`.
4. Renderizar:

       uv run python -m ferramentas.renderizar clientes/<slug>/<mes>/posts/<id>

5. Abrir o JPG com Read e conferir (mesmos critérios do `ig-carrossel`).
6. Preencher `alt` no `post.json`.
7. Escrever a legenda com `ig-legenda`.
