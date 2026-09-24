// Perguntas do formulário de marca. Derivado do formulário Frameworks da Moxie,
// sem áudio e sem a seção de inventário.
export const ARQUETIPOS = [
  { id: 'inocente', descricao: 'A que é simples, otimista e passa confiança' },
  { id: 'explorador', descricao: 'A que busca liberdade, descoberta e o novo' },
  { id: 'sabio', descricao: 'A que sabe muito e ensina' },
  { id: 'heroi', descricao: 'A que supera desafios e inspira a vencer' },
  { id: 'fora_da_lei', descricao: 'A que provoca e quebra regra' },
  { id: 'mago', descricao: 'A que transforma e faz parecer mágico' },
  { id: 'cara_comum', descricao: 'A que é gente como a gente, sem pose' },
  { id: 'amante', descricao: 'A que seduz pelos sentidos, pela beleza e pelo prazer' },
  { id: 'bobo_da_corte', descricao: 'A que diverte e não se leva a sério' },
  { id: 'cuidador', descricao: 'A que cuida, acolhe e protege' },
  { id: 'criador', descricao: 'A que inventa e valoriza o que é feito com cuidado' },
  { id: 'governante', descricao: 'A que lidera, organiza e transmite status' },
];

export const SECOES = [
  {
    id: 'marca',
    titulo: 'A marca',
    intro: 'O básico, do jeito que você explicaria para alguém numa conversa.',
    perguntas: [
      { id: 'marca_frase', texto: 'O que é a marca e o que ela vende, em uma frase?', exemplo: 'Ex: uma loja online de discos de vinil de música brasileira, novos e usados.' },
      { id: 'marca_links', texto: 'Qual é o site e o @ do Instagram?', exemplo: 'Ex: minhaloja.com.br e @minhaloja' },
      { id: 'marca_objetivo', texto: 'O que o Instagram precisa fazer pela marca nos próximos meses?', exemplo: 'Ex: vender mais pelo site, ser lembrada como referência, formar uma comunidade.' },
    ],
  },
  {
    id: 'empatia',
    titulo: 'Quem consome o conteúdo',
    intro: 'Pense numa pessoa real, ou numa mistura de pessoas, que compraria da marca.',
    perguntas: [
      { id: 'empatia_pensa', texto: 'O que essa pessoa pensa e não fala em voz alta?', exemplo: 'Ex: quer ter bom gosto, mas tem medo de parecer que está se esforçando demais.' },
      { id: 'empatia_ve', texto: 'O que ela vê no feed, nos amigos, no que está em alta?', exemplo: 'Ex: amigos mostrando coleção, perfis de curadoria, lançamentos comentados.' },
      { id: 'empatia_influencia', texto: 'Quem influencia o que ela compra?', exemplo: 'Ex: um amigo que entende do assunto, um perfil que ela confia, o vendedor da loja.' },
      { id: 'empatia_fala', texto: 'Como ela fala desse assunto com os outros?', exemplo: 'Ex: comenta a história por trás do produto quando alguém pergunta.' },
      { id: 'empatia_frustra', texto: 'O que frustra essa pessoa hoje quando procura esse tipo de produto?', exemplo: 'Ex: tudo é caro demais ou genérico, ninguém explica o que está vendendo.' },
      { id: 'empatia_ganho', texto: 'O que faria ela sentir "achei a marca certa"?', exemplo: 'Ex: ser atendida por quem conhece e receber algo que ninguém mais tem.' },
      { id: 'empatia_nao_publico', texto: 'Quem não é o público da marca?', exemplo: 'Ex: quem só procura o mais barato, quem não liga para a história do produto.' },
    ],
  },
  {
    id: 'voz',
    titulo: 'Como a marca se comunica',
    intro: 'Não existe resposta certa. É a sua percepção da marca.',
    perguntas: [
      { id: 'voz_arquetipo', tipo: 'arquetipo', texto: 'Qual descrição mais combina com a marca? Escolha até 2.', exemplo: 'Pense em como a marca age, não em como gostaria de parecer.' },
      { id: 'voz_festa', texto: 'Se a marca chegasse numa festa, como agiria nos primeiros 5 minutos?', exemplo: 'Ex: observa antes de falar e solta um comentário que só alguns entendem.' },
      { id: 'voz_defende', texto: 'O que a marca defende mesmo que afaste gente? E o que nunca faria, nem vendendo mais?', exemplo: 'Ex: nunca vai falar de promoção antes de falar do produto.' },
      { id: 'voz_palavras', texto: 'Quais palavras e expressões a marca usa? E quais nunca usaria?', exemplo: 'Ex: usa "garimpo", "edição", "curadoria". Nunca usa "imperdível" ou "aproveite".' },
      { id: 'voz_frases', texto: 'Escreva uma frase que soa como a marca e uma que não soa.', exemplo: 'Ex: soa: "Chegou a edição que faltava na estante." Não soa: "Promoção imperdível, corre!"' },
      { id: 'posic_concorrentes', texto: 'Quais são 2 ou 3 concorrentes? O que cada um faz bem e mal?', exemplo: 'Ex: Loja X tem catálogo grande, mas atendimento frio.' },
      { id: 'posic_diferencial', texto: 'O que a marca faz que os concorrentes não fazem? E qual frase resume a marca?', exemplo: 'Ex: curadoria feita por quem ouve cada disco. "Disco escolhido a dedo."' },
    ],
  },
];
