# Instagram Agent — MVP (piloto Tropi Discos)

Data: 2026-09-23
Status: rascunho para revisão de Lucas

---

## 1. Objetivo

Um braço de criação de conteúdo para Instagram, replicável por cliente da consultoria. O cliente preenche um formulário; Claude transforma as respostas em ficha da marca e ficha de tom de voz; a partir delas monta a pauta do mês, produz posts estáticos e carrosséis na identidade visual do cliente e entrega tudo numa página de aprovação com prévia do perfil, edição, status e download.

O MVP roda só com a Tropi Discos (loja de Lucas). Lucas preenche o formulário como dono e avalia a usabilidade da plataforma.

## 2. Decisões já tomadas

| Decisão | Motivo |
|---|---|
| Base: estrutura do pacote `Jakeschincariol/instagram-agent-skill` (MIT), recriada em PT-BR | Não conecta ao Instagram, não pede chave, sem custo. Cobre planejamento, escrita e humanizador |
| Nada conecta ao Instagram; quem publica é o humano | Política de segurança: terceiro com acesso ao Instagram só se for plataforma verificada, paga e com análise de segurança |
| Só posts estáticos e carrosséis | Vídeo, Reels, stories, comentários e DMs ficam para depois |
| Formulário só escrito (sem áudio) | Simplicidade |
| Cliente sobe só o logo; briefing e site cobrem o resto | Simplificar o MVP |
| Duas fichas por cliente: marca e tom de voz | Moldes: `briefing-moxie.md` e `tom-de-voz.md` da Moxie |
| Formulário e página de aprovação publicados como Artifacts do Claude | Já provado no formulário da Moxie: banco de respostas, upload e usuário, sem hospedagem e sem custo. Hospedagem própria fica para depois |
| MVP roda na sessão local do Claude Code de Lucas | Agente na nuvem fica para depois |

## 3. Fora do escopo do MVP

- Vídeo, Reels, stories, comentários, respostas, DMs, auditoria de perfil
- Pesquisa de nicho (`/ig-viral`) e calendário de datas do setor automatizado
- Hospedagem própria, login próprio, upload de materiais além do logo
- Agente rodando na nuvem (GitHub Actions)
- Tradução completa das 26 fórmulas de gancho e do léxico de "cara de IA"
- Edição visual livre dos slides (estilo Canva)
- Segundo cliente

## 4. Visão geral do fluxo

```
[1 Formulário]  cliente responde (Artifact, banco de respostas + logo)
      |
      v   Claude lê as respostas (ArtifactData) + site + material existente
[2 Fichas]      clientes/<slug>/marca.md e voz.md  -> Lucas revisa
      |
      v
[3 Pauta]       clientes/<slug>/<AAAA-MM>/pauta.md  -> Lucas aprova no chat
      |
      v
[4 Produção]    texto -> humanizador do cliente -> HTML no sistema visual -> PNG/JPG
      |
      v
[5 Entrega]     manifesto.json -> página de aprovação (Artifact)
      |
      v   Claude lê status, comentários e legendas editadas (ArtifactData)
[6 Retorno]     reaplica, re-renderiza, registra aprendizado nas fichas
```

## 5. Estrutura do repositório

```
instagram-agent/
  README.md
  LICENSE                      MIT (do projeto)
  THIRD_PARTY.md               aviso MIT de Jake Schincariol sobre o que foi derivado
  .claude/skills/
    ig-onboarding/SKILL.md     formulário -> fichas
    ig-pauta/SKILL.md          fichas -> pauta do mês
    ig-carrossel/SKILL.md      um post da pauta -> slides + legenda
    ig-post/SKILL.md           um post estático da pauta -> imagem + legenda
    ig-legenda/SKILL.md        regras de legenda (usada pelas duas acima)
    ig-humano/SKILL.md         humanizador com léxico por cliente
    ig-entrega/SKILL.md        manifesto -> página de aprovação; lê o retorno
  ferramentas/
    legenda.py                 derivado de caption.py (corte de 125 caracteres, checagens)
    humanizar.py               derivado de humanize.py, léxico base PT + léxico do cliente
    renderizar.py              HTML -> imagem via Chrome headless
    manifesto.py               valida e monta manifesto.json
    lexico_base_pt.json        "cara de IA" em PT-BR (lista inicial curta)
  modelos/
    formulario/                código do Artifact do formulário (genérico)
    aprovacao/                 código do Artifact de aprovação (genérico)
    ficha-marca.md
    ficha-voz.md
  clientes/
    tropi/
      cliente.json             nome, @, site, pasta de marca, URLs dos Artifacts
      marca.md
      voz.md
      visual/                  referência ao sistema visual (não copia a pasta da Tropi)
      2026-10/
        pauta.md
        posts/<nn>-<slug>/     slide-1.html ... slide-n.html, imagens, legenda.md
        manifesto.json
  tests/
  docs/superpowers/specs/
```

