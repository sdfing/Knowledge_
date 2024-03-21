from database import db


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

    def rank_avg_gpa(self, major):
        from sqlalchemy import text
        sql_query = text("""
               SELECT 
                   学号, 
                   姓名, 
                   专业, 
                   SUM(学分绩点) / SUM(学分) AS 平均学分绩点
               FROM 
                   enrollment
               WHERE 

                   专业 = :major
               GROUP BY 
                   学号, 姓名, 专业
               ORDER BY 
                   平均学分绩点 DESC
           """)
        db_results = db.session.execute(sql_query, {'major': major})
        results = list(db_results)

        for i in range(len(results)):
            results[i] = list(results[i])
            results[i].append(i + 1)
        return results
