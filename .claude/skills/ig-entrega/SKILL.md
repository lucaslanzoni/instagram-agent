---
name: ig-entrega
description: Publica o mês de um cliente na página de aprovação (manifesto, imagens, GitHub Pages) e depois aplica o retorno do aprovacao.json. Usar quando todos os posts do mês estiverem prontos, ou quando Lucas trouxer um aprovacao.json.
---

# ig-entrega

## Publicar

1. Conferir que todo post da pauta tem `post.json`, JPGs e `legenda.md` com
   veredito `PRONTA` (ou `REVISAR` justificado).
2. Gerar o manifesto e copiar para o site:

       uv run python -m ferramentas.manifesto clientes/<slug>/<AAAA-MM> --site site

   Se recusar, corrigir o que a mensagem aponta e rodar de novo.
3. Rodar os testes: `uv run pytest` e `node --test`.
4. Conferir localmente: `cd site && python3 -m http.server 8000`, entrar com o
   e-mail do cliente e abrir o mês. Conferir:
   - lateral com nome, mês, @ e contagem de publicações;
   - grade com todos os posts;
   - carrossel passa entre os slides;
   - status e comentário persistem ao recarregar a página;
   - legenda editável;
   - baixar um post e baixar o mês;
   - enviar aprovação;
   - 375px de largura sem rolagem horizontal.
5. Commit e push:

       git add clientes/<slug>/<AAAA-MM> site/clientes/<slug>
       git commit -m "conteudo(<slug>): <AAAA-MM> publicado para aprovação"
       gh auth switch --user lucaslanzoni
       git push origin main
       gh auth switch --user lucaslanzoni-taqtile

6. Esperar o deploy (`gh run watch` no workflow "Publicar site"), abrir
   `https://lucaslanzoni.github.io/instagram-agent/` e conferir o mês no ar.
7. Mandar a Lucas o link e o e-mail cadastrado.

## Aplicar o retorno

1. Lucas coloca `aprovacao-<slug>-<mes>.json` em `clientes/<slug>/<AAAA-MM>/aprovacao.json`.
2. Conferir a `versao` de cada entrada contra a `versao` do post correspondente no
   `manifesto.json` publicado (`site/clientes/<slug>/<AAAA-MM>/manifesto.json`).
   Entradas cuja `versao` não bate com a do post atual são de uma revisão
   anterior: ignorar e registrar em `retorno.md`.
3. Para cada entrada com `versao` correspondente:
   - `aprovado`: nada a fazer.
   - `descartado`: registrar em `retorno.md`; não apagar a pasta.
   - `revisar`: aplicar o `comentario` (texto, slide ou legenda), renderizar de
     novo e passar por `ig-humano`/`ig-legenda`.
   - `legenda_editada`: gravar em `legenda.md` como está, sem reescrever.
4. Escrever `clientes/<slug>/<AAAA-MM>/retorno.md`: o que mudou em cada post,
   as entradas de versão antiga ignoradas, e padrões que se repetem (palavra
   trocada sempre, tipo de post recusado).
5. Propor a Lucas ajustes em `voz.md` ou `marca.md` a partir desses padrões.
   Só editar as fichas com aprovação.
6. Republicar seguindo "Publicar". Depois de republicar, os posts revisados
   voltam a "pendente" na página do cliente; os demais mantêm o status.
