---
name: ig-post-foto
description: Produz um post de Instagram a partir de uma foto (enviada pelo cliente, de banco gratuito ou do Canva) aplicando um dos modelos aprovados de texto e elementos da marca. Usar quando a pauta tiver um post com foto ou quando Lucas mandar uma imagem para virar post.
---

# ig-post-foto

Posts com foto humanizam o feed entre os posts ilustrados. Cada cliente tem seus modelos
aprovados; na Tropi estão em `clientes/tropi/modelos-foto/` (regras em `README.md`, gerador em `gerar.py`).

## Passos

1. Escolher a foto:
   - a enviada pelo cliente; ou
   - de banco gratuito com licença de uso comercial, sobre o tema do post (pessoas com disco de vinil,
     toca-discos, loja, feira); ou
   - do Canva, pela conta do cliente.
   Registrar a origem no campo `fonte` de `post-foto.json`. Nada de foto com marca d'água ou licença incerta.
2. Escolher o modelo pelo uso (tabela do `README.md` do cliente). Na Tropi: `foto-cheia`, `encarte`,
   `meio-a-meio` ou `adesivos`.
3. Escrever os textos do modelo, no limite de palavras dele, e passar pelo `ig-humano`.
4. Salvar a foto como `foto.jpg` na pasta do post e escrever `post-foto.json`:

       {"modelo": "encarte", "foto": "foto.jpg", "posicao": "45% 40%",
        "fonte": "enviada por Lucas", "textos": {"rotulo": "...", "titulo": "...", "apoio": "..."}}

5. Gerar e renderizar:

       uv run python clientes/tropi/modelos-foto/gerar.py <pasta-do-post> [--story]
       uv run python -m ferramentas.renderizar <pasta-do-post>

6. Abrir o JPG e conferir: texto fora do rosto e do disco em destaque, nada cortado, cores só da marca.
   Ajustar `posicao` e gerar de novo quando o assunto ficar coberto.
7. Legenda com `ig-legenda`. Nunca inventar @ de parceiro: se o @ não for confirmado, usar
   `{{@ a confirmar}}` e perguntar a Lucas.
8. Seguir para `ig-entrega`.
