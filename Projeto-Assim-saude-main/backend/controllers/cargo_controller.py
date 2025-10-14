from flask import Blueprint, request, jsonify
from services.db import get_db

cargo_bp = Blueprint('cargo_bp', __name__)

@cargo_bp.route('', methods=['GET'])
def list_cargos():
    nome = request.args.get('nome', '')
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, nome, salario, descricao, criado_em FROM cargos WHERE nome LIKE %s", ('%'+nome+'%',))
    rows = cur.fetchall()
    result = []
    for r in rows:
        result.append({
            'id': r[0],
            'nome': r[1],
            'salario': float(r[2]) if r[2] is not None else None,
            'descricao': r[3],
            'criado_em': r[4].isoformat() if r[4] else None
        })
    return jsonify(result)

@cargo_bp.route('', methods=['POST'])
def create_cargo():
    data = request.get_json()
    nome = data.get('nome')
    salario = data.get('salario')
    descricao = data.get('descricao', '')
    if not nome or salario is None:
        return jsonify({'error': 'nome e salario são obrigatórios'}), 400
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO cargos (nome, salario, descricao) VALUES (%s,%s,%s)", (nome, salario, descricao))
    db.commit()
    return jsonify({'id': cur.lastrowid}), 201

@cargo_bp.route('/<int:id>', methods=['PUT'])
def update_cargo(id):
    data = request.get_json()
    nome = data.get('nome')
    salario = data.get('salario')
    descricao = data.get('descricao', '')
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE cargos SET nome=%s, salario=%s, descricao=%s WHERE id=%s", (nome, salario, descricao, id))
    db.commit()
    return jsonify({'updated': cur.rowcount})

@cargo_bp.route('/<int:id>', methods=['DELETE'])
def delete_cargo(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM cargos WHERE id=%s", (id,))
    db.commit()
    return jsonify({'deleted': cur.rowcount})
