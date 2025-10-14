from flask import Blueprint, app, request, jsonify
from pymysql import IntegrityError
from backend.app import DB
from services.db import get_db
import re

funcionario_bp = Blueprint('funcionario_bp', __name__)

def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf or '')
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    def calc(digs):
        s = sum(int(digs[i]) * (len(digs) + 1 - i) for i in range(len(digs)))
        r = s % 11
        return 0 if r < 2 else 11 - r
    d1 = calc(cpf[:9])
    d2 = calc(cpf[:10])
    return d1 == int(cpf[9]) and d2 == int(cpf[10])

@funcionario_bp.route('', methods=['GET'])
def list_funcionarios():
    nome = request.args.get('nome', '')
    cargo_id = request.args.get('cargo_id', None)
    db = get_db()
    cur = db.cursor()
    if cargo_id:
        cur.execute("""SELECT f.id, f.nome, f.cpf, f.telefone, c.nome, c.salario 
                       FROM funcionarios f JOIN cargos c ON f.cargo_id = c.id
                       WHERE f.nome LIKE %s AND c.id = %s""", ('%'+nome+'%', cargo_id))
    else:
        cur.execute("""SELECT f.id, f.nome, f.cpf, f.telefone, c.nome, c.salario 
                       FROM funcionarios f JOIN cargos c ON f.cargo_id = c.id
                       WHERE f.nome LIKE %s""", ('%'+nome+'%',))
    rows = cur.fetchall()
    result = []
    for r in rows:
        result.append({
            'id': r[0], 'nome': r[1], 'cpf': r[2], 'telefone': r[3], 'cargo': r[4], 'salario': float(r[5])
        })
    return jsonify(result)

@funcionario_bp.route('', methods=['POST'])
def create_funcionario():
    data = request.get_json()
    nome = data.get('nome')
    cpf = data.get('cpf')
    cargo_id = data.get('cargo_id')
    if not nome or not cpf or not cargo_id:
        return jsonify({'error': 'nome, cpf e cargo_id são obrigatórios'}), 400
    if not validar_cpf(cpf):
        return jsonify({'error': 'CPF inválido'}), 400
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM funcionarios WHERE cpf = %s", (cpf,))
    if cur.fetchone():
        return jsonify({'error': 'CPF já cadastrado'}), 400
    cur.execute("INSERT INTO funcionarios (nome, data_nascimento, endereco, cpf, email, telefone, cargo_id) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (nome, data.get('data_nascimento'), data.get('endereco'), cpf, data.get('email'), data.get('telefone'), cargo_id))
    db.commit()
    return jsonify({'id': cur.lastrowid}), 201



@app.route('/api/funcionarios/<int:func_id>', methods=['PUT'])
def update_funcionario(func_id):
    data = request.get_json() or {}
    try:
        updated = DB.atualizar_funcionario(func_id, data)  # seu Database() tem esse método
        if updated:
            return jsonify({'mensagem': 'Funcionário atualizado'}), 200
        return jsonify({'erro': 'Funcionário não encontrado'}), 404
    except ValueError as ve:
        return jsonify({'erro': str(ve)}), 400
    except IntegrityError:
        return jsonify({'erro': 'CPF já cadastrado'}), 400
    except Exception as e:
        app.logger.exception(e)
        return jsonify({'erro': 'Erro interno'}), 500


@funcionario_bp.route('/<int:id>', methods=['DELETE'])
def delete_funcionario(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM funcionarios WHERE id=%s", (id,))
    db.commit()
    return jsonify({'deleted': cur.rowcount})
