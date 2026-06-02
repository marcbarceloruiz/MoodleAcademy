"""
Modelos para estructura interna de disciplinas: módulos, recursos y actividades.
"""
from datetime import datetime
from extensions import db


class ModuloActividad(db.Model):
    __tablename__ = "modulos_actividades"

    id = db.Column(db.Integer, primary_key=True)
    disciplina_id = db.Column(db.Integer, db.ForeignKey("disciplinas.id"), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    seccion = db.Column(db.String(50), default="contenidos")
    tipo = db.Column(db.String(50), default="modulo")
    descripcion = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(300), nullable=True)
    estado = db.Column(db.String(30), default="no-comenzado")
    orden = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    recursos = db.relationship(
        "Recurso",
        backref="modulo",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Recurso.orden",
    )

    def __repr__(self):
        return f"<ModuloActividad {self.titulo}>"


class Recurso(db.Model):
    __tablename__ = "recursos"

    id = db.Column(db.Integer, primary_key=True)
    modulo_id = db.Column(db.Integer, db.ForeignKey("modulos_actividades.id"), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(30), default="link")
    duracion = db.Column(db.String(30), nullable=True)
    url = db.Column(db.String(300), nullable=True)
    estado = db.Column(db.String(30), default="no-comenzado")
    orden = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Recurso {self.titulo}>"
