# 导入flask库
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

# 导入定义的有向图类
from graph import DiGraph


# 迫真主函数，来自c++的恶臭编程习惯，主启动部分要写的都写在这，免得东一块西一块
########################################################################
# 创建一个flask应用对象
app = Flask(__name__, template_folder='./static/templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Asd12345@127.0.0.1:3306/aaa'
db = SQLAlchemy(app)

lesson_set = ('数据结构', '高等数学', '程序设计基础')  # 一共有多少课程，To Do:后续可以将此处数据库化，通过管理员用户动态添加课程
graph_set = set()  # 知识图谱们
for ls in lesson_set:
    g = DiGraph(ls)
    g.read_from_excel("data/KlgPts.xlsx")  # TO DO:此处后续使用数据库进行优化，并提供动态编辑扩充知识图谱功能

##############################################################################


# 定义一个路由，用于显示网页
@app.route('/graph')
def index():
    return render_template('graph.html')


@app.route('/')
def login():
    return render_template('login.html')


# 定义一个路由，用于返回有向图数据
@app.route('/graphInfo')
def graphInfo():
    # 创建一个有向图对象
    g = DiGraph("数据结构")

    # 假设实际数据是一个列表，每个元素是一个字典，包含一个点的id和它的前驱节点的id列表
    # 可以根据你的数据格式进行修改
    # data = [{'id': 'a', 'predecessors': []}, {'id': 'b', 'predecessors': ['a']}, {'id': 'c', 'predecessors': ['a', 'b']},{'id':'d','predecessors':['c']}]

    # 遍历数据，添加点和边到有向图对象中
    # for node in data:
    #     g.add_node(node['id']) # 添加点
    #     for pred in node['predecessors']:
    #         g.add_edge(pred, node['id']) # 添加边

    # 实际数据是一个excel，所以还是用函数喵
    g.read_from_excel("data/KlgPts.xlsx")

    # 从有向图对象中获取点和边的数据，转换成Cytoscape.js可以识别的格式
    nodes = [{'data': {'id': node, 'name': g.name[node]}} for node in
             g.get_nodes()]  # 把节点数据中的name属性加入到cytoscape的数据中，用来显示中文标签
    edges = [{'data': {'source': edge[0], 'target': edge[1]}} for edge in g.get_edges()]
    elements = nodes + edges

    # 返回你的有向图数据，用一个JSON格式表示
    return jsonify(elements)

# 这个路由的用处是显示所有的课程
@app.route('/lessons')
def lessons():
    from course import Course
    courses = Course.query.all()  # 查询所有的课程
    return render_template('index.html', courses=courses)  # 渲染首页模板，传入课程列表





# 如果这个文件是主程序，就运行flask应用
if __name__ == '__main__':
    app.run(debug=True)
