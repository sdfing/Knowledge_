from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_cors import CORS
from sqlalchemy import text
from database import db
from models import Course, Enrollment, KnowledgePoint, KnowledgePointEdge, User, Student,StagePreYear
from graph import g
from api import api_blueprint
from api import socketio
from regression import  api_reg
from dotenv import load_dotenv
import os


# 迫真主函数，来自c++的恶臭编程习惯，主启动部分要写的都写在这，免得东一块西一块
########################################################################

# 加载环境变量（优先从 .env 文件加载）
load_dotenv()

# 创建 Flask 应用实例
def create_app():
    app = Flask(__name__, template_folder='./static/templates')

    # --------------------------
    # 应用配置
    # --------------------------
    # 从环境变量读取敏感配置
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'default_fallback_key'),  # 优先使用环境变量
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL'),  # 例如：mysql://user:password@localhost/dbname
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_MAX_OVERFLOW=int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 100000)),
        # SESSION_COOKIE_SECURE=True,  # 生产环境强制 HTTPS
        # JSON_SORT_KEYS=False  # 保持 JSON 响应顺序
    )

    # --------------------------
    # 注册扩展
    # --------------------------
    db.init_app(app)
    socketio.init_app(app)  # 绑定 Socket.IO 到 app

    # --------------------------
    # 路由和蓝图
    # --------------------------

    # 注册 API 蓝图
    app.register_blueprint(api_blueprint)
    app.register_blueprint(api_reg)

    # 添加 CORS 配置（可根据需要细化）
    CORS(app)


    return app

# --------------------------
# 应用实例化
# --------------------------
app = create_app()

##############################################################################

# 登录处理
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'})


# 注册处理
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'message': 'Username already exists'})

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Registration successful'})


# 注销处理
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': 'Logout successful'})


# 检查登录状态
@app.route('/check_login', methods=['GET'])
def check_login():
    if 'user_id' in session:
        return jsonify({'isLoggedIn': True})
    else:
        return jsonify({'isLoggedIn': False})


# 其他路由处理...
@app.route('/')
def default():
    # # g.save_to_database()
    # from dataTrans import dodododo
    # dodododo('22总表_updated','2023-2024')

    # Course.extract_and_save_course_info()
    # g.save_to_database()
    # Student.extract_and_save_student_info()
    # 假设从数据库获取的数据如下
    # violin_data = Enrollment.get_violin_data_roughly('2021', '英语%')
    # from dataTrans import plot_violin
    # # 调用绘图函数
    # plot_violin(violin_data)

    # StagePreYear.update_stage_pre_year_from_excel("data/scoring.xlsx",'2023-2024')

    # Enrollment.calculate_credit_points(213401040113,"data/233.xlsx")

    return "all done all clear"



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





# 如果这个文件是主程序，就运行flask应用
if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app)
