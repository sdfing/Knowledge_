from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from sqlalchemy import text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, name='课程代码')
    name = db.Column(db.String(64), unique=True, nullable=False, name='课程名称')

    # ... other course fields ...

    @staticmethod
    def extract_and_save_course_info():
        """
        Extract all courses from the enrollment table and save them to the course table.
        """
        # Query the enrollment table for all distinct courses
        sql_query = text("""
            SELECT DISTINCT
                课程代码,
                课程名称
            FROM
                enrollment
        """)
        results = db.session.execute(sql_query)

        # Iterate through the results and create or update course records
        for row in results:
            course_code, course_name = row
            # Check if the course already exists
            existing_course = Course.query.filter_by(id=course_code).first()
            if not existing_course:
                # Course does not exist, create a new record
                new_course = Course(
                    id=course_code,
                    name=course_name
                )
                db.session.add(new_course)

        # Commit all new records to the database
        db.session.commit()

    def __repr__(self):
        return '<Course %r>' % self.name


class Student(db.Model):
    __tablename__ = 'student'  # 学生表名
    student_id = db.Column(db.String(255), primary_key=True, name='学号')
    name = db.Column(db.String(255), name='姓名')
    password_hash = db.Column(db.String(255), name='登录密码')
    major = db.Column(db.String(255), name='专业')
    class_id = db.Column(db.String(255), name='班级')
    gender = db.Column(db.String(255), name='性别')

    # knowledge_scores = relationship('StudentKnowledge', back_populates='student')

    # ... 其他个人信息字段 ...

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
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

    @staticmethod
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
                班级,
                性别
            FROM
                enrollment
        """)
        results = db.session.execute(sql_query)

        # 遍历查询结果，为每个学生创建或更新记录
        for row in results:
            student_id, name, major, class_id, gender = row
            # 检查学生是否已存在
            existing_student = Student.query.filter_by(student_id=student_id).first()
            if not existing_student:
                # 学生不存在，创建新记录
                new_student = Student(
                    student_id=student_id,
                    name=name,
                    major=major,
                    class_id=class_id,
                    gender=gender
                )
                # 设置一个默认密码，实际应用中应该让用户自己设置或生成随机密码
                default_password = 'default_password'
                # 设置默认密码或生成随机密码
                new_student.set_password(default_password)
                db.session.add(new_student)

        # 提交所有新记录到数据库
        db.session.commit()


class KnowledgePoint(db.Model):
    __tablename__ = 'knowledge_point'
    KnowledgeID = db.Column(db.Integer, name='知识点id', primary_key=True)
    KnowledgeName = db.Column(db.String(255), name='知识点名称', unique=True)
    Chapter = db.Column(db.String, name='章节', primary_key=True)
    KnowledgeBelong = db.Column(db.String(255), name='所属课程')


class KnowledgePointEdge(db.Model):
    __tablename__ = 'knowledge_point_edge'
    sourceID = db.Column(db.Integer, name='source', primary_key=True)
    targetID = db.Column(db.Integer, name='target', primary_key=True)
    KnowledgeBelong = db.Column(db.String(255), name='所属课程')
    # 其他字段...


class Enrollment(db.Model):
    __tablename__ = 'enrollment'  # 表名选课表
    class_id = db.Column(db.String(255), name='班级')
    student_id = db.Column(db.String(255), primary_key=True, name='学号')
    name = db.Column(db.String(255), name='姓名')
    course_name = db.Column(db.String(255), name='课程名称')
    grade = db.Column(db.String(255), name='成绩')
    academic_year = db.Column(db.String(255), name='学年')
    semester = db.Column(db.String(255), name='学期')
    student_category = db.Column(db.String(255), name='学生类别')
    college = db.Column(db.String(255), name='学院')
    major = db.Column(db.String(255), name='专业')
    major_direction = db.Column(db.String(255), name='专业方向', nullable=True)
    grade_year = db.Column(db.String(255), name='年级', nullable=True)
    student_tag = db.Column(db.String(255), name='学生标记', nullable=True)
    course_college = db.Column(db.String(255), name='开课学院')
    course_code = db.Column(db.String(255), name='课程代码')
    teaching_class = db.Column(db.String(255), name='教学班')
    instructor = db.Column(db.String(255), name='任课教师')
    credit = db.Column(db.Float, name='学分')
    grade_remark = db.Column(db.String(255), name='成绩备注', nullable=True)
    exam_nature = db.Column(db.String(255), name='考试性质')
    gpa = db.Column(db.Float, name='绩点')
    course_tag = db.Column(db.String(255), name='课程标记', nullable=True)
    course_category = db.Column(db.String(255), name='课程类别')
    course_belonging = db.Column(db.String(255), name='课程归属')
    course_nature = db.Column(db.String(255), name='课程性质')
    assessment_method = db.Column(db.String(255), name='考核方式')
    is_grade_invalid = db.Column(db.String(255), name='是否成绩作废')
    submitter = db.Column(db.String(255), name='提交人')
    submission_time = db.Column(db.DateTime, name='提交时间')
    is_degree_course = db.Column(db.String(255), name='是否学位课程')
    single_class_retake = db.Column(db.String(255), name='单开班重修', nullable=True)
    gender = db.Column(db.String(255), name='性别')
    remark_info = db.Column(db.String(255), name='备注信息', nullable=True)
    credit_point = db.Column(db.Float, name='学分绩点', nullable=True)
    course_type = db.Column(db.String(255), name='开课类型')

    @staticmethod
    def rank_avg_gpa(major, grade):
        sql_query = text("""
               SELECT 
                   学号, 
                   姓名, 
                   专业, 
                   SUM(学分绩点) / SUM(学分) AS 平均学分绩点
               FROM 
                   enrollment
               WHERE 
                   年级 = :grade AND
                   专业 = :major
               GROUP BY 
                   学号, 姓名, 专业
               ORDER BY 
                   平均学分绩点 DESC
           """)
        db_results = db.session.execute(sql_query, {'major': major, 'grade': grade})
        results = list(db_results)

        for i in range(len(results)):
            results[i] = list(results[i])
            results[i].append(i + 1)
        return results

    @staticmethod
    def map_score(score):
        if score == '优':
            return 95
        elif score == '良':
            return 85
        elif score == '中':
            return 75
        elif score == '及格':
            return 65
        elif score == '不及格' or score == '缓考':
            return 0
        else:
            try:
                score = float(score)
                return score
            except ValueError:
                return None

    @staticmethod
    def get_violin_data_roughly(grade_year, course_name_search, major, semester, academic_year, is_exam_course,
                                exam_nature):
        grade_year = '%' + grade_year + '%'
        course_name_search = '%' + course_name_search + '%'
        major = '%' + major + '%'
        semester = '%' + semester + '%'
        academic_year = '%' + academic_year + '%'

        sql_query = text("""
               SELECT 
                   班级,
                   成绩,
                   课程名称
               FROM 
                   enrollment
               WHERE 
                   年级 LIKE :grade_year AND
                   课程名称 LIKE :course_name_search AND
                   专业 LIKE :major AND
                   学期 LIKE :semester AND
                   学年 LIKE :academic_year AND
                   考试性质 LIKE :exam_nature
           """)
        db_results = db.session.execute(sql_query, {
            'grade_year': grade_year,
            'course_name_search': course_name_search,
            'major': major,
            'semester': semester,
            'academic_year': academic_year,
            'exam_nature': exam_nature,
        })

        violin_data = []
        for class_id, grade, course_name in db_results:
            if is_exam_course == '1':
                try:
                    grade = float(grade)
                    violin_data.append({
                        "courseName": course_name,
                        "x": class_id,
                        "y": grade
                    })
                except ValueError:
                    # print('passed')
                    pass
            else:
                mapped_score = Enrollment.map_score(grade)
                if mapped_score is not None:
                    violin_data.append({
                        "courseName": course_name,
                        "x": class_id,
                        "y": mapped_score
                    })

        return violin_data

    @staticmethod
    def get_self_home_data(semester, academic_year, student_id):
        semester = '%' + semester + '%'
        academic_year = '%' + academic_year + '%'
        student_id = student_id

        sql_query = text("""
            SELECT 
                e.课程名称,
                CASE 
                    WHEN e.成绩 = '优秀' THEN 95
                    WHEN e.成绩 = '良好' THEN 85
                    WHEN e.成绩 = '中等' THEN 75
                    WHEN e.成绩 = '及格' THEN 60
                    WHEN e.成绩 = '通过' THEN 100
                    WHEN e.成绩 = '不及格' THEN 0
                    ELSE CAST(e.成绩 AS DECIMAL)
                END AS 个人成绩,
                AVG(
                    CASE 
                        WHEN e2.成绩 = '优秀' THEN 95
                        WHEN e2.成绩 = '良好' THEN 85
                        WHEN e2.成绩 = '中等' THEN 75
                        WHEN e2.成绩 = '及格' THEN 60
                        WHEN e2.成绩 = '通过' THEN 100
                        WHEN e2.成绩 = '不及格' THEN 0
                        ELSE CAST(e2.成绩 AS DECIMAL)
                    END
                ) AS 班级平均成绩,
                AVG(
                    CASE 
                        WHEN e3.成绩 = '优秀' THEN 95
                        WHEN e3.成绩 = '良好' THEN 85
                        WHEN e3.成绩 = '中等' THEN 75
                        WHEN e3.成绩 = '及格' THEN 60
                        WHEN e3.成绩 = '通过' THEN 100
                        WHEN e3.成绩 = '不及格' THEN 0
                        ELSE CAST(e3.成绩 AS DECIMAL)
                    END
                ) AS 专业平均成绩
            FROM 
                enrollment e
            LEFT JOIN 
                enrollment e2 ON e.课程名称 = e2.课程名称 AND e.班级 = e2.班级
            LEFT JOIN
                enrollment e3 ON e.课程名称 = e3.课程名称 AND e.专业 = e3.专业
            WHERE 
                e.学期 LIKE :semester AND
                e.学年 LIKE :academic_year AND
                e.学号 LIKE :student_id
            GROUP BY
                e.课程名称, e.成绩
        """)
        db_results = db.session.execute(sql_query, {
            'semester': semester,
            'academic_year': academic_year,
            'student_id': student_id,
        })

        radar_data = []
        line_data = []
        for subject, personal_score, class_avg_score, major_avg_score in db_results:
            if personal_score is not None:
                radar_data.append({
                    "subject": subject,
                    "type": "个人",
                    "score": float(personal_score)
                })
                line_data.append({
                    "subject": subject,
                    "个人分数": float(personal_score),
                    "班级平均分": float(class_avg_score) if class_avg_score else None,
                    "专业平均分": float(major_avg_score) if major_avg_score else None
                })
            if class_avg_score is not None:
                radar_data.append({
                    "subject": subject,
                    "type": "班级平均",
                    "score": float(class_avg_score)
                })

        return {"radarData": radar_data, "lineData": line_data}