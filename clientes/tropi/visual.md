# Sistema visual da Tropi para slides

Identidade padrão: **Café e Goiaba** (virada de marca de set/2026). Fonte canônica:
`~/Documents/Freelas/tropi-discos/marca/` (tokens, logo final, elementos, guia de
ilustração). Não copiar ativos de marca para este repositório: os slides apontam
para lá.

A identidade anterior (laranja, "duas estações", `pecas/carrossel/.../base-retrato.css`)
só vale para o post de transição que anuncia a mudança. Nenhum outro post usa o laranja.

## Regras de Lucas (2026-09-24)

- Todo post novo sai 100% na identidade Café e Goiaba. Posts fixados no perfil
  (ex.: guia de setup) e guias (ex.: cuidado com o disco) sempre na identidade nova.
- Ilustração em vez de foto improvisada. Quando o post fala de um objeto ou gesto
  (toca-discos, caixa, amplificador, mão segurando o disco), usar ilustração no
  estilo da marca. O que não existir em `marca/elementos/` é criado com
  `marca/elementos/gerador/desenho.js`, seguindo `marca/elementos/GUIA-ILUSTRACAO.md`
  (skill `ilustracao-tropi` no repo da Tropi). Fone de ouvido, escova e outros
  objetos do vocabulário da marca podem ser criados. Nota musical isolada não.
- Elemento novo vai primeiro para uma página em `marca/estudos/` e só entra em
  `marca/elementos/` depois da aprovação de Lucas.
- Disco de catálogo nunca com fundo branco de foto de produto. Usar o recorte
  (capa + vinil, sem fundo) com `.claude/skills/carrossel-disco/scripts/prepare_images.py`
  do repo da Tropi, conferindo o resultado. Se o recorte falhar (capa escura ou
  full-bleed), usar só a capa quadrada. Última opção: buscar uma imagem só da capa.
- Nada de imagem solta, torta ou sem função no slide.
- Mão com disco: recusada (2026-09-24). Para gesto com o disco, usar só a ilustração do vinil (`disco`).
- Capa de disco: quando o recorte capa + vinil não fica limpo, usar a capa quadrada pura. Fontes que
  funcionaram: a imagem "só capa" do produto no site da Tropi (quando existe), a Wikipédia (capa
  original) e a página do produto no Noize Record Club (Shopify, `/products/<slug>.json`), cortando
  só o quadrado da capa. Nunca capa com vinil do lado quando a imagem não estiver limpa.
- Texto da nova identidade sem literalidade: o mascote é "o mascote" (não "disco
  com olhinhos"); o coqueiro serve para dizer que a marca ficou mais tropical, e
  aparece sozinho (`coqueiro-02-simples`), sem o sol.

## Como montar um slide

- Cabeçalho: fontes Syne e Hanken Grotesk (Google Fonts) e o CSS
  `file:///Users/Lucas/Code/freelas/instagram-agent/clientes/tropi/cafe-goiaba.css`,
  que importa `marca/tokens/cores.css` e `marca/tokens/tipografia.css`.
- Fundo no `<body>`: `bg-creme` (padrão), `bg-goiaba`, `bg-oliva`, `bg-cafe`.
- Topo: logo final (`marca/logo/final/logo/tropi-logo-cafe.svg`; `-creme` no fundo
  café) + `rotulo` ou `count`.
- Meio: `bloco` com `rotulo`, `ttl-xl` ou `ttl`, `texto`, `tags`, `cta`, `itens`.
- Rodapé: `@tropi_discos`; na capa de carrossel, "arrasta →".
- Elementos prontos: `<img class="elemento" src=".../marca/elementos/<tipo>/fundo-<fundo>/<arquivo>.svg">`,
  sempre da pasta do mesmo fundo do slide.
- Elementos desenhados na hora: `<div class="desenho" data-elemento="<nome>" data-fundo="<fundo>">`
  e, no fim do body, `desenho.js` + `marca/estudos/elementos-posts-outubro.js` +
  `TropiPosts.desenharTodos()`.
- Disco recortado: `<img class="cutout" src="disco-cutout.png">`.

## Regras da marca que valem nos slides

- Sem preço (varia com promoção).
- Sem "não é X, é Y".
- Fala de obra, artista e edição, nunca de "oferta".
- Um elemento protagonista por slide; mascote e sol podem dividir sem competir.
