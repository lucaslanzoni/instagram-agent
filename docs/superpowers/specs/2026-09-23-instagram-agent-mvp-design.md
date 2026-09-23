# Instagram Agent — MVP (piloto Tropi Discos)

Data: 2026-09-23
Status: rascunho para revisão de Lucas (v2 — hospedagem no modelo da plataforma Moxie)

---

## 1. Objetivo

Um braço de criação de conteúdo para Instagram, replicável por cliente da consultoria. O cliente preenche um formulário; Claude transforma as respostas em ficha da marca e ficha de tom de voz; a partir delas monta a pauta do mês, produz posts estáticos e carrosséis na identidade visual do cliente e entrega tudo numa página de aprovação com prévia do perfil, edição, status e download.

O MVP roda só com a Tropi Discos (loja de Lucas). Lucas preenche o formulário como dono e avalia a usabilidade da plataforma. Fase de teste: nenhum cliente externo usa o sistema ainda.

## 2. Decisões já tomadas

| Decisão | Motivo |
|---|---|
| Base: estrutura do pacote `Jakeschincariol/instagram-agent-skill` (MIT), recriada em PT-BR | Não conecta ao Instagram, não pede chave, sem custo. Cobre planejamento, escrita e humanizador |
| Nada conecta ao Instagram; quem publica é o humano | Política de segurança: terceiro com acesso ao Instagram só se for plataforma verificada, paga e com análise de segurança |
| Só posts estáticos e carrosséis | Vídeo, Reels, stories, comentários e DMs ficam para depois |
| Formulário só escrito (sem áudio) | Simplicidade |
| Duas fichas por cliente: marca e tom de voz | Moldes: `briefing-moxie.md` e `tom-de-voz.md` da Moxie |
| Hospedagem no modelo da plataforma Moxie: repositório público, GitHub Pages, site estático sem servidor | Fase de teste, custo zero, padrão que Lucas já opera |
| Login só por e-mail, conferido no navegador contra `acesso.json` (portão visual, como na Moxie) | Rodar primeiro; armazenamento seguro de e-mails e dados fica para antes do primeiro cliente externo |
| Respostas e aprovações salvas no navegador e exportadas em arquivo (como a avaliação da Gabriela) | Sem servidor não há onde gravar; o arquivo exportado é o que Claude lê |
| MVP roda na sessão local do Claude Code de Lucas | Agente na nuvem fica para depois |

## 3. Fora do escopo do MVP

- Vídeo, Reels, stories, comentários, respostas, DMs, auditoria de perfil
- Pesquisa de nicho (`/ig-viral`) e calendário de datas do setor automatizado
- Servidor, banco de dados, login com proteção real, código por e-mail
- Upload de logo e materiais pela plataforma (na Tropi, o logo já existe na pasta da marca)
- Agente rodando na nuvem (GitHub Actions)
- Tradução completa das 26 fórmulas de gancho e do léxico de "cara de IA"
- Edição visual livre dos slides (estilo Canva)
- Segundo cliente

## 4. Visão geral do fluxo

```
[1 Formulário]  cliente responde no site -> "Enviar respostas" baixa respostas.json
      |
      v   Lucas coloca o arquivo em clientes/<slug>/; Claude lê + site + material existente
[2 Fichas]      clientes/<slug>/marca.md e voz.md  -> Lucas revisa
      |
      v
[3 Pauta]       clientes/<slug>/<AAAA-MM>/pauta.md  -> Lucas aprova no chat
      |
      v
[4 Produção]    texto -> humanizador do cliente -> HTML no sistema visual -> JPG
      |
      v
[5 Entrega]     manifesto.json + imagens publicados em site/ -> página de aprovação
      |
      v   cliente aprova/edita -> "Enviar aprovação" baixa aprovacao.json
[6 Retorno]     Claude lê o arquivo, reaplica, re-renderiza, registra aprendizado nas fichas
```

## 5. Estrutura do repositório

Repositório público `instagram-agent` (GitHub, conta pessoal `lucaslanzoni`). O site publicado é só a pasta `site/`, via GitHub Actions para GitHub Pages.

