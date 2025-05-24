from flask import Blueprint, jsonify, request
from models import Student, Enrollment
from database import db
import os
from qianfan import Qianfan
import threading
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask import current_app
from sqlalchemy import text

api_blueprint = Blueprint('api', __name__)
cors = CORS(api_blueprint)
socketio = SocketIO(async_handlers=True,pingTimeout=900,cors_allowed_origins="*")


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





@api_blueprint.route('/api/rank', methods=['GET'])
def get_rank():
    major = request.args.get('major')
    grade = request.args.get('grade')
    if not major or not grade:
        return jsonify({"error": "Please provide both major and grade"}), 400
    results = Enrollment.rank_avg_gpa(major, grade)
    print(results)
    return jsonify({"data": results})


@api_blueprint.route('/api/violinDataValueAdded', methods=['GET'])
def get_violin_dataVA():
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
    data = Enrollment.get_violin_data_value_added(grade_year, course_name, major, semester, academic_year,
                                                  is_exam_course,
                                                  exam_nature)
    return jsonify(data)


@api_blueprint.route('/api/selfHomeValueAdded', methods=['GET'])
def get_selfhomeVA():
    semester = request.args.get('semester', '%')
    academic_year = request.args.get('academicYear', '%')
    student_id = request.args.get('studentId', '%')
    data = Enrollment.get_self_home_data_value_added(student_id)
    print(data)
    # 启动一个新的线程来异步生成LLM建议
    thread = threading.Thread(target=generate_llm_suggestion_value_added, args=(data, student_id))
    thread.start()

    return jsonify(data)


@api_blueprint.route('/api/courseAnalysis', methods=['GET'])
def get_course_dataBubbles():
    class_id = request.args.get('className', '%')
    course_name = request.args.get('courseName', '%')
    chapter = request.args.get('chapterName', '%')
    bubble_data = Enrollment.get_bubble_data(class_id, course_name, chapter)

    # 启动一个新的线程来异步生成LLM建议
    thread = threading.Thread(target=generate_llm_suggestion_course_analysis,
                              args=(bubble_data, class_id, course_name, chapter))
    thread.start()

    return jsonify(bubble_data)


#
# from flask import jsonify
# from sqlalchemy import text
# from sklearn.linear_model import LinearRegression
#
#
# @api_blueprint.route('/api/value_added_assessment', methods=['GET'])
# def value_added_assessment():
#     sql_query = text("""
#         SELECT
#             e.学号 AS student_id,
#             e.学年 AS academic_year,
#             e.学期 AS semester,
#             CASE
#                 WHEN e.成绩 = '优秀' THEN 95
#                 WHEN e.成绩 = '良好' THEN 85
#                 WHEN e.成绩 = '中等' THEN 75
#                 WHEN e.成绩 = '及格' THEN 60
#                 WHEN e.成绩 = '通过' THEN 100
#                 WHEN e.成绩 = '不及格' THEN 0
#                 ELSE CAST(e.成绩 AS DECIMAL)
#             END AS gpa
#         FROM
#             enrollment e
#         ORDER BY
#             e.学号, e.学年, e.学期
#     """)
#     db_results = db.session.execute(sql_query)
#
#     # 将数据按照学生分组
#     student_data = {}
#     for row in db_results:
#         student_id = row[0]  # 使用整数索引访问列
#         if student_id not in student_data:
#             student_data[student_id] = []
#         student_data[student_id].append({
#             'student_id': row[0],
#             'academic_year': row[1],
#             'semester': row[2],
#             'gpa': row[3]
#         })
#
#     # 计算每个学生的增值评价
#     value_added_data = []
#     for student_id, enrollments in student_data.items():
#         if len(enrollments) > 1:
#             # 提取学期和GPA数据
#             semesters = []
#             gpas = []
#             for i, enrollment in enumerate(enrollments):
#                 semesters.append(i)
#                 gpas.append(enrollment['gpa'])
#
#             # 使用线性回归模型进行增值评价
#             model = LinearRegression()
#             model.fit([[semester] for semester in semesters], gpas)
#             value_added = model.coef_[0]
#
#             value_added_data.append({
#                 'student_id': student_id,
#                 'value_added': value_added
#             })
#     print(value_added_data)
#     return jsonify(value_added_data)
#
#     # 将数据按照学生分组
#     student_data = {}
#     for row in db_results:
#         student_id = row['student_id']
#         if student_id not in student_data:
#             student_data[student_id] = []
#         student_data[student_id].append(dict(row))
#
#     # 计算每个学生的增值评价
#     value_added_data = []
#     for student_id, enrollments in student_data.items():
#         if len(enrollments) > 1:
#             # 提取学期和GPA数据
#             semesters = []
#             gpas = []
#             for i, enrollment in enumerate(enrollments):
#                 semesters.append(i)
#                 gpas.append(enrollment['gpa'])
#
#             # 使用线性回归模型进行增值评价
#             model = LinearRegression()
#             model.fit([[semester] for semester in semesters], gpas)
#             value_added = model.coef_[0]
#
#             value_added_data.append({
#                 'student_id': student_id,
#                 'value_added': value_added
#             })
#
#     return jsonify(value_added_data)



