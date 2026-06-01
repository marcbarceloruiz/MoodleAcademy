from extensions import db


class Centro(db.Model):
    __tablename__ = "centro"

    id = db.Column(db.Integer, primary_key=True)
    nome_oficial = db.Column(db.String(255), nullable=False)
    nome_curto = db.Column(db.String(150), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(100), nullable=False)