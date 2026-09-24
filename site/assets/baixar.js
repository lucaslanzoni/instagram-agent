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

export function baixarJSON(nome, dados) {
  baixarBlob(nome, new Blob([JSON.stringify(dados, null, 2)], { type: 'application/json' }));
}
