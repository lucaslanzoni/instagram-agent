---
name: ig-legenda
description: Escreve e verifica a legenda de um post de Instagram na voz do cliente, com gancho antes do corte de 125 caracteres, um pedido e de 3 a 5 hashtags. Usada por ig-carrossel e ig-post.
---

# ig-legenda

Adaptado de `ig-caption` (Jake Schincariol, MIT; ver THIRD_PARTY.md).

## Regras

- Os primeiros 125 caracteres são o que o feed mostra. O gancho mora ali: um fato,
  um nome, um número. Nada de "Oi, gente" nem hashtag na primeira linha.
- Carrossel: a legenda completa a capa, não repete a capa.
- Post estático: a legenda carrega mais contexto que a imagem.
- Um pedido só (salvar, comentar, link na bio, arrastar). Dois pedidos valem nenhum.
- Sem link no texto: link em legenda não é clicável; usar "link na bio".
- 3 a 5 hashtags no fim, específicas do assunto. Nenhuma genérica (#viral, #instagood).
- Tom, palavras, emoji e exclamação seguem `clientes/<slug>/voz.md`.
- Nunca citar preço, a não ser que a pauta peça.

## Passos

1. Escrever a legenda em `posts/<id>/legenda.md`.
2. Passar pelo `ig-humano`.
3. Verificar:

       uv run python -m ferramentas.legenda clientes/<slug>/<mes>/posts/<id>/legenda.md

4. Meta: veredito `PRONTA`. `REVISAR` só é aceito se o alerta for intencional
   (ex.: nome de artista que a ferramenta não vê como concreto); registrar o
   motivo no chat. `CORRIGIR` nunca vai para a entrega.
