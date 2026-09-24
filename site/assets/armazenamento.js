// Guarda dados no navegador. Se o localStorage falhar (aba anônima, bloqueio),
// continua funcionando em memória e avisa por persistente() === false.
export function criarArmazenamento(backend) {
  const memoria = new Map();
  let usarMemoria = !backend;

  function lerBruto(chave) {
    if (usarMemoria) return memoria.has(chave) ? memoria.get(chave) : null;
    try {
      return backend.getItem(chave);
    } catch {
      usarMemoria = true;
      return memoria.has(chave) ? memoria.get(chave) : null;
    }
  }

  return {
    ler(chave) {
      const bruto = lerBruto(chave);
      if (bruto === null || bruto === undefined) return null;
      try {
        return JSON.parse(bruto);
      } catch {
        return null;
      }
    },
    gravar(chave, valor) {
      const bruto = JSON.stringify(valor);
      memoria.set(chave, bruto);
      if (usarMemoria) return;
      try {
        backend.setItem(chave, bruto);
      } catch {
        usarMemoria = true;
      }
    },
    remover(chave) {
      memoria.delete(chave);
      if (usarMemoria) return;
      try {
        backend.removeItem(chave);
      } catch {
        usarMemoria = true;
      }
    },
    persistente() {
      return !usarMemoria;
    },
  };
}

export function armazenamentoDoNavegador() {
  let backend = null;
  try {
    backend = globalThis.localStorage ?? null;
  } catch {
    backend = null;
  }
  return criarArmazenamento(backend);
}
