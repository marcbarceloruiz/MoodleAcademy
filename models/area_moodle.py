"""
Modelos para la estructura institucional del Moodle.
Academia Profissional Prof. Albino de Matos - Escola Profissional Vértice.
"""
from datetime import datetime
from extensions import db


class AreaMoodle(db.Model):
    __tablename__ = "areas_moodle"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    icono = db.Column(db.String(20), nullable=True)
    tipo = db.Column(db.String(50), nullable=False, default="institucional")
    orden = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, default=True)
    restringido = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    documentos = db.relationship(
        "DocumentoInstitucional",
        backref="area",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="DocumentoInstitucional.orden",
    )

    def __repr__(self):
        return f"<AreaMoodle {self.slug}>"


class DocumentoInstitucional(db.Model):
    __tablename__ = "documentos_institucionales"

    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey("areas_moodle.id"), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    tipo = db.Column(db.String(50), default="documento")
    url = db.Column(db.String(300), nullable=True)
    orden = db.Column(db.Integer, default=0)
    visible = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DocumentoInstitucional {self.titulo}>"
