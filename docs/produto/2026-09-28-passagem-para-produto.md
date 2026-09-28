# Passagem: do piloto da Tropi para produto

Data: 2026-09-28. Documento de partida para a sessão que vai empacotar o instagram-agent como produto
da consultoria. Ler antes de qualquer pergunta a Lucas. Processo: superpowers:brainstorming, caminho
arquitetural (perguntas uma de cada vez, desenho em seções, spec escrita, plano, execução).

## Pedido de Lucas

Transformar a estrutura do instagram-agent num produto para outros clientes, usando a lógica de Harness
(validações e checagens formais em volta do agente), com segurança, e que o cliente use pelo celular
como criador de conteúdo. A Tropi continua usando o sistema normalmente.

## Decisões já tomadas

| Decisão | Resposta de Lucas | Data |
|---|---|---|
| Quem opera a criação | **Serviço operado**: a consultoria opera o agente; o cliente usa o celular para briefing, envio de fotos e vídeos, aprovação, edição de legenda e download | 2026-09-28 |
| Acesso ao Instagram | Nenhum. Nada se conecta à conta do cliente; quem publica é o humano. Exceção só para plataforma verificada, paga e com análise de segurança | 2026-09-23 |
| Fase de teste | Repositório público + GitHub Pages + portão de e-mail cosmético foram aceitos **só para o teste** | 2026-09-23 |
| Onde o produto mora | Repositório novo e privado com o nome do produto (nome a definir), só com o motor; dados de cada cliente fora do git, numa pasta por cliente em `~/Documents/Freelas/<produto>/clientes/<slug>/`. A Tropi fica no repositório atual | 2026-09-28 |
| Escala | 2 clientes externos, depois 5, depois 10, depois mais | 2026-09-28 |
| Custo | **Infra gratuita** na fase inicial; pagar só quando a receita dos clientes cobrir | 2026-09-28 |
| Harness | Vale para o produto **e também para a Tropi** (atualizar o repositório atual com a mesma esteira) | 2026-09-28 |
| Fotos do cliente | Entram já na fase inicial, com **botão de envio de imagens no briefing** (formulário), para uso nos posts | 2026-09-28 |
| Fotos de banco | Só bancos gratuitos com licença comercial e sem risco de LGPD | 2026-09-28 |

## Recomendação de Claude para a fase 0 (a detalhar no desenho)

- **Motor no Mac de Lucas, sem IA na nuvem.** Nenhuma chave de IA em servidor: custo zero de API e menos superfície de ataque.
- **App do cliente com login real e isolamento no banco.** Candidato: Supabase no plano gratuito (login por link no e-mail,
  regras de acesso por linha, armazenamento privado com links que expiram, aprovação gravada no banco).
  Limites do gratuito a considerar no desenho: 1 GB de arquivos, 5 GB de tráfego por mês e pausa do projeto após
  7 dias sem uso. Alternativa gratuita a comparar: Cloudflare (Pages + Access com código por e-mail, até 50 usuários;
  R2 com 10 GB e tráfego de saída sem custo; D1; Workers) — mais espaço e sem pausa, mais peças para montar.
- **Retenção curta de mídia na nuvem**, que resolve ao mesmo tempo o limite gratuito e a LGPD: fotos e vídeos ficam no
  app só enquanto o mês está em aprovação; depois de baixados, saem da nuvem. O original fica na pasta do cliente.
- **LGPD nas fotos do cliente:** no envio, o cliente declara que tem autorização das pessoas que aparecem; prazo de
  guarda definido; apagar tudo a pedido.
- **Fotos de banco:** Unsplash e Pexels têm licença comercial gratuita, mas **não garantem autorização de imagem das
  pessoas retratadas**. Preferir fotos sem rosto identificável (mãos, objetos, ambientes) e registrar a fonte.
- **Esteira única de publicação (harness):** `publicar <cliente> <mês>` roda todos os portões (legenda, humanizador,
  tamanhos, versão, checklist visual, isolamento por cliente) e grava um relatório; avaliação por cliente
  (aprovação sem edição, rodadas, horas de operação).
- **Visual por kit de marca:** modelos genéricos alimentados por cores, fontes, logo e elementos do cliente; tema neutro
  para quem não tem identidade.

"Harness", no vocabulário da Taqtile (reunião Harness Taqsite, 2026-06-17; pauta de conteúdo, 2026-06-24):
arquitetura em que o agente roda dentro de uma estrutura com validações e avaliação de cada saída antes
de chegar ao humano. Confirmar com Lucas se é esse o sentido.

