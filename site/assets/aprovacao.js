import { exigirSessao, armazenamento } from './sessao.js';
import {
  validarManifesto, escolherMes, definirStatus, definirComentario, editarLegenda,
  legendaFinal, limparEstado, carimbarVersao, resumo, montarAprovacao, arquivosDoPost,
} from './aprovacao-logica.js';
import { baixarBlob, baixarJSON } from './baixar.js';

const $ = (id) => document.getElementById(id);
const ROTULO_FORMATO = { carrossel: 'Carrossel', estatico: 'Post estático' };
const NOMES_MES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

function formatarMes(mes) {
  const [ano, m] = mes.split('-');
  return `${NOMES_MES[Number(m) - 1] || mes} ${ano}`;
}

function formatarData(data) {
  if (!data) return '';
  const [, m, d] = data.split('-');
  return `${d}/${m}`;
}

function comVersao(url, post) {
  return post.versao ? `${url}?v=${post.versao}` : url;
}

function el(tag, texto, classe) {
  const e = document.createElement(tag);
  if (texto) e.textContent = texto;
  if (classe) e.className = classe;
  return e;
}

function mostrarMensagem(texto, erro) {
  $('mensagem').textContent = texto;
  $('mensagem').hidden = false;
  if (erro) console.error(erro);
}

async function buscarJSON(url) {
  const r = await fetch(url, { cache: 'no-store' });
  if (!r.ok) throw new Error(`${r.status} em ${url}`);
  return r.json();
}

