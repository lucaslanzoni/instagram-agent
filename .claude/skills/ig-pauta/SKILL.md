---
name: ig-pauta
description: Monta a pauta mensal de Instagram de um cliente (8 a 12 posts entre estáticos e carrosséis) a partir das fichas, do histórico e das fontes do cliente, e cria as pastas dos posts depois da aprovação de Lucas. Usar quando Lucas pedir a pauta ou o conteúdo de um mês.
---

# ig-pauta

Adaptado de `ig-plan` (Jake Schincariol, MIT; ver THIRD_PARTY.md), de semana para
mês e de criador para marca.

## Entradas

- `clientes/<slug>/marca.md` e `voz.md` (obrigatórias; se faltarem, rodar `ig-onboarding`).
- Pautas e `aprovacao.json` dos dois meses anteriores, se existirem.
- `cliente.json` campo `catalogo` (na Tropi, exportação da loja em CSV): produtos
  novos e destaques viram ideias.
- Datas do mês que importam ao setor (Lucas confirma no chat).
- Fórmulas de gancho: `ganchos.md` nesta pasta.

## Regras

- 8 a 12 posts. Mistura de `carrossel` e `estatico`; carrossel é o formato principal
  (pelo menos metade).
- Temas vêm da seção 6 de `marca.md`. Não repetir o mesmo tema em posts seguidos.
- No máximo 2 posts seguidos no mesmo formato.
- No máximo 1 a 2 posts de oferta no mês.
- Não repetir ideia já usada nos dois meses anteriores.
- A ideia é um fato específico, não um assunto. "Vinil" não é pauta; "o lote de
  prensagens japonesas que chegou na terça" é.
- Toda ideia diz de onde veio (catálogo, data, ficha, Lucas).

## Saída

`clientes/<slug>/<AAAA-MM>/pauta.md`:

    # Pauta <Mês AAAA> · <Nome>

    | Nº | Data | Formato | Tema | Gancho | Ideia | Fonte |
    |---|---|---|---|---|---|---|
    | 01 | 07/10 | carrossel | Lançamento | G8 | ... | catálogo |

## Passos

1. Ler as entradas. Perguntar a Lucas, numa mensagem só, datas e novidades do mês
   que não estão nos arquivos.
2. Escrever `pauta.md` e mostrar a tabela a Lucas.
3. Ajustar até Lucas aprovar. Não produzir nada antes da aprovação.
4. Depois de aprovada, criar para cada linha `posts/<nn>-<slug-da-ideia>/post.json`:

       {"numero": 1, "tema": "Lançamento", "formato": "carrossel",
        "data_sugerida": "2026-10-07", "alt": ""}

   O nome da pasta: número com 2 dígitos, hífen, slug em minúsculas sem acento
   (ex.: `01-afim-ze-ibarra`). O manifesto recusa outro formato.
5. Commit da pauta e das pastas.