```
instagram-agent/
  README.md
  LICENSE                      MIT (do projeto)
  THIRD_PARTY.md               aviso MIT de Jake Schincariol sobre o que foi derivado
  .github/workflows/pages.yml  publica site/ no GitHub Pages
  .claude/skills/
    ig-onboarding/SKILL.md     respostas.json -> fichas
    ig-pauta/SKILL.md          fichas -> pauta do mês
    ig-carrossel/SKILL.md      um post da pauta -> slides + legenda
    ig-post/SKILL.md           um post estático da pauta -> imagem + legenda
    ig-legenda/SKILL.md        regras de legenda (usada pelas duas acima)
    ig-humano/SKILL.md         humanizador com léxico por cliente
    ig-entrega/SKILL.md        manifesto -> site; lê aprovacao.json
  ferramentas/
    legenda.py                 derivado de caption.py (corte de 125 caracteres, checagens)
    humanizar.py               derivado de humanize.py, léxico base PT + léxico do cliente
    renderizar.py              HTML -> JPG via Chrome headless
    manifesto.py               valida e monta manifesto.json
    lexico_base_pt.json        "cara de IA" em PT-BR (lista inicial curta)
  modelos/
    ficha-marca.md
    ficha-voz.md
  site/                        o que vai para o GitHub Pages (HTML/CSS/JS sem framework, sem build)
    index.html                 tela de e-mail
    acesso.json                { "emails": { "email": "slug-do-cliente" } }
    assets/                    estilo.css, acesso.js, formulario.js, aprovacao.js, exportar.js
    formulario/index.html
    aprovacao/index.html
    clientes/tropi/2026-10/    manifesto.json + imagens do mês
  clientes/
    tropi/
      cliente.json             nome, @, site, caminho da pasta de marca
      respostas.json           exportado do formulário
      marca.md
      voz.md
      2026-10/
        pauta.md
        posts/<nn>-<slug>/     slide-1.html ... slide-n.html, legenda.md
        aprovacao.json         exportado da página de aprovação
  tests/
  docs/superpowers/specs/
```

Os ativos de marca da Tropi continuam em `~/Documents/Freelas/tropi-discos/` (casa canônica). `cliente.json` aponta para lá; nada é duplicado.

**Consequência do repositório público, aceita para a fase de teste:** fichas, pauta, respostas e posts ainda não publicados da Tropi ficam visíveis para quem acessar o repositório ou o endereço direto dos arquivos. O portão de e-mail filtra a tela, não protege os arquivos.

## 6. Componentes

### 6.1 Acesso

- `site/index.html`: campo de e-mail e botão Entrar, como na plataforma Moxie.
- `acesso.js` compara o e-mail (minúsculo, sem espaços) com `acesso.json`, guarda e-mail e cliente no navegador e leva para o formulário ou para a aprovação daquele cliente.
- Lucas libera um cliente adicionando o e-mail em `acesso.json` e publicando.

### 6.2 Formulário de entrada

Derivado do formulário da Moxie, sem áudio e sem a seção de inventário. Salva cada resposta no navegador ao digitar, permite fechar e voltar, mostra progresso. Ao final, "Enviar respostas" baixa `respostas.json` (cliente, data e respostas por id).

**Bloco 1 — A marca**
1. O que é a marca e o que ela vende, em uma frase.
2. Site e @ do Instagram.
3. O que o Instagram precisa fazer pela marca nos próximos meses (vender, ser lembrada, formar comunidade).

**Bloco 2 — Quem consome o conteúdo (mapa de empatia)**
4. O que essa pessoa pensa e não fala em voz alta?
5. O que ela vê no feed, nos amigos, no que está em alta?
6. Quem influencia o que ela compra?
7. Como ela fala do assunto com os outros?
8. O que frustra essa pessoa hoje quando procura esse tipo de produto?
9. O que faria ela sentir "achei a marca certa"?
10. Quem não é o público?

