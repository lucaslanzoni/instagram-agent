import { SECOES, ARQUETIPOS } from './perguntas.js';
import { contarRespondidas, montarRespostas, alternarArquetipo, totalPerguntas } from './formulario-logica.js';
import { exigirSessao, armazenamento } from './sessao.js';
import { baixarJSON } from './baixar.js';

const $ = (id) => document.getElementById(id);

function el(tag, texto, classe) {
  const e = document.createElement(tag);
  if (texto) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}

function iniciar({ email, cliente }) {
  const chave = `ia_form_${cliente}`;
  let respostas = armazenamento.ler(chave) || {};
  const campos = new Map();

  const atualizarProgresso = () => {
    $('progresso').textContent = `${contarRespondidas(SECOES, respostas)} de ${totalPerguntas(SECOES)} respondidas`;
  };
  const salvar = () => {
    armazenamento.gravar(chave, respostas);
    atualizarProgresso();
  };

  function campoTexto(p) {
    const caixa = el('section', null, 'pergunta');
    const area = document.createElement('textarea');
    area.value = typeof respostas[p.id] === 'string' ? respostas[p.id] : '';
    area.setAttribute('aria-label', p.texto);
    let espera;
    area.addEventListener('input', () => {
      clearTimeout(espera);
      espera = setTimeout(() => {
        respostas = { ...respostas, [p.id]: area.value };
        salvar();
      }, 400);
    });
    campos.set(p.id, area);
    caixa.append(el('p', p.texto, 'texto'), el('p', p.exemplo, 'exemplo'), area);
    return caixa;
  }

  function campoArquetipo(p) {
    const caixa = el('section', null, 'pergunta');
    const chips = el('div', null, 'chips');
    const aviso = el('p', '', 'exemplo');
    const desenhar = () => {
      const escolhidos = respostas[p.id] || [];
      for (const botao of chips.children) botao.setAttribute('aria-pressed', String(escolhidos.includes(botao.dataset.id)));
    };
    for (const a of ARQUETIPOS) {
      const botao = el('button', a.descricao, 'chip');
      botao.type = 'button';
      botao.dataset.id = a.id;
      botao.addEventListener('click', () => {
        const antes = respostas[p.id] || [];
        const depois = alternarArquetipo(antes, a.id);
        aviso.textContent = depois === antes ? 'Escolha no máximo 2. Desmarque uma para trocar.' : '';
        respostas = { ...respostas, [p.id]: depois };
        salvar();
        desenhar();
      });
      chips.append(botao);
    }
    desenhar();
    caixa.append(el('p', p.texto, 'texto'), el('p', p.exemplo, 'exemplo'), chips, aviso);
    return caixa;
  }

  const raiz = $('secoes');
  for (const secao of SECOES) {
    raiz.append(el('h2', secao.titulo, 'secao-titulo'), el('p', secao.intro, 'intro'));
    for (const p of secao.perguntas) raiz.append(p.tipo === 'arquetipo' ? campoArquetipo(p) : campoTexto(p));
  }

  $('enviar').addEventListener('click', () => {
    for (const [id, area] of campos) respostas = { ...respostas, [id]: area.value };
    salvar();
    const dados = montarRespostas({ cliente, email, respostas, agora: new Date() });
    baixarJSON(`respostas-${cliente}-${dados.gerado_em.slice(0, 10)}.json`, dados);
    $('enviado').hidden = false;
  });

  window.addEventListener('pagehide', () => {
    for (const [id, area] of campos) respostas = { ...respostas, [id]: area.value };
    salvar();
  });

  $('aviso-memoria').hidden = armazenamento.persistente();
  atualizarProgresso();
}

const sessao = exigirSessao('../');
if (sessao) iniciar(sessao);
