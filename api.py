from flask import Blueprint, jsonify, request
from models import Student, Enrollment
from database import db

api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/api/student-gender-distribution')
def get_student_gender_distribution():
    # 查询学生性别分布数据
    gender_distribution = db.session.query(
        Student.gender,
        db.func.count(Student.student_id)
    ).group_by(Student.gender).all()

    # 将查询结果转换为字典格式
    data = {gender: count for gender, count in gender_distribution}

    return jsonify(data)


@api_blueprint.route('/api/violinData', methods=['GET'])
def get_violin_data():
    grade_year = request.args.get('grade', '%')
    course_name = request.args.get('courseName', '%')
    major = request.args.get('major', '%')
    semester = request.args.get('semester', '%')
    academic_year = request.args.get('academicYear', '%')
    is_exam_course = request.args.get('isExamCourse', '0')
    exam_nature = request.args.get('onlyNeedNormalExam', '%')
    if (exam_nature == '0'):
        exam_nature = '%'
    elif (exam_nature == '1'):
        exam_nature = '正常考试'
    data = Enrollment.get_violin_data_roughly(grade_year, course_name, major, semester, academic_year, is_exam_course,
                                              exam_nature)
    # print(is_exam_course)
    # print(data)
    return jsonify(data)


@api_blueprint.route('/api/selfHome', methods=['GET'])
def get_selfhome():
    semester = request.args.get('semester', '%')
    academic_year = request.args.get('academicYear', '%')
    student_id = request.args.get('studentId', '%')
    radar_data = Enrollment.get_self_home_data(semester, academic_year, student_id)
    print(radar_data)
    return jsonify(radar_data)
