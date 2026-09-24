import { test } from 'node:test';
import assert from 'node:assert/strict';
import { normalizarEmail, emailValido, clienteDoEmail } from '../../site/assets/acesso-logica.js';

test('normaliza espaços e maiúsculas', () => {
  assert.equal(normalizarEmail('  Lucas@Exemplo.COM '), 'lucas@exemplo.com');
  assert.equal(normalizarEmail(undefined), '');
});

test('valida formato de e-mail', () => {
  assert.equal(emailValido('a@b.co'), true);
  assert.equal(emailValido(' A@B.CO '), true);
  assert.equal(emailValido('sem-arroba.com'), false);
  assert.equal(emailValido('a@b'), false);
});

test('encontra o cliente ignorando caixa e espaços dos dois lados', () => {
  const acesso = { emails: { 'Lucas@Exemplo.com': 'tropi' } };
  assert.equal(clienteDoEmail(acesso, ' lucas@exemplo.COM'), 'tropi');
});

test('e-mail fora da lista devolve null', () => {
  assert.equal(clienteDoEmail({ emails: { 'a@b.co': 'tropi' } }, 'c@d.co'), null);
});

test('acesso sem lista devolve null', () => {
  assert.equal(clienteDoEmail({}, 'a@b.co'), null);
  assert.equal(clienteDoEmail(null, 'a@b.co'), null);
});