## O que o piloto provou (outubro/2026, Tropi)

Medição completa em `clientes/tropi/2026-10/retorno.md`.

- 12 posts aprovados (carrossel, estático, foto com modelo, Reels com moldura e capa).
- Textos: aprovados quase sem edição depois que a ficha de voz amadureceu. Os ajustes de Lucas viraram
  regras na ficha (`voz.md`: Proibidas, tom por contexto) e o humanizador passou a pegá-los.
- Visual: foi onde houve mais retrabalho (identidade misturada, recorte de capa, texto literal, elemento
  cobrindo rosto). As regras estão em `clientes/tropi/visual.md` e `modelos-foto/README.md`.
- Página de aprovação: Lucas aprovou, editou e baixou pelo celular sem ajuda. Download no iPhone precisou
  do menu de compartilhar (Web Share), porque o zip não abria no app do Drive.
- Formulário: cobriu público, personalidade, tom e concorrentes; faltavam linhas da marca e condições
  comerciais (entraram como perguntas opcionais).

## O que já é estrutura reaproveitável

| Peça | Onde | Estado |
|---|---|---|
| Formulário de briefing (17 obrigatórias + 2 opcionais) | `site/formulario/`, `site/assets/perguntas.js` | genérico |
| Moldes de ficha da marca e ficha de voz | `modelos/` | genérico |
| Skills do fluxo: onboarding, pauta, carrossel, post, post com foto, legenda, humano, entrega | `.claude/skills/ig-*` | quase genérico (exemplos citam a Tropi) |
| Verificador de legenda (corte de 125, hashtags, um pedido, NFC) | `ferramentas/legenda.py` | genérico |
| Humanizador (léxico base + Proibidas da ficha de voz) | `ferramentas/humanizar.py` | genérico |
| Renderização HTML → JPG, capa vertical, captura transparente | `ferramentas/renderizar.py` | genérico |
| Moldura de vídeo para Reels | `ferramentas/video.py` | genérico |
| Manifesto com versão por post (invalida aprovação antiga) | `ferramentas/manifesto.py` | genérico |
| Página de aprovação (grade, carrossel, vídeo, status, edição, download, Web Share, exportar JSON) | `site/aprovacao/`, `site/assets/` | genérico |
| Testes (67 Python, 40 JS) | `tests/` | genérico |

## O que ainda é só da Tropi

- Modelos visuais: `clientes/tropi/cafe-goiaba.css` e `clientes/tropi/modelos-foto/gerar.py`, com caminhos
  absolutos (`file:///Users/Lucas/...`) para a marca, que mora fora do repositório.
- Biblioteca de ilustração (`desenho.js`) e elementos: vivem no repositório da marca da Tropi. Outro cliente
  pode não ter identidade pronta.
- Regras visuais escritas à mão por cliente (`visual.md`).

## Lacunas para virar produto (pontos de partida da conversa, não decisões)

1. **Privacidade dos arquivos do cliente.** Hoje tudo é público: imagens, legendas, manifesto e
   `acesso.json` (lista de e-mails) ficam abertos no GitHub Pages. Inaceitável com clientes pagantes.
2. **Login real.** O portão de e-mail só esconde a tela.
3. **Envio de fotos e vídeos pelo celular.** Hoje chegam por conversa com Lucas e pasta Downloads.
4. **Isolamento entre clientes.** Um cliente nunca pode ver arquivo, ficha ou aprovação de outro.
5. **Retorno da aprovação.** Hoje é um JSON baixado e trazido à mão; o estado fica no navegador de quem aprova.
6. **Identidade visual por cliente.** Como montar modelos visuais para um cliente novo sem escrever
   HTML à mão, e o que fazer quando o cliente não tem identidade.
7. **Harness formal.** Juntar as checagens que existem (legenda, humanizador, versão, conferência visual
   manual) numa esteira única com portões, registro de cada execução e avaliação por cliente.
8. **Nome do produto.** Define o repositório e as pastas (casa já decidida: repositório novo e privado; Tropi fica onde está).
9. **Oferta comercial.** Preço, escopo mensal (quantos posts, Reels ou não), quem opera além de Lucas.

## Regras que continuam valendo

- Nunca conectar à conta de Instagram do cliente.
- Nunca inventar @ de parceiro; perguntar.
- Texto passa pelo humanizador e pelo verificador antes de ir para aprovação.
- Nada de foto com licença incerta; registrar a fonte.
- Commits: conta pessoal `lucaslanzoni` no push (ver rotina no README ou na sessão anterior).
