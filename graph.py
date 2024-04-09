import pandas as pd
import pysnowflake
from database import db
from models import KnowledgePointEdge, KnowledgePoint


# 定义一个有向图类
class DiGraph:
    # 初始化一个空的有向图
    def __init__(self, lesson_name):
        self.nodes = set()  # 存储所有的点
        self.edges = dict()  # 存储每个点的出边，用一个字典表示，键是点，值是一个集合，存储该点的所有邻居
        self.in_edges = dict()  # 存储每个点的入边，用一个字典表示，键是点，值是一个集合，存储所有指向该点的点
        self.name = dict()  # 存储每个点的中文名字，用一个字典表示，键是点，值是一个字符串
        # self.current_id = 0  # 存储当前的id值，用一个整数表示，初始值为0
        self.lessonName = lesson_name  # 表明这个有向图从属于哪个课程

    # 添加一个点
    def add_node(self, name):
        self.current_id += 1  # 把当前的id值加一
        node = self.current_id  # 把当前的id值赋值给顶点
        self.nodes.add(node)  # 把点加入到点集合中
        self.edges[node] = set()  # 初始化该点的出边集合为空
        self.in_edges[node] = set()  # 初始化该点的入边集合为空
        self.name[node] = name  # 给该点赋值name属性

    # 添加一条边
    def add_edge(self, u, v):
        self.edges[u].add(v)  # 把v加入到u的出边集合中
        self.in_edges[v].add(u)  # 把u加入到v的入边集合中

    # 返回所有的点
    def get_nodes(self):
        return self.nodes

    # 返回所有的边，用一个元组列表表示
    def get_edges(self):
        edges = []
        for u in self.edges:
            for v in self.edges[u]:
                edges.append((u, v))
        return edges

    # 返回一个点的出度
    def out_degree(self, node):
        return len(self.edges[node])

    # 返回一个点的入度
    def in_degree(self, node):
        return len(self.in_edges[node])

    # 返回一个点的所有邻居，用一个集合表示
    def neighbors(self, node):
        return self.edges[node]

    # 返回一个点的所有前驱节点，用一个集合表示
    def predecessors(self, node):
        return self.in_edges[node]

    # 定义一个根据名称找id的方法
    def get_id_by_name(self, name):
        # 判断给定的名称是否在图中
        if name in self.name.values():
            # 如果在图中，就遍历name属性的字典，找到该名称对应的id
            for id, n in self.name.items():
                if n == name:
                    return id
        else:
            # 如果不在图中，就返回一个提示信息
            return "No such name in the graph."

    def save_to_database(self):
        with db.session.no_autoflush:
            for node in self.nodes:
                name = self.name[node]
                course = self.lessonName
                knowledge_point = KnowledgePoint.query.filter_by(KnowledgeName=name, KnowledgeBelong=course).first()
                if not knowledge_point:
                    knowledge_point = KnowledgePoint(KnowledgeName=name, KnowledgeBelong=course)
                    db.session.add(knowledge_point)
            db.session.flush()

            for source, target in self.get_edges():
                source_name = self.name[source]
                target_name = self.name[target]
                source_course = self.lessonName
                target_course = self.lessonName
                source_kp = KnowledgePoint.query.filter_by(KnowledgeName=source_name,
                                                           KnowledgeBelong=source_course).first()
                target_kp = KnowledgePoint.query.filter_by(KnowledgeName=target_name,
                                                           KnowledgeBelong=target_course).first()
                if source_kp and target_kp:
                    edge = KnowledgePointEdge(sourceID=source_kp.KnowledgeID, targetID=target_kp.KnowledgeID,
                                              KnowledgeBelong=self.lessonName)
                    db.session.add(edge)

        db.session.commit()

    # 利用pandas读取excel表格
    def read_from_excel(self, file_name):
        # 读取Excel文件
        df = pd.read_excel(file_name)

        # 初始化雪花ID生成器
        snowflake_generator = pysnowflake.SnowflakeGenerator()

        # 检查知识点列是否存在
        if '一级知识点' in df.columns:
            KlgPtL1 = df['一级知识点'].tolist()  # 获取一级知识点的列表
            # 创建一个字典,用来存储每个中文名字对应的id
            name_to_id = dict()
            # 遍历每个一级知识点
            for k in KlgPtL1:
                # 生成一个雪花ID
                id = snowflake_generator.get_guid()
                # 添加一个新的顶点,并给它赋值name属性
                self.add_node(k, id)
                # 把该顶点的中文名字和id存入字典中
                name_to_id[k] = id
                # 获取该知识点的前驱知识点的列名
                pre_cols = [f'前驱知识点{i}' for i in range(1, 4)]
                # 遍历每个前驱知识点的列名
                for col in pre_cols:
                    # 如果该列存在
                    if col in df.columns:
                        # 获取该列对应的一级知识点的前驱知识点
                        pre_k = df.loc[df['一级知识点'] == k, col].values[0]
                        # 如果前驱知识点不为空
                        if not pd.isnull(pre_k) and pre_k != " ":
                            # 如果前驱知识点不在字典中,就添加它
                            if pre_k not in name_to_id:
                                # 生成一个雪花ID
                                pre_id = snowflake_generator.get_guid()
                                self.add_node(pre_k, pre_id)
                                # 把前驱知识点的中文名字和id存入字典中
                                name_to_id[pre_k] = pre_id
                            else:
                                # 如果前驱知识点已经在字典中,就直接获取它的id
                                pre_id = name_to_id[pre_k]
                            # 添加一条从前驱知识点到一级知识点的边
                            self.add_edge(pre_id, id)
                # 获取该知识点所包含的二级知识点的列名
                sub_cols = [f'二级知识点{i}' for i in range(1, 6)]
                # 遍历每个二级知识点的列名
                for col in sub_cols:
                    # 如果该列存在
                    if col in df.columns:
                        # 获取该列对应的一级知识点所包含的二级知识点
                        sub_k = df.loc[df['一级知识点'] == k, col].values[0]
                        # 如果二级知识点不为空
                        if not pd.isnull(sub_k) and sub_k != " ":
                            # 如果二级知识点不在字典中,就添加它
                            if sub_k not in name_to_id:
                                # 生成一个雪花ID
                                sub_id = snowflake_generator.get_guid()
                                self.add_node(sub_k, sub_id)
                                # 把二级知识点的中文名字和id存入字典中
                                name_to_id[sub_k] = sub_id
                            else:
                                # 如果二级知识点已经在字典中,就直接获取它的id
                                sub_id = name_to_id[sub_k]
                            # 添加一条从二级知识点到一级知识点的边
                            self.add_edge(sub_id, id)
        else:
            print("Error: One or more required columns are missing.")


# 创建一个有向图对象
g = DiGraph("数据结构")
# 实际数据是一个excel，所以还是用函数喵
g.read_from_excel("data/KlgPts.xlsx")
