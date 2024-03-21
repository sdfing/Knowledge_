from sqlalchemy.orm import relationship


from database import db


class KnowledgePoints(db.Model):
    __tablename__ = 'knowledge_point'
    KnowledgeID = db.Column(db.Integer, name='知识点id', primary_key=True)
    KnowledgeName = db.Column(db.String(255), name='知识点名称', unique=True)
    KnowledgeBelong = db.Column(db.String(255), name='所属课程')
    # 其他字段...
    student_scores = relationship('student_knowledge', back_populates='knowledge_points')