####################################
###
#
# 以下是个人主页部分相关代码
#
###
#####################################
@api_blueprint.route('/api/selfHome', methods=['GET'])
def get_selfhome():
    semester = request.args.get('semester', '%')
    academic_year = request.args.get('academicYear', '%')
    student_id = request.args.get('studentId', '%')
    home_data = Enrollment.get_self_home_data(semester, academic_year, student_id)
    # print(home_data)
    radar_data=home_data['radarData'];
    # 获取真实应用对象
    app = current_app._get_current_object()

    # 传递应用对象到线程
    thread = threading.Thread(
        target=generate_llm_suggestion_self,
        args=(app, radar_data, student_id)
    )
    thread.start()

    return jsonify(home_data)


def generate_llm_suggestion_self(app, radar_data, student_id):
    """
    流式生成学习建议的核心函数
    参数：
    - app: Flask应用实例
    - radar_data: 雷达图数据列表
    - student_id: 学生ID
    """
    with app.app_context():  # 确保应用上下文
        try:
            # ===================== 数据准备阶段 =====================
            # 初始化成绩字典
            personal_scores = {}
            class_avg_scores = {}

            # 遍历原始数据构建字典
            for data_point in radar_data:
                subject = data_point['subject']
                if data_point['type'] == '个人':
                    personal_scores[subject] = data_point['score']
                elif data_point['type'] == '班级平均':
                    class_avg_scores[subject] = data_point['score']

            # 识别薄弱科目（分数低于班级平均）
            weak_subjects = [
                subject for subject in personal_scores
                if subject in class_avg_scores
                   and personal_scores[subject] < class_avg_scores[subject]
            ]

            # ==================== 提示词工程阶段 ====================
            prompt_template = f"""
            【学生学业分析请求】
            学生标识：{student_id}
            成绩概况：
            - 个人成绩：{ {k: f"{v:.1f}分" for k, v in personal_scores.items()} }
            - 班级平均：{ {k: f"{v:.1f}分" for k, v in class_avg_scores.items()} }
            - 低于班级平均的科目：{weak_subjects if weak_subjects else "无"}

            请以智能助教「智评君」的身份：
            1. 用★符号开头进行自我介绍
            2. 分科目给出具体个性化学习建议
            3. 对{len(weak_subjects)}门薄弱科目进行重点分析
            4. 最后给出总体学习策略
            要求：
            - 使用口语化中文
            - 避免专业术语
            - 总字数控制在600字左右
            - 使用自然段分隔不同内容
            """

            # ==================== 流式通信阶段 ====================
            # 发送分析开始事件
            socketio.emit('llm_start', {
                'studentId': student_id,
                'weakSubjects': weak_subjects
            })

            # 带重试机制的流式调用
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    stream = call_qianfan_llm_api_stream(prompt_template)
                    buffer = ""  # 合并短句的缓冲区
                    # for partial_result in stream:
                    #     print(partial_result, end="", flush=True)
                    # 处理流式响应
                    for chunk in stream:
                        if chunk:
                            buffer += chunk

                            # 当缓冲区达到阈值或遇到句末符号时发送
                            if len(buffer) >= 10 or chunk in ('。', '！', '？', '\n'):
                                socketio.emit('llm_chunk', {
                                    'studentId': student_id,
                                    'content': buffer.strip()
                                })
                                buffer = ""

                    # 发送结束标记
                    socketio.emit('llm_end', {'studentId': student_id})
                    return  # 正常退出

                except Exception as api_error:
                    current_app.logger.error(f"API调用异常（第{attempt + 1}次尝试）: {str(api_error)}")
                    if attempt == max_retries - 1:
                        raise RuntimeError("API服务不可用") from api_error

        except Exception as global_error:
            # ==================== 错误处理阶段 ====================
            error_message = f"全局异常: {str(global_error)}"
            current_app.logger.error(error_message)

            # 发送错误通知
            socketio.emit('llm_error', {
                'studentId': student_id,
                'error': "建议生成失败，请稍后刷新重试"
            })


