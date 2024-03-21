
from werkzeug.security import generate_password_hash
from database import db
from sqlalchemy import text
from sqlalchemy.orm import relationship


class Student(db.Model):
    __tablename__ = 'student'  # 学生表名
    student_id = db.Column(db.String(255), primary_key=True, name='学号')
    name = db.Column(db.String(255), name='姓名')
    password_hash = db.Column(db.String(255), name='登录密码')
    major = db.Column(db.String(255), name='专业')
    class_id = db.Column(db.String(255), name='班级')
    # knowledge_scores = relationship('StudentKnowledge', back_populates='student')


    # ... 其他个人信息字段 ...

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


def get_or_create_student(student_id, name, major, class_id, password):


    """
    从选课表中查询学生的信息，如果学生不存在则创建新记录。

    :param student_id: 学生的学号。
    :param name: 学生的姓名。
    :param major: 学生的专业。
    :param class_id: 学生的班级。
    :param password: 学生的登录密码。
    :return: Student对象。
    """
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        student = Student(
            student_id=student_id,
            name=name,
            major=major,
            class_id=class_id,
            password_hash='1'
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()
    return student


def extract_and_save_student_info():
    """
    从选课表中提取所有学生的信息，并保存到学生信息表中。
    """
    # 查询选课表中的所有不同学生的信息
    sql_query = text("""
        SELECT DISTINCT
            学号,
            姓名,
            专业,
            班级
        FROM
            enrollment
    """)
    results = db.session.execute(sql_query)

    # 遍历查询结果，为每个学生创建或更新记录
    for row in results:
        student_id, name, major, class_id = row
        # 检查学生是否已存在
        existing_student = Student.query.filter_by(student_id=student_id).first()
        if not existing_student:
            # 学生不存在，创建新记录
            new_student = Student(
                student_id=student_id,
                name=name,
                major=major,
                class_id=class_id
            )
            # 设置一个默认密码，实际应用中应该让用户自己设置或生成随机密码
            default_password = 'default_password'
            # 设置默认密码或生成随机密码
            new_student.set_password(default_password)
            db.session.add(new_student)

    # 提交所有新记录到数据库
    db.session.commit()














