# models.py
from main import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    teacher = db.Column(db.String(32))

    def __repr__(self):
        return '<Course %r>' % self.name
