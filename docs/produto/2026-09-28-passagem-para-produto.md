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
8. **Onde o produto mora.** Repositório novo, casa canônica (`~/Code/freelas/<nome>`), repositório privado.
   A Tropi migra para ele ou fica como está?
9. **Oferta comercial.** Preço, escopo mensal (quantos posts, Reels ou não), quem opera além de Lucas.

## Regras que continuam valendo

- Nunca conectar à conta de Instagram do cliente.
- Nunca inventar @ de parceiro; perguntar.
- Texto passa pelo humanizador e pelo verificador antes de ir para aprovação.
- Nada de foto com licença incerta; registrar a fonte.
- Commits: conta pessoal `lucaslanzoni` no push (ver rotina no README ou na sessão anterior).
