// cargo.js
importScript = function(src){var s=document.createElement('script');s.src=src;document.head.appendChild(s);};
if(!window.API_URL){
  // try to add config
  var el = document.createElement('script'); el.src = "../js/config.js"; document.head.appendChild(el);
}

const tabelaBody = document.querySelector('#tabela_cargos tbody');
const searchInput = document.getElementById('search_nome');
const btnSearch = document.getElementById('btn_search');
const btnNew = document.getElementById('btn_new');
const form = document.getElementById('form_cargo');

async function fetchCargos(nome=''){
  const res = await fetch(`${API_URL}/cargos?nome=${encodeURIComponent(nome)}`);
  return res.json();
}

function renderCargos(cargos){
  tabelaBody.innerHTML = '';
  cargos.forEach(c=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${c.id}</td><td>${c.nome}</td><td>${c.salario}</td><td>${c.descricao||''}</td>`;
    tr.onclick = ()=> fillForm(c);
    tabelaBody.appendChild(tr);
  });
}

function fillForm(c){
  document.getElementById('cargo_id').value = c.id;
  document.getElementById('nome').value = c.nome;
  document.getElementById('salario').value = c.salario;
  document.getElementById('descricao').value = c.descricao || '';
}

btnSearch.onclick = async ()=> {
  const data = await fetchCargos(searchInput.value);
  renderCargos(data);
};

btnNew.onclick = ()=> {
  form.reset();
  document.getElementById('cargo_id').value = '';
};

form.onsubmit = async (e)=>{
  e.preventDefault();
  const payload = {
    nome: document.getElementById('nome').value,
    salario: document.getElementById('salario').value,
    descricao: document.getElementById('descricao').value
  };
  const id = document.getElementById('cargo_id').value;
  if(id){
    await fetch(`${API_URL}/cargos/${id}`, {method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  } else {
    await fetch(`${API_URL}/cargos`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
  }
  // refresh
  btnSearch.click();
};

document.getElementById('btn_delete').addEventListener('click', async () => {
  const id = document.getElementById('cargo_id').value;
  if (!id) return alert('Selecione um cargo');
  if (!confirm('Deseja excluir este cargo?')) return;

  const btn = document.getElementById('btn_delete');
  btn.disabled = true;
  btn.textContent = 'Excluindo...';

  try {
    const res = await fetch(`${API_URL}/cargos/${id}`, { method: 'DELETE' });
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      alert(data.erro || data.mensagem || 'Erro ao excluir cargo');
      return;
    }

    alert(data.mensagem || 'Cargo excluído com sucesso.');
    form.reset();

    // Recarrega a lista com o termo de busca atual (se existir)
    const nomeBusca = (searchInput && searchInput.value) ? searchInput.value : '';
    const cargos = await fetchCargos(nomeBusca);
    renderCargos(cargos);

  } catch (err) {
    console.error('Erro ao excluir cargo:', err);
    alert('Erro de rede ao excluir cargo: ' + (err.message || err));
  } finally {
    btn.disabled = false;
    btn.textContent = 'Excluir';
  }
});


// load initial cargos
btnSearch.click();
