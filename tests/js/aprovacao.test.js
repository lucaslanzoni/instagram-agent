import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  validarManifesto, escolherMes, definirStatus, definirComentario, editarLegenda,
  legendaFinal, limparEstado, resumo, montarAprovacao, arquivosDoPost,
} from '../../site/assets/aprovacao-logica.js';

const posts = [
  { id: '01-a', numero: 1, formato: 'carrossel', imagens: ['01-a/1.jpg', '01-a/2.jpg'], legenda: 'Legenda A' },
  { id: '02-b', numero: 2, formato: 'estatico', imagens: ['02-b/1.jpg'], legenda: 'Legenda B' },
];

test('manifesto válido não tem erros', () => {
  assert.deepEqual(validarManifesto({ cliente: 'demo', mes: '2026-01', posts }), []);
});

test('manifesto com id repetido e post sem imagem', () => {
  const erros = validarManifesto({ cliente: 'demo', mes: '2026-01', posts: [posts[0], { ...posts[0] }, { id: '03-c', formato: 'estatico', imagens: [] }] });
  assert.ok(erros.some((e) => e.includes('id repetido')));
  assert.ok(erros.some((e) => e.includes('03-c: sem imagens')));
});

test('manifesto ausente', () => {
  assert.deepEqual(validarManifesto(null), ['manifesto ausente']);
});

test('escolherMes usa o pedido se existir, senão o mais recente, senão null', () => {
  const indice = { meses: ['2026-09', '2026-11', '2026-10'] };
  assert.equal(escolherMes(indice, '2026-10'), '2026-10');
  assert.equal(escolherMes(indice, '2030-01'), '2026-11');
  assert.equal(escolherMes(indice, null), '2026-11');
  assert.equal(escolherMes({ meses: [] }, '2026-10'), null);
  assert.equal(escolherMes(null, null), null);
});

test('definirStatus marca, troca e desmarca clicando de novo', () => {
  let e = definirStatus({}, '01-a', 'aprovado');
  assert.deepEqual(e, { '01-a': { status: 'aprovado' } });
  e = definirStatus(e, '01-a', 'revisar');
  assert.equal(e['01-a'].status, 'revisar');
  e = definirStatus(e, '01-a', 'revisar');
  assert.deepEqual(e, {});
});

test('status inválido lança erro', () => {
  assert.throws(() => definirStatus({}, '01-a', 'talvez'), /status inválido/);
});

test('comentário vazio some; legenda igual à original some', () => {
  let e = definirComentario({}, '01-a', '  trocar a capa ');
  assert.equal(e['01-a'].comentario, 'trocar a capa');
  e = definirComentario(e, '01-a', '   ');
  assert.deepEqual(e, {});
  e = editarLegenda({}, '01-a', 'Nova', 'Legenda A');
  assert.equal(legendaFinal(posts[0], e), 'Nova');
  e = editarLegenda(e, '01-a', 'Legenda A', 'Legenda A');
  assert.deepEqual(e, {});
  assert.equal(legendaFinal(posts[0], e), 'Legenda A');
});

test('legenda editada para vazio continua valendo como edição', () => {
  const e = editarLegenda({}, '01-a', '', 'Legenda A');
  assert.equal(legendaFinal(posts[0], e), '');
});

test('limparEstado descarta posts que não estão mais no manifesto', () => {
  const estado = { '01-a': { status: 'aprovado' }, '99-velho': { status: 'revisar' } };
  assert.deepEqual(limparEstado(estado, posts), { '01-a': { status: 'aprovado' } });
});

test('resumo conta pendentes', () => {
  assert.deepEqual(resumo({ '01-a': { status: 'revisar' } }, posts), { aprovado: 0, revisar: 1, descartado: 0, pendente: 1 });
});

test('montarAprovacao exporta só posts atuais e com data', () => {
  const dados = montarAprovacao({
    cliente: 'demo', mes: '2026-01', email: 'a@b.co',
    estado: { '02-b': { status: 'aprovado' }, '99-velho': { status: 'revisar' } },
    posts, agora: new Date('2026-01-15T10:00:00Z'),
  });
  assert.deepEqual(dados, {
    cliente: 'demo', mes: '2026-01', email: 'a@b.co', gerado_em: '2026-01-15T10:00:00.000Z',
    resumo: { aprovado: 1, revisar: 0, descartado: 0, pendente: 1 },
    posts: { '02-b': { status: 'aprovado' } },
  });
});

test('arquivosDoPost nomeia imagens e legenda final', () => {
  const arq = arquivosDoPost(posts[0], { '01-a': { legenda_editada: 'Editada' } });
  assert.deepEqual(arq.imagens, [
    { src: '01-a/1.jpg', nome: '01-a/1.jpg' },
    { src: '01-a/2.jpg', nome: '01-a/2.jpg' },
  ]);
  assert.deepEqual(arq.legenda, { nome: '01-a/legenda.txt', texto: 'Editada' });
});