**Bloco 3 — Como a marca se comunica**
11. Arquétipo: escolher até 2 entre 12 descrições simples (sem os nomes técnicos).
12. Se a marca chegasse numa festa, como agiria nos primeiros 5 minutos?
13. O que a marca defende mesmo que afaste gente, e o que nunca faria nem vendendo mais?
14. Palavras e expressões que a marca usa, e palavras que nunca usaria.
15. Uma frase que soa como a marca e uma que não soa.
16. Concorrentes: 2 ou 3 marcas, e o que cada uma faz bem e mal.
17. O que a marca faz que as concorrentes não fazem, e a frase que resume a marca.

O upload de logo saiu do MVP (sem servidor não há onde guardar); volta com o backend.

### 6.3 Fichas (skill `ig-onboarding`)

Entrada: `respostas.json`, leitura do site e, quando existir, material de marca do cliente (na Tropi: `CLAUDE.md`, `branding/proposta-identidade.md`, `branding/site-conteudo-textos.md`, `MODELO-CARROSSEL-DISCO.md`).

Saída:
- `marca.md` — molde do `briefing-moxie.md`: identidade, público (inclusive quem não é), produto e oferta, posicionamento, concorrentes, temas de conteúdo, insights.
- `voz.md` — molde do `tom-de-voz.md`: personalidade como pessoa, arquétipo, pilares de voz com "distingue de", voz vs. tom por contexto, o que fala e o que não usa, pares ruim/bom, o que nunca faz, checklist, frase-âncora. Termina com dois blocos lidos por máquina:
  - `proibidas`: palavras e expressões vetadas (pergunta 14 e regras da marca).
  - `exemplos`: pares ruim/bom (pergunta 15 e os escritos pelo agente, marcados como tal).

Regra: o agente não inventa prova (número, prêmio, depoimento). O que faltar vira `{{a preencher}}`.

### 6.4 Pauta do mês (skill `ig-pauta`)

Derivada de `ig-plan`, adaptada de semana para mês e de criador para marca.

- 8 a 12 posts, mistura de estático e carrossel.
- Fontes: fichas, histórico dos meses anteriores e, na Tropi, o catálogo (exportação da loja em `referencias/` e produtos novos).
- Cada linha: número, tema (pilar), formato, fórmula de gancho, ideia específica (um fato, não um assunto), data sugerida.
- Regras herdadas: não repetir formato em sequência, no máximo 1 a 2 posts de oferta, não repetir tema das últimas duas semanas.
- Aprovação da pauta no chat antes da produção.

### 6.5 Produção (skills `ig-carrossel`, `ig-post`, `ig-legenda`, `ig-humano`)

- `ig-carrossel`: capa (até 6 palavras), um ponto por slide (até 25 palavras), recapitulação, CTA único. 4 a 10 slides.
- `ig-post`: imagem única com título e apoio curto.
- `ig-legenda`: gancho nos primeiros 125 caracteres, uma chamada para ação, 3 a 5 hashtags. Validada por `legenda.py`.
- `ig-humano`: roda `humanizar.py` com o léxico base PT + `proibidas` do cliente; o que não dá para corrigir por regra volta como alerta para reescrita.
- Visual: modelos HTML no sistema visual de cada cliente. Na Tropi, reaproveita o sistema da `carrossel-disco` (`base-retrato.css`, 1080x1350). `renderizar.py` gera JPG (qualidade ~85) com Chrome headless.
- Conferência visual: Claude abre cada imagem gerada e verifica corte de texto, fonte e alinhamento antes da entrega.

### 6.6 Página de aprovação (skill `ig-entrega`)

`site/aprovacao/` lê `site/clientes/<slug>/<mês>/manifesto.json` do cliente logado.

Layout (referência: print da Nunes Digital):
- Barra lateral: consultoria, cliente, mês, @, total de posts; lista numerada com miniatura, tema, ícone de formato e status.
- Grade de prévia do perfil em 3 colunas, retrato, com número e ícone de formato.
- Post aberto: carrossel que passa para o lado, legenda completa com botão copiar, legenda editável, status (aprovado / revisar com comentário / descartado).
- Download: por post (imagens + legenda.txt) e do mês inteiro, em .zip gerado no navegador (JSZip via cdnjs).
- Status e edições ficam salvos no navegador; "Enviar aprovação" baixa `aprovacao.json`.
- Funciona no celular.

