---
name: ig-onboarding
description: Transforma o respostas.json do formulário de um cliente em ficha da marca (marca.md) e ficha de voz (voz.md). Usar quando Lucas trouxer um respostas.json novo ou pedir para criar ou atualizar as fichas de um cliente.
---

# ig-onboarding

Entrada: `clientes/<slug>/respostas.json` (exportado pelo formulário do site) e
`clientes/<slug>/cliente.json`. Saída: `clientes/<slug>/marca.md` e
`clientes/<slug>/voz.md`, nos moldes de `modelos/ficha-marca.md` e
`modelos/ficha-voz.md`.

## Passos

1. Ler `respostas.json` e `cliente.json`. Listar perguntas sem resposta. Se faltar
   alguma de `marca_frase`, `empatia_*`, `voz_palavras`, `voz_frases` ou
   `posic_diferencial`, mostrar a lista a Lucas e perguntar se segue com lacunas.
2. Ler o site (`cliente.json` campo `site`) com WebFetch: o que vende, categorias,
   palavras que a marca já usa. Guardar as frases reais do site como exemplos.
3. Se `cliente.json` tiver `pasta_marca`, ler o `CLAUDE.md` e os documentos de
   branding dessa pasta. Eles têm prioridade sobre inferências.
4. Escrever `marca.md` a partir do molde, com este mapa:

   | Pergunta | Seção |
   |---|---|
   | marca_frase, marca_objetivo | 1. Identidade |
   | marca_links | cabeçalho (fonte) |
   | empatia_* | 2. Público |
   | site + pasta_marca | 3. Produto e oferta |
   | posic_diferencial, voz_defende | 4. Posicionamento |
   | posic_concorrentes | 5. Concorrentes |
   | todas | 6. Temas de conteúdo (3 a 5 pilares) |
   | leitura de Claude | 7. Insights, cada item marcado "(inferência)" |

5. Escrever `voz.md` a partir do molde, com este mapa:

   | Pergunta | Seção |
   |---|---|
   | voz_arquetipo (ids em ARQUETIPOS de `site/assets/perguntas.js`) | 1. Personalidade |
   | voz_festa, voz_defende | 1. Personalidade e 2. Pilares |
   | voz_palavras (parte "usa") | 4. O que a marca fala |
   | voz_palavras (parte "nunca usaria") + regras da marca | ## Proibidas, um termo por linha `- termo`, em minúsculas |
   | voz_frases | ## Exemplos, formato `- Ruim: <frase> \| Bom: <frase>` |

   Pares ruim/bom escritos por Claude levam "(Claude)" no fim da linha.
6. Regras: não inventar número, prêmio ou depoimento; o que faltar vira
   `{{a preencher}}`. Não mudar os títulos `## Proibidas` e `## Exemplos`: o
   humanizador lê o primeiro pelo título exato.
7. Comparar com o material de marca existente e listar a Lucas, em bullets, onde
   as respostas divergem ou deixam de fora algo que já está documentado. Isso
   mede se o formulário captura a marca.
8. Conferir: `uv run python -c "from ferramentas.humanizar import ler_proibidas; print(ler_proibidas(open('clientes/<slug>/voz.md').read()))"`
   devolve a lista esperada.
9. Mostrar a Lucas um resumo das duas fichas e ajustar. Commit das fichas.
