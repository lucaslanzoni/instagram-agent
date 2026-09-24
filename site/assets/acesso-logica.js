// Portão visual por e-mail (fase de teste). Filtra a tela, não protege arquivos.
export const normalizarEmail = (email) => (email || '').trim().toLowerCase();

export const emailValido = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizarEmail(email));

export function clienteDoEmail(acesso, email) {
  const mapa = acesso?.emails || {};
  const alvo = normalizarEmail(email);
  for (const [cadastrado, cliente] of Object.entries(mapa)) {
    if (normalizarEmail(cadastrado) === alvo) return cliente;
  }
  return null;
}
