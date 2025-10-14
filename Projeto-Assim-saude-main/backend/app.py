
# --- ADICIONADO: configuração de conexão com banco para múltiplos ambientes ---
import os
from urllib.parse import urlparse

# Prioriza DATABASE_URL (Render / produção), depois LOCAL_DATABASE_URL (local Docker/MySQL), depois fallback sqlite
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("LOCAL_DATABASE_URL") or "sqlite:///dev.db"

# Se for uma URL que começa com postgresql://, SQLAlchemy aceita, mas algumas versões preferem postgresql+psycopg2://
if DATABASE_URL.startswith("postgresql://"):
    # transforma para formato aceito: postgresql+psycopg2:// (caso necessário)
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
# --- FIM DA ADIÇÃO ---

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from services.db import Database
from pymysql.err import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

# ✅ Permitir chamadas de qualquer origem (para o site hospedado)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ✅ Configuração dinâmica do banco — funciona local e na nuvem
DB = Database(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "appuser"),
    password=os.getenv("DB_PASSWORD", "app_password_here"),
    database=os.getenv("DB_NAME", "assim_saude")
)

# ----------------------------
# CARGOS
# ----------------------------
@app.route('/api/cargos', methods=['GET'])
def listar_cargos():
    nome = request.args.get('nome', '')
    cargos = DB.buscar_cargos_por_nome(nome)
    return jsonify(cargos), 200


@app.route('/api/cargos', methods=['POST'])
def adicionar_cargo():
    data = request.json or {}
    nome = data.get('nome')
    salario = data.get('salario')
    descricao = data.get('descricao', '')

    if not nome or salario is None:
        return jsonify({'erro': 'Nome e salário são obrigatórios.'}), 400

    try:
        novo_id = DB.inserir_cargo(nome, salario, descricao)
        return jsonify({'mensagem': 'Cargo criado', 'id': novo_id}), 201
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/cargos/<int:cargo_id>', methods=['PUT'])
def editar_cargo(cargo_id):
    data = request.json or {}
    updated = DB.atualizar_cargo(cargo_id, data.get('nome'), data.get('salario'), data.get('descricao'))
    if updated:
        return jsonify({'mensagem': 'Cargo atualizado'}), 200
    return jsonify({'erro': 'Cargo não encontrado'}), 404


@app.route('/api/cargos/<int:cargo_id>', methods=['DELETE'])
def remover_cargo(cargo_id):
    try:
        deleted = DB.deletar_cargo(cargo_id)
        if deleted:
            return jsonify({'mensagem': 'Cargo excluído'}), 200
        return jsonify({'erro': 'Cargo não encontrado'}), 404
    except IntegrityError:
        return jsonify({'erro': 'Não é possível excluir este cargo: existem funcionários vinculados.'}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ----------------------------
# FUNCIONÁRIOS
# ----------------------------
@app.route('/api/funcionarios', methods=['GET'])
def listar_funcionarios():
    nome = request.args.get('nome', '')
    cpf = request.args.get('cpf', '')
    funcionarios = DB.buscar_funcionarios(nome, cpf)
    return jsonify(funcionarios), 200


@app.route('/api/funcionarios', methods=['POST'])
def adicionar_funcionario():
    data = request.json or {}
    required = ['nome', 'cpf', 'cargo_id']
    for f in required:
        if not data.get(f):
            return jsonify({'erro': f'Campo {f} é obrigatório'}), 400

    try:
        new_id = DB.inserir_funcionario(
            data.get('nome'),
            data.get('data_nascimento'),
            data.get('endereco'),
            data.get('cpf'),
            data.get('email'),
            data.get('telefone'),
            data.get('cargo_id')
        )
        return jsonify({'mensagem': 'Funcionário cadastrado', 'id': new_id}), 201
    except IntegrityError:
        return jsonify({'erro': 'CPF já cadastrado'}), 400
    except ValueError as ve:
        return jsonify({'erro': str(ve)}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/funcionarios/<int:func_id>', methods=['PUT'])
def editar_funcionario(func_id):
    data = request.json or {}
    try:
        updated = DB.atualizar_funcionario(func_id, data)
        if updated:
            return jsonify({'mensagem': 'Funcionário atualizado'}), 200
        return jsonify({'erro': 'Funcionário não encontrado'}), 404
    except ValueError as ve:
        return jsonify({'erro': str(ve)}), 400
    except IntegrityError:
        return jsonify({'erro': 'CPF já cadastrado'}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


@app.route('/api/funcionarios/<int:func_id>', methods=['DELETE'])
def excluir_funcionario(func_id):
    try:
        deleted = DB.deletar_funcionario(func_id)
        if deleted:
            return jsonify({'mensagem': 'Funcionário excluído'}), 200
        return jsonify({'erro': 'Funcionário não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ----------------------------
# CONTADORES GERAIS
# ----------------------------
@app.route('/api/counts', methods=['GET'])
def api_counts():
    try:
        cur = DB.conn.cursor()

        cur.execute("SELECT COUNT(*) FROM cargos")
        cargos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM funcionarios")
        funcionarios = cur.fetchone()[0]

        schema = os.getenv('DB_NAME', 'assim_saude')
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_schema=%s AND table_name=%s
        """, (schema, 'relatorios'))
        existe = cur.fetchone()[0]

        relatorios = None
        if existe:
            cur.execute("SELECT COUNT(*) FROM relatorios")
            relatorios = cur.fetchone()[0]

        return jsonify({
            'cargos': cargos,
            'funcionarios': funcionarios,
            'relatorios': relatorios
        }), 200

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ✅ Detecta automaticamente o ambiente (local ou Render)
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # Render define PORT automaticamente
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug)