import { test } from 'node:test';
import assert from 'node:assert/strict';
import { criarArmazenamento } from '../../site/assets/armazenamento.js';

function fakeStorage() {
  const m = new Map();
  return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)), removeItem: (k) => m.delete(k) };
}

test('grava e lê pelo backend', () => {
  const fake = fakeStorage();
  criarArmazenamento(fake).gravar('k', { x: 1 });
  assert.deepEqual(criarArmazenamento(fake).ler('k'), { x: 1 });
});

test('backend que lança erro cai para memória sem quebrar', () => {
  const quebrado = {
    getItem() { throw new Error('bloqueado'); },
    setItem() { throw new Error('bloqueado'); },
    removeItem() { throw new Error('bloqueado'); },
  };
  const a = criarArmazenamento(quebrado);
  a.gravar('k', 'v');
  assert.equal(a.ler('k'), 'v');
  assert.equal(a.persistente(), false);
});

test('sem backend funciona em memória', () => {
  const a = criarArmazenamento(null);
  a.gravar('k', [1, 2]);
  assert.deepEqual(a.ler('k'), [1, 2]);
  assert.equal(a.persistente(), false);
});

test('valor corrompido volta null e continua persistente', () => {
  const fake = fakeStorage();
  fake.setItem('k', '{quebrado');
  const a = criarArmazenamento(fake);
  assert.equal(a.ler('k'), null);
  assert.equal(a.persistente(), true);
});

test('remover apaga', () => {
  const a = criarArmazenamento(fakeStorage());
  a.gravar('k', 1);
  a.remover('k');
  assert.equal(a.ler('k'), null);
});
