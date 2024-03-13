from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


class Student(db.Model):
    __tablename__ = 'students'  # 替换为您的学生信息表名
    student_id = db.Column(db.String(255), primary_key=True, name='学号')
    name = db.Column(db.String(255), name='姓名')
    password_hash = db.Column(db.String(255), name='登录密码')
    major = db.Column(db.String(255), name='专业')
    class_id = db.Column(db.String(255), name='班级')

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
            class_id=class_id
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()
    return student


# 使用示例
student = get_or_create_student(
    student_id='213401010129',
    name='赵柯',
    major='计算机科学与技术',
    class_id='计科2101',
    password='student_password'
)