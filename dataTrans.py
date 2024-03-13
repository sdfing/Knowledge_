import pandas as pd



def trans(name):
    # 读取Excel文件
    df = pd.read_excel(name)

    # 将数据转为UTF-8编码的CSV文件
    df.to_csv(name+'.csv', encoding='utf-8', index=False)
    pass
    pass