"""
Modelos para ciclos formativos, años y disciplinas.
"""
from datetime import datetime
from extensions import db


class CicloFormativo(db.Model):
    __tablename__ = "ciclos_formativos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=True)
    nombre = db.Column(db.String(200), nullable=False)
    area = db.Column(db.String(100), nullable=True)
    nivel = db.Column(db.String(50), nullable=True)
    duracion = db.Column(db.String(80), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    anos = db.relationship(
        "AnoCurso",
        backref="ciclo",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="AnoCurso.numero",
    )

    def __repr__(self):
        return f"<CicloFormativo {self.nombre}>"


class AnoCurso(db.Model):
    __tablename__ = "anos_curso"

    id = db.Column(db.Integer, primary_key=True)
    ciclo_id = db.Column(db.Integer, db.ForeignKey("ciclos_formativos.id"), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    ano_escolar = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)

    disciplinas = db.relationship(
        "Disciplina",
        backref="ano",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Disciplina.orden",
    )

    def __repr__(self):
        return f"<AnoCurso {self.ano_escolar}>"


class Disciplina(db.Model):
    __tablename__ = "disciplinas"

    id = db.Column(db.Integer, primary_key=True)
    ano_id = db.Column(db.Integer, db.ForeignKey("anos_curso.id"), nullable=False)
    codigo = db.Column(db.String(30), nullable=True)
    nombre = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(30), default="disciplina")  # disciplina | fct | pap
    horas = db.Column(db.Integer, nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    orden = db.Column(db.Integer, default=0)

    modulos = db.relationship(
        "ModuloActividad",
        backref="disciplina",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="ModuloActividad.orden",
    )

    def __repr__(self):
        return f"<Disciplina {self.nombre}>"
