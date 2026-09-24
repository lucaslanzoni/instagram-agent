import { test } from 'node:test';
import assert from 'node:assert/strict';
import { SECOES, ARQUETIPOS } from '../../site/assets/perguntas.js';
import { totalPerguntas, contarRespondidas, alternarArquetipo, montarRespostas, validarSecoes } from '../../site/assets/formulario-logica.js';

test('o formulário tem 3 seções e 17 perguntas válidas', () => {
  assert.equal(SECOES.length, 3);
  assert.equal(totalPerguntas(SECOES), 17);
  assert.deepEqual(validarSecoes(SECOES, ARQUETIPOS), []);
});

test('validarSecoes acha id repetido e arquétipo ausente', () => {
  const ruins = [{ id: 's', titulo: 'T', intro: 'I', perguntas: [{ id: 'a', texto: 't', exemplo: 'e' }, { id: 'a', texto: 't', exemplo: 'e' }] }];
  const problemas = validarSecoes(ruins, ARQUETIPOS);
  assert.ok(problemas.some((p) => p.includes('repetido')));
  assert.ok(problemas.some((p) => p.includes('arquétipo')));
});

test('contarRespondidas ignora espaços e lista vazia', () => {
  const respostas = { marca_frase: '  ', marca_links: 'site', voz_arquetipo: [] };
  assert.equal(contarRespondidas(SECOES, respostas), 1);
});

test('alternarArquetipo aceita no máximo 2 e desmarca', () => {
  let lista = alternarArquetipo([], 'sabio');
  lista = alternarArquetipo(lista, 'criador');
  assert.deepEqual(alternarArquetipo(lista, 'heroi'), ['sabio', 'criador']);
  assert.deepEqual(alternarArquetipo(lista, 'sabio'), ['criador']);
});

test('montarRespostas limpa vazios, apara texto e registra a data', () => {
  const dados = montarRespostas({
    cliente: 'tropi',
    email: 'a@b.co',
    respostas: { marca_frase: '  Loja de vinil  ', marca_links: '', voz_arquetipo: ['sabio'] },
    agora: new Date('2026-10-01T12:00:00Z'),
  });
  assert.deepEqual(dados, {
    cliente: 'tropi',
    email: 'a@b.co',
    gerado_em: '2026-10-01T12:00:00.000Z',
    respostas: { marca_frase: 'Loja de vinil', voz_arquetipo: ['sabio'] },
  });
});
