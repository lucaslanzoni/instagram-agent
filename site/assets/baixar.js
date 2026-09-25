export function baixarBlob(nome, blob) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = nome;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Celular: o menu de compartilhar salva as imagens direto na galeria ("Salvar imagens").
// O app do Drive no iPhone não abre .zip, por isso o post não vai compactado no celular.
export function podeCompartilhar(arquivos, nav = globalThis.navigator) {
  if (!nav || typeof nav.canShare !== 'function' || typeof nav.share !== 'function') return false;
  if (!arquivos || arquivos.length === 0) return false;
  try {
    return nav.canShare({ files: arquivos });
  } catch {
    return false;
  }
}

// Precisa ser chamada direto do toque do usuário (sem await antes), senão o iOS recusa.
export async function compartilharArquivos(arquivos, titulo, nav = globalThis.navigator) {
  try {
    await nav.share({ files: arquivos, title: titulo });
    return 'compartilhado';
  } catch (erro) {
    if (erro && erro.name === 'AbortError') return 'cancelado';
    throw erro;
  }
}

export function baixarJSON(nome, dados) {
  baixarBlob(nome, new Blob([JSON.stringify(dados, null, 2)], { type: 'application/json' }));
}
