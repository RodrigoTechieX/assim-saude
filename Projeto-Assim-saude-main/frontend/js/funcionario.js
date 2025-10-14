
if(!window.API_URL){
  var el = document.createElement('script'); el.src = "../js/config.js"; document.head.appendChild(el);
}

const tabelaBody = document.querySelector('#tabela_funcionarios tbody');
const searchNome = document.getElementById('search_nome');
const searchCpf = document.getElementById('search_cpf');
const btnSearch = document.getElementById('btn_search');
const btnNew = document.getElementById('btn_new');
const form = document.getElementById('form_funcionario');

async function fetchCargos(){
  const res = await fetch(`${API_URL}/cargos`);
  return res.json();
}
async function fetchFuncionarios(nome='', cpf=''){
  const res = await fetch(`${API_URL}/funcionarios?nome=${encodeURIComponent(nome)}&cpf=${encodeURIComponent(cpf)}`);
  return res.json();
}

function renderFuncionarios(funcs){
  tabelaBody.innerHTML = '';
  funcs.forEach(f=>{
    const tr = document.createElement('tr');
    // adiciona data-id para facilitar achar a linha depois
    tr.dataset.id = f.id;
    tr.innerHTML = `<td>${f.id}</td><td>${f.nome}</td><td>${f.cpf}</td><td>${f.telefone||''}</td><td>${f.cargo_nome||''}</td>`;
    // quando clicar, preenche o formulário com o objeto f
    tr.addEventListener('click', () => fillForm(f));
    tabelaBody.appendChild(tr);
  });
}


function fillForm(f){
  document.getElementById('func_id').value = f.id;
  document.getElementById('nome').value = f.nome;
  document.getElementById('data_nascimento').value = f.data_nascimento || '';
  document.getElementById('endereco').value = f.endereco || '';
  document.getElementById('cpf').value = f.cpf;
  document.getElementById('email').value = f.email || '';
  document.getElementById('telefone').value = f.telefone || '';
  document.getElementById('cargo_id').value = f.cargo_id;
}


async function loadCargosIntoSelect(){
  const cargos = await fetchCargos();
  const sel = document.getElementById('cargo_id');
  sel.innerHTML = '';
  cargos.forEach(c=>{
    const opt = document.createElement('option');
    opt.value = c.id; opt.text = c.nome;
    sel.appendChild(opt);
  });
}

btnSearch.onclick = async ()=>{
  const res = await fetchFuncionarios(searchNome.value, searchCpf.value);
  renderFuncionarios(res);
};

btnNew.onclick = ()=>{
  form.reset(); document.getElementById('func_id').value = '';
};

form.onsubmit = async (e) => {
  e.preventDefault();

  const payload = {
    nome: document.getElementById('nome').value.trim(),
    data_nascimento: document.getElementById('data_nascimento').value || null,
    endereco: document.getElementById('endereco').value.trim(),
    cpf: document.getElementById('cpf').value.trim(),
    email: document.getElementById('email').value.trim(),
    telefone: document.getElementById('telefone').value.trim(),
    cargo_id: document.getElementById('cargo_id').value || null
  };

  const id = document.getElementById('func_id').value;
  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = id ? 'Salvando...' : 'Criando...';

  try {
    const url = id ? `${API_URL}/funcionarios/${id}` : `${API_URL}/funcionarios`;
    const method = id ? 'PUT' : 'POST';

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.erro || data.error || 'Erro ao salvar');

    
    if (id) {
      const tr = tabelaBody.querySelector(`tr[data-id="${id}"]`);
      if (tr) {
        const tds = tr.querySelectorAll('td');
        // tds[0] = id, tds[1] = nome, tds[2] = cpf, tds[3] = telefone, tds[4] = cargo_nome
        tds[1].textContent = payload.nome;
        tds[2].textContent = payload.cpf;
        tds[3].textContent = payload.telefone || '';
        // pega o texto do select (nome do cargo)
        tds[4].textContent = (document.getElementById('cargo_id').selectedOptions[0] || {}).text || '';
      }
    }

    // Recarrega a tabela 
    btnSearch.click();

    alert('Salvo com sucesso!');
    // opcional: form.reset();
    // document.getElementById('func_id').value = '';
  } catch (err) {
    console.error(err);
    alert('Erro ao salvar: ' + (err.message || err));
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Salvar';
  }
};


document.getElementById('btn_delete').addEventListener('click', async () => {
  const id = document.getElementById('func_id').value;
  if (!id) return alert('Selecione um funcionário');
  if (!confirm('Deseja excluir este funcionário?')) return;

  const btn = document.getElementById('btn_delete');
  btn.disabled = true;
  btn.textContent = 'Excluindo...';

  try {
    const res = await fetch(`${API_URL}/funcionarios/${id}`, { method: 'DELETE' });
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      alert(data.erro || data.mensagem || 'Erro ao excluir funcionário');
      return;
    }

    alert(data.mensagem || 'Funcionário excluído com sucesso.');
    form.reset();

    // Recarrega a lista com os filtros atuais
    const nome = (searchNome && searchNome.value) ? searchNome.value : '';
    const cpf = (searchCpf && searchCpf.value) ? searchCpf.value : '';
    const funcs = await fetchFuncionarios(nome, cpf);
    renderFuncionarios(funcs);

  } catch (err) {
    console.error('Erro ao excluir funcionário:', err);
    alert('Erro de rede ao excluir funcionário: ' + (err.message || err));
  } finally {
    btn.disabled = false;
    btn.textContent = 'Excluir';
  }
});


// inicial
loadCargosIntoSelect();
btnSearch.click();