Os ativos de marca da Tropi continuam em `~/Documents/Freelas/tropi-discos/` (casa canônica). `clientes/tropi/cliente.json` aponta para lá; nada é duplicado.

## 6. Componentes

### 6.1 Formulário de entrada (Artifact)

Genérico por cliente: um Artifact publicado por cliente, com URL e banco próprios. Derivado do formulário da Moxie, sem o áudio e sem a seção de inventário. Salva cada resposta ao digitar, permite voltar depois, mostra progresso.

**Bloco 1 — A marca**
1. O que é a marca e o que ela vende, em uma frase.
2. Site e @ do Instagram.
3. O que o Instagram precisa fazer pela marca nos próximos meses (vender, ser lembrada, formar comunidade).
4. Upload do logo.

**Bloco 2 — Quem consome o conteúdo (mapa de empatia)**
5. O que essa pessoa pensa e não fala em voz alta?
6. O que ela vê no feed, nos amigos, no que está em alta?
7. Quem influencia o que ela compra?
8. Como ela fala do assunto com os outros?
9. O que frustra essa pessoa hoje quando procura esse tipo de produto?
10. O que faria ela sentir "achei a marca certa"?
11. Quem não é o público?

**Bloco 3 — Como a marca se comunica**
12. Arquétipo: escolher até 2 entre 12 descrições simples (sem os nomes técnicos).
13. Se a marca chegasse numa festa, como agiria nos primeiros 5 minutos?
14. O que a marca defende mesmo que afaste gente, e o que nunca faria nem vendendo mais?
15. Palavras e expressões que a marca usa, e palavras que nunca usaria.
16. Uma frase que soa como a marca e uma que não soa.
17. Concorrentes: 2 ou 3 marcas, e o que cada uma faz bem e mal.
18. O que a marca faz que as concorrentes não fazem, e a frase que resume a marca.

Banco: coleção `respostas`, um documento por pergunta (`{pergunta, texto, atualizado_em}`); a 12 guarda a lista de arquétipos escolhidos; o logo vai para o armazenamento de arquivos do Artifact e o id fica em `respostas/logo`.

### 6.2 Fichas (skill `ig-onboarding`)

Entrada: respostas do formulário, leitura do site e, quando existir, material de marca do cliente (na Tropi: `CLAUDE.md`, `branding/proposta-identidade.md`, `branding/site-conteudo-textos.md`, `MODELO-CARROSSEL-DISCO.md`).

Saída:
- `marca.md` — molde do `briefing-moxie.md`: identidade, público (inclusive quem não é), produto e oferta, posicionamento, concorrentes, temas de conteúdo, insights.
- `voz.md` — molde do `tom-de-voz.md`: personalidade como pessoa, arquétipo, pilares de voz com "distingue de", voz vs. tom por contexto, o que fala e o que não usa, pares ruim/bom, o que nunca faz, checklist, frase-âncora. Termina com dois blocos lidos por máquina:
  - `proibidas`: palavras e expressões vetadas (vem da pergunta 15 e das regras da marca).
  - `exemplos`: pares ruim/bom (pergunta 16 e os escritos pelo agente, marcados como tal).

Regra: o agente não inventa prova (número, prêmio, depoimento). O que faltar vira `{{a preencher}}`.

### 6.3 Pauta do mês (skill `ig-pauta`)

Derivada de `ig-plan`, adaptada de semana para mês e de criador para marca.

- 8 a 12 posts, mistura de estático e carrossel.
- Fontes: fichas, histórico dos meses anteriores e, na Tropi, o catálogo (exportação da loja em `referencias/` e produtos novos).
- Cada linha: número, tema (pilar), formato, fórmula de gancho, ideia específica (um fato, não um assunto), data sugerida.
- Regras herdadas: não repetir formato em sequência, no máximo 1 a 2 posts de oferta, não repetir tema das últimas duas semanas.
- Aprovação da pauta no chat antes da produção.

### 6.4 Produção (skills `ig-carrossel`, `ig-post`, `ig-legenda`, `ig-humano`)

- `ig-carrossel`: capa (até 6 palavras), um ponto por slide (até 25 palavras), recapitulação, CTA único. 4 a 10 slides.
- `ig-post`: imagem única com título e apoio curto.
- `ig-legenda`: gancho nos primeiros 125 caracteres, uma chamada para ação, 3 a 5 hashtags. Validada por `legenda.py`.
- `ig-humano`: roda `humanizar.py` com o léxico base PT + `proibidas` do cliente; o que não dá para corrigir por regra volta como alerta para reescrita.
- Visual: cada cliente tem modelos HTML no seu sistema visual. Na Tropi, reaproveita o sistema da `carrossel-disco` (`base-retrato.css`, 1080x1350). `renderizar.py` gera as imagens com Chrome headless e exporta JPG (qualidade ~85) para caber nos limites do Artifact.
- Conferência visual: Claude abre cada imagem gerada e verifica corte de texto, fonte e alinhamento antes da entrega.

