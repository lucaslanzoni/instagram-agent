import { normalizarEmail, emailValido, clienteDoEmail } from './acesso-logica.js';
import { lerSessao, salvarSessao, limparSessao, armazenamento } from './sessao.js';

const $ = (id) => document.getElementById(id);
const NOMES_MES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

function formatarMes(mes) {
  const [ano, m] = mes.split('-');
  return `${NOMES_MES[Number(m) - 1] || mes} ${ano}`;
}

async function buscarJSON(url) {
  const r = await fetch(url, { cache: 'no-store' });
  if (!r.ok) throw new Error(`${r.status} em ${url}`);
  return r.json();
}

async function carregarAcesso() {
  try {
    return await buscarJSON('acesso.json');
  } catch {
    return null;
  }
}

function link(texto, href) {
  const a = document.createElement('a');
  a.textContent = texto;
  a.href = href;
  return a;
}

async function mostrarMenu({ cliente }) {
  $('tela-entrada').hidden = true;
  $('tela-menu').hidden = false;
  $('aviso-memoria').hidden = armazenamento.persistente();
  const menu = $('menu');
  menu.replaceChildren(link('Formulário da marca', 'formulario/'));
  let indice = null;
  try {
    indice = await buscarJSON(`clientes/${cliente}/indice.json`);
  } catch {
    indice = null;
  }
  $('nome-cliente').textContent = indice?.nome || cliente;
  $('arroba-cliente').textContent = indice?.arroba || '';
  const meses = [...(indice?.meses || [])].sort().reverse();
  for (const mes of meses) menu.append(link(`Conteúdo de ${formatarMes(mes)}`, `aprovacao/?mes=${encodeURIComponent(mes)}`));
  $('sem-mes').hidden = meses.length > 0;
}

async function tentar(valor) {
  const erro = $('erro');
  erro.textContent = '';
  const email = normalizarEmail(valor);
  if (!emailValido(email)) {
    erro.textContent = 'Digite um e-mail válido.';
    return;
  }
  const acesso = await carregarAcesso();
  if (!acesso) {
    erro.textContent = 'Não foi possível conferir o acesso agora. Tente de novo.';
    return;
  }
  const cliente = clienteDoEmail(acesso, email);
  if (!cliente) {
    erro.textContent = 'Este e-mail ainda não tem acesso. Fale com a consultoria.';
    return;
  }
  salvarSessao({ email, cliente });
  mostrarMenu({ email, cliente });
}

async function iniciar() {
  $('sair').addEventListener('click', () => {
    limparSessao();
    location.reload();
  });
  $('form-acesso').addEventListener('submit', (e) => {
    e.preventDefault();
    tentar($('email').value);
  });
  const sessao = lerSessao();
  if (sessao) {
    const acesso = await carregarAcesso();
    if (acesso && clienteDoEmail(acesso, sessao.email) === sessao.cliente) {
      mostrarMenu(sessao);
      return;
    }
    if (acesso) limparSessao();
  }
  $('email').focus();
}

iniciar();
