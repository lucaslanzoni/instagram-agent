---
name: ig-carrossel
description: Produz um carrossel da pauta aprovada, com texto dos slides, slides HTML no sistema visual do cliente, imagens JPG 1080x1350 e legenda. Usar para cada post de formato carrossel em clientes/<slug>/<mes>/posts/.
---

# ig-carrossel

Adaptado de `ig-carousel` (Jake Schincariol, MIT; ver THIRD_PARTY.md).

## Estrutura (4 a 10 slides)

    1         CAPA      o gancho, até 6 palavras, legível na miniatura da grade
    2         O PORQUÊ  por que isso importa, em uma frase (funciona como segunda capa)
    3 a N-1   UMA IDEIA POR SLIDE  título de 3 a 7 palavras + até 25 palavras
    N         FECHO     resumo ou citação, o slide que dá vontade de guardar
    (último)  PEDIDO    um só: arrastar, salvar, link na bio

Nunca encher para chegar num número. Menos de 4 slides vira post estático.

## Passos

1. Ler a linha da pauta, `post.json`, `marca.md`, `voz.md` e o `visual` do
   `cliente.json` (na Tropi, `clientes/tropi/visual.md`).
2. Escrever o texto de todos os slides numa lista numerada em `posts/<id>/texto.md`.
3. Passar `texto.md` pelo `ig-humano`.
4. Escrever `slide-1.html` ... `slide-N.html` na pasta do post seguindo o
   `visual.md` do cliente (cabeçalho, classes, fundos, contador). Se o post usa
   imagem de produto, seguir a seção "Imagem de produto" do `visual.md`.
5. Renderizar:

       uv run python -m ferramentas.renderizar clientes/<slug>/<mes>/posts/<id>

6. Abrir cada JPG com Read e conferir: texto cortado, fonte que não carregou,
   alinhamento, contraste, miniatura legível. Corrigir e renderizar de novo.
7. Preencher `alt` no `post.json` (descrição da capa em uma frase).
8. Escrever a legenda com `ig-legenda`.
9. Apagar `texto.md` só depois que os slides estiverem fechados (manter se Lucas
   quiser revisar o texto sem abrir HTML).