### 6.5 Página de aprovação (skill `ig-entrega`, Artifact)

Um Artifact por cliente e mês. Lê `manifesto.json` publicado junto com as imagens.

Layout (referência: print da Nunes Digital):
- Barra lateral: consultoria, cliente, mês, @, total de posts; lista numerada com miniatura, tema, ícone de formato e status.
- Grade de prévia do perfil em 3 colunas, retrato, com número e ícone de formato.
- Post aberto: carrossel que passa para o lado, legenda completa com botão copiar, legenda editável, status (aprovado / revisar com comentário / descartado).
- Download: por post (imagens + legenda.txt) e do mês inteiro, em .zip gerado no navegador (JSZip via cdnjs).
- Funciona no celular.

Banco: coleção `posts`, um documento por post (`{status, comentario, legenda_editada, atualizado_em, por}`).

`manifesto.json`:
```json
{
  "cliente": "tropi", "mes": "2026-10", "arroba": "@tropi_discos",
  "posts": [
    {
      "id": "03-afim-ze-ibarra", "numero": 3, "tema": "Lançamento",
      "formato": "carrossel", "data_sugerida": "2026-10-07",
      "imagens": ["posts/03-afim-ze-ibarra/1.jpg", "..."],
      "legenda": "texto completo", "alt": "descrição da capa"
    }
  ]
}
```

### 6.6 Retorno

`ig-entrega` lê a coleção `posts` via ArtifactData:
- `revisar`: aplica o comentário, re-renderiza e republica a mesma URL.
- `legenda_editada`: passa a valer como legenda final.
- Padrões de recusa ou edição (ex.: palavra trocada sempre) viram proposta de ajuste em `voz.md`, que Lucas aprova.

## 7. Limites e cuidados técnicos

- Artifact: até 255 arquivos e 64 MB por versão; 15 MB por imagem. 10 posts x ~6 slides x ~350 KB em JPG ≈ 21 MB.
- Compartilhamento: a página precisa estar em "qualquer pessoa com o link". Verificar no MVP se quem não tem conta no Claude consegue gravar status e edição (o formulário da Moxie mostra aviso de "sem permissão de edição" em alguns casos). Teste: abrir o link em janela anônima.
- Dados do cliente ficam no repositório local de Lucas e nos Artifacts privados dele. Nada vai para modelo ou serviço de terceiros.
- Licença: arquivos derivados do pacote do Jake mantêm o aviso MIT em `THIRD_PARTY.md`.

## 8. Testes

- `tests/` com pytest para as ferramentas:
  - `legenda.py`: conta palavras com acento corretamente ("Ninguém" = 1 palavra); corte de 125 caracteres; limite de 5 hashtags; uma única chamada para ação.
  - `humanizar.py`: remove caracteres invisíveis; aplica léxico base; aplica `proibidas` do cliente; não altera texto sem ocorrências.
  - `manifesto.py`: rejeita manifesto sem imagem, com formato inválido ou com imagem inexistente.
  - `renderizar.py`: teste de fumaça gera uma imagem 1080x1350 de um HTML mínimo.
- Verificação manual: Claude abre as imagens geradas; Lucas testa formulário e página no celular e em janela anônima.

## 9. Critérios de sucesso do MVP

1. Lucas publicaria pelo menos 7 de 10 posts com pouca ou nenhuma edição.
2. As fichas geradas pelo formulário cobrem o que já está documentado da marca Tropi.
3. O mês inteiro (pauta, produção, página) sai em uma sessão de trabalho.
4. Formulário e página funcionam no celular e em janela anônima; Lucas consegue aprovar, editar e baixar sem ajuda.

## 10. Plano de melhoria (depois do MVP)

| Fase | Entrega |
|---|---|
| 2 | Tradução completa das ferramentas: 26 fórmulas de gancho e léxico de "cara de IA" em PT-BR |
| 3 | Segundo cliente (Moxie) e modelo de pasta de cliente |
| 4 | Pesquisa de nicho (`ig-viral`) e calendário de datas do setor |
| 5 | Agente na nuvem (GitHub Actions com a assinatura do Claude, agenda mensal) |
| 6 | Hospedagem própria com login por cliente e upload de materiais extras |
| 7 | Stories, roteiro de Reels, vídeo, comentários e DMs |
| 8 | Teste comparativo com modelo gratuito (OpenCode + OpenRouter) |
