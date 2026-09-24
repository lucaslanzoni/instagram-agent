export const STATUS = ['aprovado', 'revisar', 'descartado'];
const FORMATOS = ['carrossel', 'estatico'];

export function validarManifesto(m) {
  if (!m || typeof m !== 'object') return ['manifesto ausente'];
  const erros = [];
  for (const campo of ['cliente', 'mes', 'posts']) if (!m[campo]) erros.push(`sem ${campo}`);
  if (m.posts && !Array.isArray(m.posts)) return [...erros, 'posts não é lista'];
  const ids = new Set();
  (m.posts || []).forEach((p, i) => {
    if (!p.id) {
      erros.push(`post ${i + 1} sem id`);
      return;
    }
    if (ids.has(p.id)) erros.push(`id repetido: ${p.id}`);
    ids.add(p.id);
    if (!FORMATOS.includes(p.formato)) erros.push(`${p.id}: formato inválido`);
    if (!Array.isArray(p.imagens) || p.imagens.length === 0) erros.push(`${p.id}: sem imagens`);
  });
  return erros;
}

export function escolherMes(indice, pedido) {
  const meses = [...(indice?.meses || [])].sort();
  if (pedido && meses.includes(pedido)) return pedido;
  return meses.length ? meses[meses.length - 1] : null;
}

function limparEntrada(e) {
  const r = {};
  if (e.status) r.status = e.status;
  if (e.comentario) r.comentario = e.comentario;
  if (typeof e.legenda_editada === 'string') r.legenda_editada = e.legenda_editada;
  return r;
}

function comEntrada(estado, id, mudar) {
  const nova = limparEntrada(mudar({ ...(estado?.[id] || {}) }));
  const resto = { ...(estado || {}) };
  if (Object.keys(nova).length) resto[id] = nova;
  else delete resto[id];
  return resto;
}

export function definirStatus(estado, id, status) {
  if (!STATUS.includes(status)) throw new Error(`status inválido: ${status}`);
  return comEntrada(estado, id, (e) => ({ ...e, status: e.status === status ? undefined : status }));
}

export function definirComentario(estado, id, texto) {
  return comEntrada(estado, id, (e) => ({ ...e, comentario: (texto || '').trim() || undefined }));
}

export function editarLegenda(estado, id, texto, original) {
  return comEntrada(estado, id, (e) => ({ ...e, legenda_editada: texto === original ? undefined : texto }));
}

export function legendaFinal(post, estado) {
  const e = estado?.[post.id];
  return typeof e?.legenda_editada === 'string' ? e.legenda_editada : post.legenda;
}

export function limparEstado(estado, posts) {
  const porId = new Map(posts.map((p) => [p.id, p]));
  return Object.fromEntries(
    Object.entries(estado || {}).filter(([id, entrada]) => {
      const post = porId.get(id);
      if (!post) return false;
      if (post.versao && entrada.versao !== post.versao) return false;
      return true;
    })
  );
}

export function carimbarVersao(estado, posts) {
  const porId = new Map(posts.map((p) => [p.id, p]));
  return Object.fromEntries(
    Object.entries(estado || {}).map(([id, entrada]) => {
      const post = porId.get(id);
      return post?.versao ? [id, { ...entrada, versao: post.versao }] : [id, { ...entrada }];
    })
  );
}

export function resumo(estado, posts) {
  const r = { aprovado: 0, revisar: 0, descartado: 0, pendente: 0 };
  for (const p of posts) {
    const s = estado?.[p.id]?.status;
    if (s) r[s]++;
    else r.pendente++;
  }
  return r;
}

export function montarAprovacao({ cliente, mes, email, estado, posts, agora }) {
  return {
    cliente, mes, email,
    gerado_em: agora.toISOString(),
    resumo: resumo(estado, posts),
    posts: limparEstado(estado, posts),
  };
}

export function arquivosDoPost(post, estado) {
  return {
    imagens: post.imagens.map((src) => ({ src, nome: src })),
    legenda: { nome: `${post.id}/legenda.txt`, texto: legendaFinal(post, estado) },
  };
}
