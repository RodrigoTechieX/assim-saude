
const updateCounts = async () => {
  const elCargos = document.getElementById('count-cargos');
  const elFuncs = document.getElementById('count-funcionarios');
  const elRels = document.getElementById('count-relatorios');
  if (!elCargos && !elFuncs && !elRels) return;

  try {
    const res = await fetch(`${API_URL}/counts`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (elCargos) elCargos.textContent = (data.cargos ?? 0).toString();
    if (elFuncs)  elFuncs.textContent  = (data.funcionarios ?? 0).toString();

    // mostra "—" se relatorios não existir (null), senão número
    if (elRels) {
      elRels.textContent = (data.relatorios === null || data.relatorios === undefined) ? '—' : data.relatorios.toString();
    }
  } catch (err) {
    console.error('Erro ao buscar counts:', err);
    if (elCargos) elCargos.textContent = '!';
    if (elFuncs)  elFuncs.textContent  = '!';
    if (elRels)   elRels.textContent   = '!';
  }
};

// inicia ao carregar e repete a cada 5s
document.addEventListener('DOMContentLoaded', () => {
  updateCounts();
  setInterval(updateCounts, 5000);
});

