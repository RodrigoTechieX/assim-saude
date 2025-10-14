"""
models/funcionario.py

Modelo ORM SQLAlchemy para tabela 'funcionarios'.
"""

from datetime import datetime
from services.db import db


class Funcionario(db.Model):
    __tablename__ = "funcionarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(20), nullable=False, unique=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(150), nullable=True)
    telefone = db.Column(db.String(50), nullable=True)
    cargo_id = db.Column(db.Integer, db.ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    cargo = db.relationship("Cargo", backref=db.backref("funcionarios", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "data_nascimento": self.data_nascimento.isoformat() if self.data_nascimento else None,
            "endereco": self.endereco,
            "email": self.email,
            "telefone": self.telefone,
            "cargo_id": self.cargo_id,
            "cargo": self.cargo.nome if self.cargo else None,
            "ativo": bool(self.ativo),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
