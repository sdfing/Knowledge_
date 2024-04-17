import pandas as pd
from database import db
import matplotlib.pyplot as plt
import seaborn as sns

def plot_violin(violin_data):
    # 将数据转换为 pandas DataFrame
    import pandas as pd
    df = pd.DataFrame(violin_data)

    # 绘制小提琴图
    plt.figure(figsize=(10, 6))
    sns.violinplot(x='classId', y='grade', data=df)

    # 设置图表标题和标签
    plt.title('各班级成绩分布')
    plt.xlabel('班级')
    plt.ylabel('成绩')

    # 显示图表
    plt.show()




def trans(name):
    # 读取Excel文件
    df = pd.read_excel(name)

    # 将数据转为UTF-8编码的CSV文件
    df.to_csv(name + '.csv', encoding='utf-8', index=False)
    pass
    pass


def dodododo(original_data, record_year):
    # 假设您的原始数据Excel文件名为'original_data.xlsx'
    # 假设您的知识点Excel文件名为'knowledge_points.xlsx'
    # 假设您的学生知识点Excel文件名为'student_knowledge.xlsx'
    # 读取原始数据
    original_data_df = pd.read_excel('data/' + original_data + '.xlsx')
    # 读取知识点数据
    knowledge_points_df = pd.read_excel('data/knowledge_point.xlsx')
    # 创建一个空的DataFrame用于存储学生知识点数据
    student_knowledge_df = pd.DataFrame(columns=['学号', '知识点id', '年份', '分数'])
    # 遍历每个知识点
    for index, row in knowledge_points_df.iterrows():
        knowledge_point_id = row['知识点id']
        knowledge_point_name = row['知识点名称']
        # 检查原始数据中是否有该知识点的列
        if knowledge_point_name in original_data_df.columns:
            # 提取该知识点的分数数据
            scores = original_data_df[['学号', knowledge_point_name]].copy()
            scores.rename(columns={knowledge_point_name: '分数'}, inplace=True)
            scores['知识点id'] = knowledge_point_id
            scores['年份'] = record_year  # 添加年份列，并设置为函数参数record_year的值
            # 将提取的数据添加到学生知识点DataFrame中
            student_knowledge_df = pd.concat([student_knowledge_df, scores])
    # 重置索引
    student_knowledge_df.reset_index(drop=True, inplace=True)
    # 将学生知识点数据保存到Excel文件
    # student_knowledge_df.to_excel('data/' + original_data + '_student_knowledge.xlsx', index=False)
    # student_knowledge_df.to_csv('data/' + original_data + '_student_knowledge' + '.csv', encoding='utf-8', index=False)
    # 将数据导入到数据库中的student_knowledge表
    # 如果表不存在，会自动创建；如果表存在，追加数据（请根据需要选择if_exists的值，可以是'append'或'replace'）
    student_knowledge_df.to_sql('student_knowledge', con=db.engine, index=False, if_exists='append')
    pass


def trytry():
    pass
