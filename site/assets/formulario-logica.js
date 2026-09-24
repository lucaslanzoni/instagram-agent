export function totalPerguntas(secoes) {
  return secoes.reduce((n, s) => n + s.perguntas.length, 0);
}

function preenchida(valor) {
  if (Array.isArray(valor)) return valor.length > 0;
  return typeof valor === 'string' && valor.trim().length > 0;
}

export function contarRespondidas(secoes, respostas) {
  let n = 0;
  for (const secao of secoes) for (const p of secao.perguntas) if (preenchida(respostas?.[p.id])) n++;
  return n;
}

export function alternarArquetipo(lista, id, max = 2) {
  const atual = Array.isArray(lista) ? lista : [];
  if (atual.includes(id)) return atual.filter((x) => x !== id);
  if (atual.length >= max) return atual;
  return [...atual, id];
}

export function montarRespostas({ cliente, email, respostas, agora }) {
  const limpas = {};
  for (const [id, valor] of Object.entries(respostas || {})) {
    if (!preenchida(valor)) continue;
    limpas[id] = Array.isArray(valor) ? [...valor] : valor.trim();
  }
  return { cliente, email, gerado_em: agora.toISOString(), respostas: limpas };
}

export function validarSecoes(secoes, arquetipos) {
  const problemas = [];
  const ids = new Set();
  let arquetiposNoFormulario = 0;
  for (const secao of secoes) {
    if (!secao.titulo || !secao.intro) problemas.push(`seção ${secao.id} sem título ou intro`);
    for (const p of secao.perguntas || []) {
      if (ids.has(p.id)) problemas.push(`id repetido: ${p.id}`);
      ids.add(p.id);
      if (!p.texto || !p.exemplo) problemas.push(`pergunta ${p.id} sem texto ou exemplo`);
      if (p.tipo === 'arquetipo') arquetiposNoFormulario++;
    }
  }
  if (arquetiposNoFormulario !== 1) problemas.push('o formulário precisa de exatamente 1 pergunta de arquétipo');
  const idsArquetipo = new Set(arquetipos.map((a) => a.id));
  if (arquetipos.length !== 12 || idsArquetipo.size !== 12) problemas.push('a lista de arquétipos precisa de 12 ids únicos');
  return problemas;
}
