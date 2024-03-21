from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from database import db


class StudentKnowledge(db.Model):
    __tablename__ = 'student_knowledge'

    KnowledgeID = db.Column(db.String(255), ForeignKey('knowledge_points.KnowledgeID'), name='知识点id', primary_key=True)
    StudentID = db.Column(db.String(255), name='学号', primary_key=True)

    Score = db.Column(db.Float, name='分数')

    # 设置与Student模型的关系
    # student = relationship('Student', back_populates='knowledge_scores')
    # 设置与KnowledgePoints模型的关系
    knowledge_point = relationship('knowledge_points', back_populates='student_scores')
