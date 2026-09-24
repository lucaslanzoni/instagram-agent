# Sistema visual da Tropi para slides

Fonte canônica: `~/Documents/Freelas/tropi-discos/marca/` (virada para a paleta Café e Goiaba em andamento; os slides seguem a identidade "Duas
Estações") e o carrossel de referência `pecas/carrossel/afim-ze-ibarra/`. Não
copiar o CSS para este repositório: os slides apontam para ele.

## Cabeçalho de todo slide

```html
<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,900;1,9..144,500&family=Inter:wght@400;500;600;700&family=Archivo:wght@700;900&display=swap" rel="stylesheet">
<link href="file:///Users/Lucas/Documents/Freelas/tropi-discos/pecas/carrossel/afim-ze-ibarra/base-retrato.css" rel="stylesheet">
</head>
```

## Fundos (classe no `<body>`)

- `bg-papel`: capa e slides de conteúdo (texto grafite).
- `bg-sunset` (com `<div class="rays"></div>`): citação, fecho e pedido.
- `bg-night`: alternativa escura para conteúdo, no máximo 1 por carrossel.
- `bg-orange`: destaque pontual, no máximo 1 por carrossel.

## Estrutura de cada slide

- Topo: `<div class="row"><span class="brand">Tropi Discos</span> ... </div>`.
  Na capa e no pedido, à direita vai um `kicker`; nos demais, o contador
  `<span class="count"><b>02</b> / 06</span>`.
- Meio: `<div class="block">` com `kicker`, `ttl` ou `ttl-xl`, `body`, `quote` +
  `cite`, `names` + `tag`, `cta`.
- Rodapé: `<div class="row"><span class="handle">@tropi_discos</span></div>`; na
  capa, acrescentar `<span class="handle" style="opacity:.8">arrasta →</span>`.

## Imagem de produto (disco)

Usar a skill `carrossel-disco` para baixar a capa e gerar `disco-cutout.png`
(`~/.claude/skills/carrossel-disco/scripts/prepare_images.py`), salvando na pasta
do post. Na capa: `<img class="cutout" src="disco-cutout.png" style="width:920px">`.

## Regras da marca que valem nos slides

- Sem preço (varia com promoção).
- Sem exclamação.
- Sem "não é X, é Y".
- Fala de obra, artista e edição, nunca de "oferta".
- No slide de pedido de post de disco, o `taghint` no canto inferior direito marca
  onde ancorar a tag de produto no app.
