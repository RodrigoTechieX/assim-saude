
if(!window.API_URL){
  var el = document.createElement('script'); el.src = "../js/config.js"; document.head.appendChild(el);
}

const tabelaBody = document.querySelector('#tabela_relatorio tbody');
const btnFilter = document.getElementById('btn_filter');

async function fetchCargos(){
  const res = await fetch(`${API_URL}/cargos`);
  return res.json();
}
async function fetchFuncionarios(nome='', cargo=''){
  // cargo filter: we'll filter clientside by cargo id if backend doesn't support direct join filter param
  const res = await fetch(`${API_URL}/funcionarios?nome=${encodeURIComponent(nome)}`);
  return res.json();
}

function renderRelatorio(funcs){
  tabelaBody.innerHTML = '';

 
  funcs.forEach((f, idx) => {
    const tr = document.createElement('tr');


    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${f.nome || ''}</td>
      <td>${f.telefone || ''}</td>
      <td>${f.cargo_nome || f.cargo || ''}</td>
      <td>${f.cargo_salario || ''}</td>
    `;
    tabelaBody.appendChild(tr);
  });

  
  try {
    localStorage.setItem('relatorios_count', String(funcs.length));
  } catch (e) {
    // se storage falhar, não atrapalha a renderização
    console.warn('Não foi possível salvar relatorios_count em localStorage', e);
  }
}


async function loadFilters(){
  const cargos = await fetchCargos();
  const sel = document.getElementById('filter_cargo');
  cargos.forEach(c=>{
    const opt = document.createElement('option');
    opt.value = c.id; opt.text = c.nome;
    sel.appendChild(opt);
  });
}

btnFilter.onclick = async ()=>{
  const nome = document.getElementById('filter_nome').value;
  const cargo = document.getElementById('filter_cargo').value;
  const funcs = await fetchFuncionarios(nome);
  const filtered = cargo ? funcs.filter(f=> String(f.cargo_id) === String(cargo)) : funcs;
  renderRelatorio(filtered);
};

loadFilters();
btnFilter.click();
