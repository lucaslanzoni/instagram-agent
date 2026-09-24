# Instagram Agent

Braço de criação de conteúdo para Instagram da consultoria. O cliente responde
um formulário; Claude gera ficha da marca e ficha de voz, monta a pauta do mês,
produz posts estáticos e carrosséis e publica uma página de aprovação.

Nada se conecta ao Instagram. Quem publica é o humano.

Spec: `docs/superpowers/specs/2026-09-23-instagram-agent-mvp-design.md`

## Testes

    uv run pytest
    node --test

## Site local

    cd site && python3 -m http.server 8000
    # abrir http://localhost:8000

## Publicar

O site em `site/` é publicado no GitHub Pages a cada push no `main`
(`.github/workflows/pages.yml`). Aviso: repositório público; o portão de e-mail
filtra a tela, não protege os arquivos.
