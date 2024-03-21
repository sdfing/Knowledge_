# 导入flask库
from flask import Flask, jsonify, render_template
from flask import redirect, url_for, request

from course import Course
from database import db
from enrollment import Enrollment
from graph import g
from studentKnowledge import StudentKnowledge
from students import extract_and_save_student_info
from dataTrans import dodododo

# 迫真主函数，来自c++的恶臭编程习惯，主启动部分要写的都写在这，免得东一块西一块
########################################################################
# 创建一个flask应用对象
app = Flask(__name__, template_folder='./static/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Asd12345@127.0.0.1:3306/aaa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

dodododo()


# from dataTrans import trans
# trans('data/all_2022.xlsx')


# lesson_set = ('数据结构', '高等数学', '程序设计基础')  # 一共有多少课程，To Do:后续可以将此处数据库化，通过管理员用户动态添加课程
# graph_set = set()  # 知识图谱们
# for ls in lesson_set:
#   g = DiGraph(ls)
#   g.read_from_excel("data/KlgPts.xlsx")  # TO DO:此处后续使用数据库进行优化，并提供动态编辑扩充知识图谱功能

##############################################################################

# 登录登录
@app.route('/')
def login():
    return render_template('login.html')


# 知识图谱喵
@app.route('/graph')
def index():
    return render_template('graph.html')


# 有向图结构
@app.route('/graphInfo')
def graphInfo():
    # 假设实际数据是一个列表，每个元素是一个字典，包含一个点的id和它的前驱节点的id列表
    # 可以根据你的数据格式进行修改
    # data = [{'id': 'a', 'predecessors': []}, {'id': 'b', 'predecessors': ['a']}, {'id': 'c', 'predecessors': ['a', 'b']},{'id':'d','predecessors':['c']}]

    # 遍历数据，添加点和边到有向图对象中
    # for node in data:
    #     g.add_node(node['id']) # 添加点
    #     for pred in node['predecessors']:
    #         g.add_edge(pred, node['id']) # 添加边

    # 从有向图对象中获取点和边的数据，转换成Cytoscape.js可以识别的格式
    nodes = [{'data': {'id': node, 'name': g.name[node]}} for node in
             g.get_nodes()]  # 把节点数据中的name属性加入到cytoscape的数据中，用来显示中文标签
    edges = [{'data': {'source': edge[0], 'target': edge[1]}} for edge in g.get_edges()]
    elements = nodes + edges

    # 返回你的有向图数据，用一个JSON格式表示
    return jsonify(elements)


# 每个知识点每人的掌握情况
@app.route('/get_student_knowledge/<student_id>')
def get_student_knowledge(student_id):
    # 查询数据库中对应学生的知识点掌握情况
    knowledge_data = StudentKnowledge.query.filter_by(student_id=student_id).all()
    # 将查询结果转换为字典列表
    print(knowledge_data)
    print()
    print()
    results = [{'knowledge_point': item.knowledge_point, 'score': item.score} for item in knowledge_data]
    # 返回JSON数据
    return jsonify(results)


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


@app.route('/student/average_gpa/<major>', methods=['GET'])
def get_students_average_gpa(major):
    enrollments = Enrollment()
    results = enrollments.rank_avg_gpa(major)
    return render_template('rank_gpa.html', results=results)


@app.route('/student')
def student_main():
    extract_and_save_student_info()


# 如果这个文件是主程序，就运行flask应用
if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()