async function iniciar({ email, cliente }) {
  let indice;
  try {
    indice = await buscarJSON(`../clientes/${cliente}/indice.json`);
  } catch {
    indice = null;
  }
  const mes = escolherMes(indice, new URLSearchParams(location.search).get('mes'));
  if (!mes) {
    mostrarMensagem('Ainda não há conteúdo publicado para esta marca.');
    return;
  }
  const base = `../clientes/${cliente}/${mes}/`;
  const manifesto = await buscarJSON(`${base}manifesto.json`);
  const erros = validarManifesto(manifesto);
  if (erros.length) {
    mostrarMensagem(`O conteúdo deste mês está com problema: ${erros[0]}. Fale com o Lucas.`);
    return;
  }
  const posts = manifesto.posts;
  const chave = `ia_aprov_${cliente}_${mes}`;
  let estado = carimbarVersao(limparEstado(armazenamento.ler(chave) || {}, posts), posts);
  let aberto = null;

  $('cliente-nome').textContent = manifesto.nome || cliente;
  $('cliente-mes').textContent = formatarMes(mes);
  $('cliente-arroba').textContent = `${manifesto.arroba || ''} · ${posts.length} publicações`;
  $('aviso-memoria').hidden = armazenamento.persistente();
  $('enviar').hidden = false;
  $('baixar-tudo').hidden = false;

  function salvar(novo) {
    estado = carimbarVersao(novo, posts);
    armazenamento.gravar(chave, estado);
    desenharStatus();
  }

  function desenharStatus() {
    const r = resumo(estado, posts);
    $('resumo').textContent = `${r.aprovado} aprovados · ${r.revisar} para revisar · ${r.descartado} descartados · ${r.pendente} pendentes`;
    for (const no of document.querySelectorAll('[data-post]')) {
      const s = estado[no.dataset.post]?.status || '';
      no.dataset.status = s;
    }
    if (aberto) {
      const s = estado[aberto.id]?.status || '';
      for (const b of $('status-botoes').children) b.setAttribute('aria-pressed', String(b.dataset.status === s));
      const revisar = s === 'revisar';
      $('comentario').hidden = !revisar;
      $('rotulo-comentario').hidden = !revisar;
    }
  }

  function miniatura(post) {
    const img = document.createElement('img');
    img.src = comVersao(base + post.imagens[0], post);
    img.alt = post.alt || post.tema || '';
    img.loading = 'lazy';
    return img;
  }

  posts.forEach((post, i) => {
    const item = el('button', null, 'item');
    item.type = 'button';
    const texto = el('span', post.tema || post.id, 'tema');
    texto.append(el('span', ROTULO_FORMATO[post.formato], 'formato'));
    const ponto = el('span', null, 'ponto-status');
    ponto.dataset.post = post.id;
    item.append(el('span', String(post.numero).padStart(2, '0'), 'num'), miniatura(post), texto, ponto);
    item.addEventListener('click', () => abrir(i));
    const li = document.createElement('li');
    li.append(item);
    $('lista').append(li);

    const celula = el('button', null, 'celula');
    celula.type = 'button';
    celula.dataset.post = post.id;
    celula.setAttribute('aria-label', `Abrir post ${post.numero}: ${post.tema || ''}`);
    celula.append(miniatura(post), el('span', String(post.numero).padStart(2, '0'), 'selo num'), el('span', ROTULO_FORMATO[post.formato], 'selo formato'));
    celula.addEventListener('click', () => abrir(i));
    $('grade').append(celula);
  });

  function slideAtual() {
    const c = $('carrossel');
    return Math.round(c.scrollLeft / Math.max(c.clientWidth, 1));
  }

  function desenharPontos() {
    const atual = slideAtual();
    [...$('pontos').children].forEach((p, i) => p.classList.toggle('ativo', i === atual));
  }

  function irPara(i) {
    const c = $('carrossel');
    c.scrollTo({ left: i * c.clientWidth, behavior: 'smooth' });
  }

  function abrir(i) {
    aberto = posts[i];
    const c = $('carrossel');
    c.replaceChildren(...aberto.imagens.map((src, n) => {
      const img = document.createElement('img');
      img.src = comVersao(base + src, aberto);
      img.alt = n === 0 ? aberto.alt || '' : `Slide ${n + 1}`;
      return img;
    }));
    c.scrollLeft = 0;
    $('pontos').replaceChildren(...aberto.imagens.map(() => el('span')));
    const varios = aberto.imagens.length > 1;
    $('anterior').hidden = !varios;
    $('proxima').hidden = !varios;
    $('pontos').hidden = !varios;
    $('post-info').textContent = [String(aberto.numero).padStart(2, '0'), ROTULO_FORMATO[aberto.formato], formatarData(aberto.data_sugerida)].filter(Boolean).join(' · ');
    $('post-tema').textContent = aberto.tema || '';
    $('legenda').value = legendaFinal(aberto, estado);
    $('comentario').value = estado[aberto.id]?.comentario || '';
    $('copiado').hidden = true;
    desenharStatus();
    desenharPontos();
    $('janela').showModal();
  }

  $('carrossel').addEventListener('scroll', desenharPontos, { passive: true });
  $('anterior').addEventListener('click', () => irPara(Math.max(slideAtual() - 1, 0)));
  $('proxima').addEventListener('click', () => irPara(Math.min(slideAtual() + 1, aberto.imagens.length - 1)));
  $('janela').addEventListener('keydown', (e) => {
    if (e.target.tagName === 'TEXTAREA') return;
    if (e.key === 'ArrowLeft') $('anterior').click();
    if (e.key === 'ArrowRight') $('proxima').click();
  });
  $('janela').addEventListener('close', () => { aberto = null; });
  $('fechar').addEventListener('click', () => $('janela').close());

  for (const botao of $('status-botoes').children) {
    botao.addEventListener('click', () => salvar(definirStatus(estado, aberto.id, botao.dataset.status)));
  }
  $('comentario').addEventListener('input', () => salvar(definirComentario(estado, aberto.id, $('comentario').value)));
  $('legenda').addEventListener('input', () => salvar(editarLegenda(estado, aberto.id, $('legenda').value, aberto.legenda)));
  $('copiar').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText($('legenda').value);
      $('copiado').textContent = 'Legenda copiada.';
    } catch {
      $('legenda').select();
      $('copiado').textContent = 'Selecionei a legenda. Use copiar do seu aparelho.';
    }
    $('copiado').hidden = false;
  });

  async function baixarZip(lista, nomeZip, botao) {
    if (!window.JSZip) {
      mostrarMensagem('Não foi possível preparar o download. Verifique a conexão e tente de novo.');
      return;
    }
    const rotulo = botao.textContent;
    botao.disabled = true;
    botao.textContent = 'Preparando...';
    try {
      const zip = new window.JSZip();
      for (const post of lista) {
        const arquivos = arquivosDoPost(post, estado);
        for (const img of arquivos.imagens) {
          const r = await fetch(comVersao(base + img.src, post));
          if (!r.ok) throw new Error(`${r.status} em ${img.src}`);
          zip.file(img.nome, await r.blob());
        }
        zip.file(arquivos.legenda.nome, arquivos.legenda.texto);
      }
      baixarBlob(nomeZip, await zip.generateAsync({ type: 'blob' }));
    } catch (erro) {
      mostrarMensagem('O download falhou. Tente de novo.', erro);
    } finally {
      botao.disabled = false;
      botao.textContent = rotulo;
    }
  }

  $('baixar-post').addEventListener('click', () => baixarZip([aberto], `${cliente}-${mes}-${aberto.id}.zip`, $('baixar-post')));
  $('baixar-tudo').addEventListener('click', () => baixarZip(posts, `${cliente}-${mes}.zip`, $('baixar-tudo')));
  $('enviar').addEventListener('click', () => {
    baixarJSON(`aprovacao-${cliente}-${mes}.json`, montarAprovacao({ cliente, mes, email, estado, posts, agora: new Date() }));
    $('enviado').hidden = false;
  });

  desenharStatus();
}

const sessao = exigirSessao('../');
if (sessao) iniciar(sessao).catch((erro) => mostrarMensagem('Não foi possível carregar o conteúdo. Recarregue a página.', erro));
