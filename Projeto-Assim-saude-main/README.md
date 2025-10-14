# Projeto-Assim-saude

# 🏥 Assim Saúde — Sistema de Gestão de Saúde

O **Assim Saúde** é um sistema completo para gestão de dados de pacientes, funcionários, cargos, consultas e muito mais.  
Desenvolvido com **Flask (Python)** no backend, **MySQL** para persistência de dados e **HTML/CSS/JS + Nginx** no frontend,  
ele visa proporcionar **controle, eficiência e clareza** na administração de clínicas e unidades de saúde.  
Sistema desenvolvido para avaliação da empresa **Assim Saúde**.

---

## 🚀 Quickstart (Execução Rápida)

Clone o repositório e suba todo o ambiente com Docker em um único comando:

```bash
git clone https://github.com/RodrigoTechieX/Projeto-Assim-saude.git
cd projeto-assim-saude
docker compose up -d
```

Após iniciar, acesse no navegador:  
👉 [http://localhost:8080](http://localhost:8080)

---

## 🧩 Estrutura do Projeto

```
projeto-assim-saude/
│
├── backend/                 # API Flask (Python)
│   ├── app.py
│   ├── services/
│   └── ...
│
├── frontend/                # Interface do usuário (HTML/CSS/JS)
│   ├── index.html
│   └── pages/
│
├── database/
│   └── script.sql           # Script de criação do banco
│
├── docker-compose.yml       # Orquestração dos containers
└── README.md
```

---

## 🐳 Configuração com Docker

O projeto já vem totalmente configurado para uso com Docker Compose.

### 🔧 Subir os containers

```bash
docker compose up -d
```

Isso criará os seguintes serviços:

| Serviço | Imagem | Porta | Descrição |
|----------|--------|--------|-----------|
| **assim_db** | mysql:8.0 | 3306 | Banco de dados MySQL |
| **assim_backend** | python:3.11 | 5000 | API Flask |
| **assim_frontend** | nginx:alpine | 8080 | Frontend (HTML/CSS/JS) |

### 🧱 Banco de Dados (MySQL)

Por padrão, o banco é iniciado com as credenciais:

```
Usuário: root
Senha: root
Banco: assim_saude
Host: db
Porta: 3306
```

O arquivo `database/script.sql` é executado automaticamente **apenas na primeira criação** do container MySQL.

> ⚠️ Caso já exista um volume anterior (`db_data`), o script **não será executado novamente**.  
> Para recriar o banco do zero e rodar o script novamente:
>
> ```bash
> docker compose down -v
> docker compose up -d
> ```

---

## ⚙️ Variáveis de Ambiente

As variáveis do backend Flask são configuradas automaticamente no `docker-compose.yml`,  
mas caso queira rodar localmente sem Docker, crie um arquivo `.env` dentro da pasta `backend/`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=assim_saude
FLASK_ENV=development
```

---

## 🧩 Estrutura do Banco de Dados

```sql
-- cria DB (se ainda não existir)
CREATE DATABASE IF NOT EXISTS assim_saude
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE assim_saude;

-- cargos
CREATE TABLE IF NOT EXISTS cargos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  salario DECIMAL(10,2) NOT NULL,
  descricao TEXT,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- funcionarios
CREATE TABLE IF NOT EXISTS funcionarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(255) NOT NULL,
  data_nascimento DATE,
  endereco TEXT,
  cpf VARCHAR(14) NOT NULL UNIQUE,
  email VARCHAR(255),
  telefone VARCHAR(20),
  cargo_id INT NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (cargo_id) REFERENCES cargos(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- relatorios
CREATE TABLE IF NOT EXISTS relatorios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(255) NOT NULL,
  descricao TEXT,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- índices
CREATE INDEX idx_funcionarios_nome ON funcionarios(nome);
CREATE INDEX idx_cargos_nome ON cargos(nome);

```

---

## 💻 Rodar o Frontend sem Docker (opcional)

Caso queira testar o frontend diretamente:

```bash
cd frontend
python -m http.server 8080
```

E acesse: 👉 [http://localhost:8080](http://localhost:8080)

---

## 🧠 Estrutura de Pastas do Backend (Flask)

```
backend/
│
├── app.py                # Ponto principal da aplicação Flask
├── services/
│   ├── db.py             # Classe de conexão com MySQL
│   ├── funcionarios.py   # CRUD de funcionários
│   ├── cargos.py         # CRUD de cargos
│   └── ...
│
└── requirements.txt      # Dependências do Python
```

Para rodar manualmente (fora do Docker):

```bash
cd backend
pip install -r requirements.txt
flask run
```

---

## 🧰 Comandos Úteis do Docker

| Comando | Descrição |
|----------|------------|
| `docker compose up -d` | Sobe todos os serviços em segundo plano |
| `docker compose down` | Para e remove containers |
| `docker compose logs -f backend` | Acompanha logs do backend em tempo real |
| `docker exec -it assim_db bash` | Acessa o container do MySQL |

---

## 🧪 Testar a API (via cURL ou Postman)

```bash
curl -X GET http://localhost:5000/funcionarios
```

Exemplo de retorno esperado:

```json
[
  {
    "id": 1,
    "nome": "João Silva",
    "cpf": "123.456.789-00",
    "email": "joao@assimsaude.com",
    "cargo": "Enfermeiro"
  }
]
```

---

## 🩺 Tecnologias Utilizadas

| Categoria | Tecnologias |
|------------|--------------|
| **Backend** | Python, Flask, PyMySQL |
| **Banco de Dados** | MySQL |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Infraestrutura** | Docker, Docker Compose, Nginx |

---

## 🧑‍💻 Autor

**Rodrigo Ferreira da Silva Filho**  
✉️ [contato.rodrigo.tech@gmail.com]<br>
🔗 [https://www.linkedin.com/in/rodrigo-ferreira-325527272/]<br>
📁 Projeto desenvolvido como parte da avaliação — Assim Saúde

---

## 🏁 Licença

Este projeto é distribuído sob a licença **MIT**.  
Sinta-se livre para usar, modificar e distribuir.
