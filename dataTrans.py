import pandas as pd



def trans(name):
    # 读取Excel文件
    df = pd.read_excel(name)

    # 将数据转为UTF-8编码的CSV文件
    df.to_csv(name+'.csv', encoding='utf-8', index=False)
    pass
    pass


def dodododo(original_data):
    import pandas as pd

    # 假设您的原始数据Excel文件名为'original_data.xlsx'
    # 假设您的知识点Excel文件名为'knowledge_points.xlsx'
    # 假设您的学生知识点Excel文件名为'student_knowledge.xlsx'

    # 读取原始数据
    original_data_df = pd.read_excel(original_data)

    # 读取知识点数据
    knowledge_points_df = pd.read_excel('data/knowledge_points.xlsx')

    # 创建一个空的DataFrame用于存储学生知识点数据
    student_knowledge_df = pd.DataFrame(columns=['学号', '知识点id', '分数'])

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

            # 将提取的数据添加到学生知识点DataFrame中
            student_knowledge_df = pd.concat([student_knowledge_df, scores])

    # 重置索引
    student_knowledge_df.reset_index(drop=True, inplace=True)

    # 将学生知识点数据保存到Excel文件
    student_knowledge_df.to_excel('data/student_knowledge.xlsx', index=False)
    student_knowledge_df.to_csv('data/student_knowledge.xlsx' + '.csv', encoding='utf-8', index=False)

def trytry():
    pass