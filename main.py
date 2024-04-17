# 导入flask库
from flask import Flask, render_template
from flask import redirect, url_for, request
from sqlalchemy import text

from database import db
from models import Course, Enrollment, KnowledgePoint, KnowledgePointEdge
# 有向图结构
from flask import jsonify
from graph import g

# 迫真主函数，来自c++的恶臭编程习惯，主启动部分要写的都写在这，免得东一块西一块
########################################################################
# 创建一个flask应用对象
app = Flask(__name__, template_folder='./static/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Asd12345@127.0.0.1:3306/aaa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


##############################################################################

# 登录登录
@app.route('/')
def default():
    # g.save_to_database()
    # from dataTrans import dodododo
    # dodododo('21总表_updated','2022-2023')

    Course.extract_and_save_course_info()
    return 'all done all fine'


# 知识图谱喵
@app.route('/graph')
def index():
    return render_template('graph.html')


@app.route('/graphInfo/<course_id>')
def graphInfo(course_id):
    course_name = course_id  # 假设你想查询"数据结构"课程的知识点图
    # 查询所有知识点
    knowledge_points = KnowledgePoint.query.filter_by(KnowledgeBelong=course_name).all()
    # 构建节点数据
    nodes = []
    for kp in knowledge_points:
        node = {
            'data': {
                'id': str(kp.KnowledgeID),
                'name': kp.KnowledgeName
            }
        }
        nodes.append(node)
    # 查询所有知识点边
    knowledge_point_edges = KnowledgePointEdge.query.filter_by(KnowledgeBelong=course_name).all()
    # 构建边数据
    edges = []
    for edge in knowledge_point_edges:
        edge_data = {
            'data': {
                'source': str(edge.sourceID),
                'target': str(edge.targetID)
            }
        }
        edges.append(edge_data)
    # 将节点和边数据合并
    elements = nodes + edges
    # 返回 JSON 格式的数据
    return jsonify(elements)


@app.route('/get_student_knowledge/<student_id>', methods=['GET'])
def get_student_scores(student_id):
    query = text("""
        SELECT  kp.知识点id, kp.知识点名称, sk.分数
        FROM student s
        JOIN student_knowledge sk ON s.学号 = sk.学号
        JOIN knowledge_point kp ON sk.知识点id = kp.知识点id
        WHERE s.学号 = :student_id;
    """)
    result = db.session.execute(query, {'student_id': student_id})
    result_list = []
    for row in result:
        tmp = dict()
        tmp['id'] = str(row[0])
        tmp['名称'] = row[1]
        tmp['分数'] = row[2]
        result_list.append(tmp)
    # 返回JSON数据
    return jsonify(result_list)


# 这个路由的用处是显示所有的课程
@app.route('/lessons')
def lessons():
    courses = Course.query.all()  # 查询所有的课程
    return render_template('lessons.html', courses=courses)  # 渲染首页模板，传入课程列表


@app.route('/course/<int:course_id>', methods=['GET', 'POST'])
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)  # 根据课程id查询课程，如果不存在则返回404错误
    if request.method == 'POST':  # 如果是POST请求，说明用户提交了修改表单
        course.name = request.form.get('name')  # 从表单中获取新的课程名
        course.description = request.form.get('description')  # 从表单中获取新的课程描述
        course.teacher = request.form.get('teacher')  # 从表单中获取新的课程教师
        db.session.commit()  # 提交数据库变更
        return redirect(url_for('course_detail', course_id=course.id))  # 重定向到课程详情页面
    return render_template('course_detail.html', course=course)  # 如果是GET请求，渲染课程详情模板，传入课程对象


@app.route('/student/<major>', methods=['GET'])
def get_students_by_major(major):
    enrollments = Enrollment.query.filter_by(major=major).all()
    return render_template('chart.html', enrollments=enrollments)


@app.route('/student/average_gpa/<grade>/<major>', methods=['GET'])
def get_students_average_gpa(major, grade):
    results = Enrollment.rank_avg_gpa(major, grade)
    return render_template('rank_gpa.html', results=results)


@app.route('/student')
def student_main():
    # extract_and_save_student_info()
    pass


# 如果这个文件是主程序，就运行flask应用
if __name__ == '__main__':
    app.run(debug=True)