def call_qianfan_llm_api_stream(prompt):
    """千帆大模型流式调用"""
    # 获取当前应用配置
    app = current_app._get_current_object()

    from qianfan import Qianfan
    client = Qianfan(
        api_key=os.getenv('QIANFAN_API')
    )
    # print(prompt)

    stream = client.chat.completions.create(
        model="ernie-3.5-8k",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature=0.3,
        top_p=0.8,
        penalty_score=1.2,
        max_tokens=500
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content.replace("\n", " ")  # 处理换行符

###########################################################################################
#个人主页部分结束
############################################################################################






# def generate_llm_suggestion_self(radar_data, student_id):
#     # print(radar_data,student_id);
#     # 提取个人成绩和班级平均成绩
#     personal_scores = {data['subject']: data['score'] for data in radar_data['radarData'] if data['type'] == '个人'}
#     class_avg_scores = {data['subject']: data['score'] for data in radar_data['radarData'] if
#                         data['type'] == '班级平均'}
#
#     # 找出个人成绩低于班级平均成绩的科目
#     low_score_subjects = [subject for subject in personal_scores if
#                           personal_scores[subject] < class_avg_scores[subject]]
#
#     # 生成提示信息
#     prompt = f"学生ID: {student_id}\n\n"
#     prompt += "个人成绩:\n"
#     for subject, score in personal_scores.items():
#         prompt += f"{subject}: {score}\n"
#     prompt += "\n班级平均成绩:\n"
#     for subject, score in class_avg_scores.items():
#         prompt += f"{subject}: {score}\n"
#     prompt += "\n个人成绩低于班级平均成绩的科目:\n"
#     for subject in low_score_subjects:
#         prompt += f"{subject}\n"
#     prompt += "\n现在你的名字叫智评君,你是一个智能学生学习情况分析机器人，这是该学生的学习情况，现在请你先介绍自己，再为该学生提供每门课程的学习建议和改进方向，可以稍微简短"
#     print(prompt)
#     # 调用千帆平台的LLM API生成建议
#     suggestion = call_qianfan_llm_api(prompt)
#     print(suggestion)
#     # # 使用Flask-SocketIO发送建议给前端
#     socketio.emit('llm_suggestion', {'studentId': student_id, 'suggestion': suggestion})


def generate_llm_suggestion_value_added(radar_data, student_id):
    # 提取个人增值评价数据
    value_added_scores = radar_data['radarData']
    print(value_added_scores)
    # 生成提示信息
    prompt = f"学生ID: {student_id}\n\n"
    prompt += "个人增值评价:\n"
    for it in value_added_scores:
        prompt += f"{it['subject']}: {it['score']},学期：{it['type']}\n"
    prompt += ("\n现在你的名字叫智评君,你是一个智能学生学习情况分析机器人,这是该学生的增值评价情况,增值评价是与传统的成绩评价不同,"
               "增值评价关注的是学生在一段时间内的进步和成长。通过跟踪学生的学习轨迹和能力变化,你需要生成个性化的增值报告,鼓励每一位学生不断挑战"
               "自我、超越自我。现在请你先介绍自己,再为该学生提供增值评价报告，可以稍微简短。")

    print(prompt)
    # 调用千帆平台的LLM API生成建议
    suggestion = call_qianfan_llm_api(prompt)
    print(suggestion)

    # 使用Flask-SocketIO发送建议给前端
    socketio.emit('llm_suggestion_value_added', {'studentId': student_id, 'suggestion': suggestion})




def generate_llm_suggestion_course_analysis(bubble_data, class_id, course_name, chapter):
    # 生成提示信息
    prompt = f"班级ID: {class_id}\n课程名称: {course_name}\n章节: {chapter}\n\n"
    prompt += "课程分析数据:\n"
    for data in bubble_data:
        prompt += f"学生ID: {data['student_id']}, 得分: {data['score']}\n"
    prompt += "\n现在你的名字叫智评君,你是一个智能学生学习情况分析机器人,这是该班级的课程分析情况。现在请你先介绍自己,再为该班级提供这门课程的学习建议和改进方向,可以稍微简短。"

    # 调用千帆平台的LLM API生成建议
    suggestion = call_qianfan_llm_api(prompt)

    # 使用Flask-SocketIO发送建议给前端
    socketio.emit('llm_suggestion_course_analysis',
                  {'classId': class_id, 'courseName': course_name, 'chapter': chapter, 'suggestion': suggestion})










def call_qianfan_llm_api(data):
    """
    流式调用千帆大模型的生成函数
    返回生成器对象，通过迭代获取实时响应
    """
    # print("good");

    client = Qianfan(
        api_key=os.getenv('QIANFAN_API')
        # app_id="", # 选填，不填写则使用默认appid
        # todo：建议使用环境变量配置密钥，而非硬编码
    )

    # 创建流式响应
    stream = client.chat.completions.create(
        model="ernie-3.5-8k",
        messages=[{
            "role": "user",
            "content": data
        }],
        stream=True,
        temperature=0.6,
        top_p=0.8
    )
    # 实时返回结果
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:  # 过滤空内容
            yield content
    # try:

    # except Exception as e:
    #     logging.error(f"API调用失败: {str(e)}")
    #     yield "[服务暂时不可用，请稍后重试]"


# def call_qianfan_llm_api(data):
#     os.environ["QIANFAN_ACCESS_KEY"] = "0d43ce87f940491da3d43d811fb543c3"
#     os.environ["QIANFAN_SECRET_KEY"] = "f8668e7fb7be409d8a8d47d1a79a6f35"
#     chat_comp = qianfan.ChatCompletion()
#     # 调用默认模型，ERNIE-Lite-8K-0922（即ERNIE-Bot-turbo）
#     resp = chat_comp.do(model="ERNIE-4.0-8K", messages=[{
#         "role": "user",
#         "content": data
#     }])
#     # print(resp)
#     return resp['result']

@api_blueprint.route('/api/llmApi')
def get_llm_api():
    # 模拟前端调用

    response_stream = call_qianfan_llm_api("如何学习人工智能？")
    # 实时处理响应
    for partial_result in response_stream:
        print(partial_result, end="", flush=True)
    return response_stream





############################################################
#
#   以下是知识图谱部分
#
############################################################
from models import KnowledgePointEdge,KnowledgePoint
from flask import jsonify,render_template
@api_blueprint.route('/graphReturnInfo')
def graphReturnInfo():
    course_name = request.args.get('course', '')
    year = request.args.get('year', '')  # 从请求参数中获取年份
    # print("接收到前端发送的课程名称"+course_name)

    # 根据课程名称和年份获取阶段信息
    query = text("SELECT DISTINCT spy.阶段 "
                 "FROM stage_pre_year spy "
                 "JOIN knowledge_point kp ON spy.知识点ID = kp.知识点ID "
                 "WHERE kp.所属课程 = :course_name "
                 "AND spy.年份 = :year "
                 "ORDER BY spy.阶段")
    result = db.session.execute(query, {'course_name': course_name, 'year': year})
    stages = [row[0] for row in result]
    print(stages)
    return jsonify(stages)
@api_blueprint.route('/graph')
def graph():
    course_name = request.args.get('course', '%')
    student_id = request.args.get('student', '')
    selected_chapter = request.args.get('chapter', '%')
    # print(course_name,student_id,selected_chapter)

    # 获取知识点图数据
    knowledge_points_data = get_knowledge_points_data(course_name)

    # 获取学生知识点数据
    student_knowledge_data = get_student_knowledge_data(student_id, selected_chapter)

    # print(course_name,student_id,selected_chapter,knowledge_points_data,student_knowledge_data)

    return render_template('graph.html', knowledge_points=knowledge_points_data,
                           student_knowledge=student_knowledge_data)
def get_knowledge_points_data(course_name):
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
    return elements

def get_student_knowledge_data(student_id, selected_stage):
    print(selected_stage)
    query = text("""
        SELECT kp.知识点id, kp.知识点名称, sk.分数
        FROM student s
        JOIN student_knowledge sk ON s.学号 = sk.学号
        JOIN knowledge_point kp ON sk.知识点id = kp.知识点id
        JOIN stage_pre_year spy ON kp.知识点id = spy.知识点id
        WHERE s.学号 = :student_id AND spy.阶段 <= :selected_stage
        ORDER BY spy.阶段;
    """)
    result = db.session.execute(query, {'student_id': student_id, 'selected_stage': selected_stage})
    result_list = []
    # print(result_list)
    for row in result:
        tmp = dict()
        tmp['id'] = str(row[0])
        tmp['名称'] = row[1]
        tmp['分数'] = row[2]
        result_list.append(tmp)
    return result_list





# @api_blueprint.route('/graphCourseInfo')
# def graphCourseInfo():
#     course_name = request.args.get('course', '')
#     print(course_name)
#
#     # 根据课程名称获取章节信息
#     query = text("SELECT DISTINCT 章节 FROM knowledge_point WHERE 所属课程 = :course_name")
#     result = db.session.execute(query, {'course_name': course_name})
#     chapters = [row[0] for row in result]
#     print(chapters)
#     return jsonify(chapters)
#
#
# @api_blueprint.route('/graph')
# def graph():
#     course_name = request.args.get('course', '')
#     student_id = request.args.get('student', '')
#     selected_chapter = request.args.get('chapter', '')
#
#     # 根据课程名称获取章节信息
#     query = text("SELECT DISTINCT 章节 FROM knowledge_point WHERE 知识点名称 = :course_name")
#     result = db.session.execute(query, {'course_name': course_name})
#     chapters = [row[0] for row in result]
#
#     if not selected_chapter:
#         # 如果没有选择章节,返回章节信息给前端
#         return jsonify(chapters)
#     else:
#         # 如果选择了章节,进行下一步操作
#
#         return render_template('graph.html', course_name=course_name, student_id=student_id,
#                                selected_chapter=selected_chapter, knowledge_points=knowledge_points)
#
#
# @api_blueprint.route('/graphInfo/<course_id>')
# def graphInfo(course_id):
#     course_name = course_id  # 假设你想查询"数据结构"课程的知识点图
#     print("thisiscoursename" + course_name)
#     # 查询所有知识点
#     knowledge_points = KnowledgePoint.query.filter_by(KnowledgeBelong=course_name).all()
#     # 构建节点数据
#     nodes = []
#     for kp in knowledge_points:
#         node = {
#             'data': {
#                 'id': str(kp.KnowledgeID),
#                 'name': kp.KnowledgeName
#             }
#         }
#         nodes.append(node)
#     # 查询所有知识点边
#     knowledge_point_edges = KnowledgePointEdge.query.filter_by(KnowledgeBelong=course_name).all()
#     # 构建边数据
#     edges = []
#     for edge in knowledge_point_edges:
#         edge_data = {
#             'data': {
#                 'source': str(edge.sourceID),
#                 'target': str(edge.targetID)
#             }
#         }
#         edges.append(edge_data)
#     # 将节点和边数据合并
#     elements = nodes + edges
#     # 返回 JSON 格式的数据
#     print(elements)
#     return jsonify(elements)
#
#
# @api_blueprint.route('/get_student_knowledge/<student_id>', methods=['GET'])
# def get_student_scores(student_id):
#     query = text("""
#         SELECT  kp.知识点id, kp.知识点名称, sk.分数
#         FROM student s
#         JOIN student_knowledge sk ON s.学号 = sk.学号
#         JOIN knowledge_point kp ON sk.知识点id = kp.知识点id
#         WHERE s.学号 = :student_id;
#     """)
#     result = db.session.execute(query, {'student_id': student_id})
#     result_list = []
#     print(result_list)
#     for row in result:
#         tmp = dict()
#         tmp['id'] = str(row[0])
#         tmp['名称'] = row[1]
#         tmp['分数'] = row[2]
#         result_list.append(tmp)
#     # 返回JSON数据
#     return jsonify(result_list)
