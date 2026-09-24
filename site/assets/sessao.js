import { armazenamentoDoNavegador } from './armazenamento.js';

const CHAVE = 'ia_sessao';
export const armazenamento = armazenamentoDoNavegador();

export function lerSessao() {
  const s = armazenamento.ler(CHAVE);
  return s && s.email && s.cliente ? s : null;
}

export function salvarSessao(sessao) {
  armazenamento.gravar(CHAVE, sessao);
}

export function limparSessao() {
  armazenamento.remover(CHAVE);
}

export function exigirSessao(raiz = '../') {
  const s = lerSessao();
  if (!s) {
    location.href = raiz;
    return null;
  }
  return s;
}