`manifesto.json`:
```json
{
  "cliente": "tropi", "mes": "2026-10", "arroba": "@tropi_discos",
  "posts": [
    {
      "id": "03-afim-ze-ibarra", "numero": 3, "tema": "Lançamento",
      "formato": "carrossel", "data_sugerida": "2026-10-07",
      "imagens": ["03-afim-ze-ibarra/1.jpg", "03-afim-ze-ibarra/2.jpg"],
      "legenda": "texto completo", "alt": "descrição da capa"
    }
  ]
}
```

`aprovacao.json`:
```json
{
  "cliente": "tropi", "mes": "2026-10", "email": "...", "gerado_em": "ISO",
  "posts": { "03-afim-ze-ibarra": { "status": "revisar", "comentario": "...", "legenda_editada": "..." } }
}
```

### 6.7 Retorno

Lucas coloca `aprovacao.json` em `clientes/<slug>/<mês>/`; `ig-entrega` lê:
- `revisar`: aplica o comentário, re-renderiza e republica.
- `legenda_editada`: passa a valer como legenda final.
- Padrões de recusa ou edição viram proposta de ajuste em `voz.md`, que Lucas aprova.

## 7. Limites e cuidados técnicos

- GitHub Pages: site até 1 GB e arquivos até 100 MB; um mês com ~60 JPGs de ~350 KB ≈ 21 MB.
- Estado no navegador se perde se o cliente limpar os dados ou trocar de aparelho antes de enviar; a página avisa isso e oferece "Enviar" a qualquer momento.
- Nada vai para modelo ou serviço de terceiros além do GitHub.
- Push no repositório: `gh auth switch --user lucaslanzoni` antes, voltar para `lucaslanzoni-taqtile` depois (padrão já usado na Moxie).
- Licença: arquivos derivados do pacote do Jake mantêm o aviso MIT em `THIRD_PARTY.md`.

## 8. Testes

- Python (pytest):
  - `legenda.py`: conta palavras com acento corretamente ("Ninguém" = 1 palavra); corte de 125 caracteres; limite de 5 hashtags; uma única chamada para ação.
  - `humanizar.py`: remove caracteres invisíveis; aplica léxico base; aplica `proibidas` do cliente; não altera texto sem ocorrências.
  - `manifesto.py`: rejeita manifesto sem imagem, com formato inválido ou com imagem inexistente.
  - `renderizar.py`: teste de fumaça gera JPG 1080x1350 de um HTML mínimo.
- JavaScript (`node --test`, como na Moxie): conferência de e-mail, montagem de `respostas.json` e `aprovacao.json`.
- Verificação manual: Claude abre as imagens geradas e a página num navegador; Lucas testa formulário e aprovação no celular.

## 9. Critérios de sucesso do MVP

1. Lucas publicaria pelo menos 7 de 10 posts com pouca ou nenhuma edição.
2. As fichas geradas pelo formulário cobrem o que já está documentado da marca Tropi.
3. O mês inteiro (pauta, produção, página) sai em uma sessão de trabalho.
4. Lucas consegue entrar, responder, aprovar, editar e baixar pelo celular sem ajuda.

## 10. Plano de melhoria (depois do MVP)

| Fase | Entrega |
|---|---|
| 2 | Tradução completa das ferramentas: 26 fórmulas de gancho e léxico de "cara de IA" em PT-BR |
| 3 | Backend antes do primeiro cliente externo: repositório privado, servidor (Cloudflare Pages + D1 + R2), e-mails e respostas guardados no banco, upload de logo, aprovação gravada sem exportar arquivo, depois código por e-mail |
| 4 | Segundo cliente (Moxie) e modelo de pasta de cliente |
| 5 | Pesquisa de nicho (`ig-viral`) e calendário de datas do setor |
| 6 | Agente na nuvem (GitHub Actions com a assinatura do Claude, agenda mensal) |
| 7 | Stories, roteiro de Reels, vídeo, comentários e DMs |
| 8 | Teste comparativo com modelo gratuito (OpenCode + OpenRouter) |
