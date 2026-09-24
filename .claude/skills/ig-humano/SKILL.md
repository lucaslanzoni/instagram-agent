---
name: ig-humano
description: Passa texto de slide ou legenda pelo humanizador em PT-BR com a lista de proibidas do cliente e reescreve o que a ferramenta só sinaliza. Usar antes de fechar qualquer texto que vai para um post.
---

# ig-humano

Adaptado de `ig-human` (Jake Schincariol, MIT; ver THIRD_PARTY.md).

## Passos

1. Salvar o rascunho em `clientes/<slug>/<mes>/posts/<id>/rascunho.txt`.
2. Rodar, da raiz do repositório:

       uv run python -m ferramentas.humanizar clientes/<slug>/<mes>/posts/<id>/rascunho.txt --voz clientes/<slug>/voz.md --saida clientes/<slug>/<mes>/posts/<id>/rascunho.txt --relatorio

3. Ler o relatório:
   - Invisíveis, tipográficos e léxico já foram corrigidos no arquivo.
   - **Estruturas** e **proibidas do cliente** NÃO são corrigidas pela ferramenta.
     Reescrever essas frases à mão, seguindo `voz.md` (pilares, exemplos, o que a
     marca nunca faz). Não trocar uma palavra proibida por sinônimo que diga o
     mesmo; mudar a frase.
4. Rodar de novo até sair com código 0 (nenhuma proibida). Estrutura que continuar
   sinalizada só fica se Claude conseguir justificar em uma linha por que ela é da
   voz da marca; registrar a justificativa no chat.
5. Apagar `clientes/<slug>/<mes>/posts/<id>/rascunho.txt` depois de copiar o
   texto final para o slide ou para `legenda.md`.

## Limites

- O léxico em PT-BR é curto (Fase 2 traduz o do Jake inteiro). Ler o texto com os
  olhos da marca depois da ferramenta: ela pega marca de máquina, não pega texto
  genérico.
- Texto de slide é curto por natureza: não encher nem picotar slide por ritmo.
