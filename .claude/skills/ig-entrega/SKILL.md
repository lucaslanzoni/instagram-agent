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
   e-mail do cliente e abrir o mês (mesmos pontos do Step 8 da Task 7 do plano).
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
2. Para cada post:
   - `aprovado`: nada a fazer.
   - `descartado`: registrar em `retorno.md`; não apagar a pasta.
   - `revisar`: aplicar o `comentario` (texto, slide ou legenda), renderizar de
     novo e passar por `ig-humano`/`ig-legenda`.
   - `legenda_editada`: gravar em `legenda.md` como está, sem reescrever.
3. Escrever `clientes/<slug>/<AAAA-MM>/retorno.md`: o que mudou em cada post e
   padrões que se repetem (palavra trocada sempre, tipo de post recusado).
4. Propor a Lucas ajustes em `voz.md` ou `marca.md` a partir desses padrões.
   Só editar as fichas com aprovação.
5. Republicar seguindo "Publicar". O estado de aprovação guardado no navegador do
   cliente continua valendo para os posts que seguem no manifesto.
