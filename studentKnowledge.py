from database import db
from graph import g


class StudentKnowledge(db.Model):
    __tablename__ = 'points'  # 确保名称一定要和数据库的表相同
    student_id = db.Column(db.String(255), primary_key=True,name='学号')
    student_name = db.Column(db.String(128),name='姓名')
    for i in range(1,112):
        a=g.name[i]
        locals()[f'{a}'] = db.Column(db.Float)

