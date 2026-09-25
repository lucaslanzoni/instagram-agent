import { test } from 'node:test';
import assert from 'node:assert/strict';
import { podeCompartilhar, compartilharArquivos } from '../../site/assets/baixar.js';

const arquivos = [new File(['x'], '01-a-1.jpg', { type: 'image/jpeg' })];

test('sem navigator ou sem canShare não compartilha', () => {
  assert.equal(podeCompartilhar(arquivos, undefined), false);
  assert.equal(podeCompartilhar(arquivos, {}), false);
  assert.equal(podeCompartilhar(arquivos, { canShare: () => true }), false);
});

test('canShare falso para arquivos não compartilha', () => {
  assert.equal(podeCompartilhar(arquivos, { canShare: () => false, share: async () => {} }), false);
});

test('canShare verdadeiro compartilha', () => {
  let recebido;
  const nav = { canShare: (d) => { recebido = d; return true; }, share: async () => {} };
  assert.equal(podeCompartilhar(arquivos, nav), true);
  assert.deepEqual(recebido, { files: arquivos });
});

test('lista vazia não compartilha', () => {
  assert.equal(podeCompartilhar([], { canShare: () => true, share: async () => {} }), false);
});

test('compartilharArquivos passa arquivos e título', async () => {
  let recebido;
  const nav = { share: async (d) => { recebido = d; } };
  assert.equal(await compartilharArquivos(arquivos, 'Post 01', nav), 'compartilhado');
  assert.deepEqual(recebido, { files: arquivos, title: 'Post 01' });
});

test('cancelar o menu não é erro', async () => {
  const nav = { share: async () => { const e = new Error('cancelado'); e.name = 'AbortError'; throw e; } };
  assert.equal(await compartilharArquivos(arquivos, 'Post 01', nav), 'cancelado');
});

test('outros erros sobem', async () => {
  const nav = { share: async () => { const e = new Error('sem gesto'); e.name = 'NotAllowedError'; throw e; } };
  await assert.rejects(compartilharArquivos(arquivos, 'Post 01', nav), /sem gesto/);
});
