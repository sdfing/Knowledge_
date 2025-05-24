from flask import Flask, request, jsonify, Blueprint
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from sqlalchemy import text
from database import db
from models import Enrollment  # 确保 Enrollment 模型被正确导入

api_reg = Blueprint('regression', __name__)

# 路径：保存训练好的模型
MODEL_PATH = "regression/elastic_net_model.pkl"
SCALER_PATH = "regression/scaler.pkl"

def get_training_data():
    # 确保SQL使用中文列名且引号正确
    sql = text("""
        SELECT 
            pb.学号,
            pb.grade AS 基础成绩,
            ap.grade AS 高级成绩,
            ds.grade AS 数据结构成绩
        FROM 
            (SELECT 学号, 
                CASE 
                    WHEN 成绩 = '优秀' THEN 95
                    WHEN 成绩 = '良好' THEN 85
                    WHEN 成绩 = '中等' THEN 75
                    WHEN 成绩 = '及格' THEN 60
                    WHEN 成绩 = '通过' THEN 100
                    WHEN 成绩 = '不及格' THEN 0
                    ELSE CAST(成绩 AS DECIMAL) 
                END AS grade
             FROM enrollment
             WHERE 课程名称 = '程序设计基础A' 
               AND 学年 = '2021-2022') pb
        JOIN 
            (SELECT 学号, 
                CASE 
                    WHEN 成绩 = '优秀' THEN 95
                    WHEN 成绩 = '良好' THEN 85
                    WHEN 成绩 = '中等' THEN 75
                    WHEN 成绩 = '及格' THEN 60
                    WHEN 成绩 = '通过' THEN 100
                    WHEN 成绩 = '不及格' THEN 0
                    ELSE CAST(成绩 AS DECIMAL) 
                END AS grade
             FROM enrollment
             WHERE 课程名称 = '高级程序设计A' 
               AND 学年 = '2021-2022') ap
        ON pb.学号 = ap.学号
        JOIN 
            (SELECT 学号, 
                CASE 
                    WHEN 成绩 = '优秀' THEN 95
                    WHEN 成绩 = '良好' THEN 85
                    WHEN 成绩 = '中等' THEN 75
                    WHEN 成绩 = '及格' THEN 60
                    WHEN 成绩 = '通过' THEN 100
                    WHEN 成绩 = '不及格' THEN 0
                    ELSE CAST(成绩 AS DECIMAL) 
                END AS grade
             FROM enrollment
             WHERE 课程名称 = '数据结构与算法' 
               AND 学年 = '2022-2023') ds
        ON pb.学号 = ds.学号
    """)

    # 执行查询
    result = db.session.execute(sql)

    # 正确解析查询结果（关键修正）
    data_rows = []
    for row in result:
        # 将Row对象转为有序字典
        row_dict = row._asdict()  # 使用SQLAlchemy的_asdict方法

        # 提取各字段值（确保中文列名精确匹配）
        processed_row = {
            '学号': str(row_dict['学号']),  # 学号转为字符串
            '基础成绩': float(row_dict['基础成绩']),
            '高级成绩': float(row_dict['高级成绩']),
            '数据结构成绩': float(row_dict['数据结构成绩'])
        }
        data_rows.append(processed_row)

    # 创建DataFrame
    data = pd.DataFrame(
        data_rows,
        columns=['学号', '基础成绩', '高级成绩', '数据结构成绩']
    )

    # 数据清洗
    data = data.dropna(subset=['基础成绩', '高级成绩', '数据结构成绩'])

    # 验证数据
    print("\n[数据验证] 前5条数据:")
    print(data.head())
    print("\n[数据验证] 统计描述:")
    print(data[['基础成绩', '高级成绩', '数据结构成绩']].describe())
    print("\n[数据验证] 相关系数矩阵:")
    print(data.corr(numeric_only=True))

    print("i runed here")

    return data
def get_training_data(target_course='操作系统'):
    """增强版数据获取函数，支持动态课程预测"""
    # 动态生成课程匹配条件
    target_course_condition = f"课程名称 LIKE '{target_course}%%'"  # 匹配操作系统开头的课程

    sql = text(f"""
           SELECT 
               pb.学号,
               pb.grade AS 基础成绩,
               ap.grade AS 高级成绩,
               ds.grade AS 数据结构成绩,
               COALESCE(os.grade, 0) AS 操作系统成绩  -- 处理缺失值
           FROM 
               (SELECT 学号, 
                   CASE 
                       WHEN 成绩 IN ('优秀','良好','中等','及格','通过') 
                           THEN CASE 成绩
                               WHEN '优秀' THEN 95
                               WHEN '良好' THEN 85
                               WHEN '中等' THEN 75
                               WHEN '及格' THEN 60
                               WHEN '通过' THEN 100
                           END
                       WHEN 成绩 = '不及格' THEN 0
                       ELSE CAST(成绩 AS DECIMAL)
                   END AS grade
                FROM enrollment
                WHERE 课程名称 = '程序设计基础A' 
                  AND 学年 = '2021-2022') pb
           JOIN  -- 保留核心课程的内连接
               (SELECT 学号, 
                   CASE 
                       WHEN 成绩 IN ('优秀','良好','中等','及格','通过') 
                           THEN CASE 成绩
                               WHEN '优秀' THEN 95
                               WHEN '良好' THEN 85
                               WHEN '中等' THEN 75
                               WHEN '及格' THEN 60
                               WHEN '通过' THEN 100
                           END
                       WHEN 成绩 = '不及格' THEN 0
                       ELSE CAST(成绩 AS DECIMAL)
                   END AS grade
                FROM enrollment
                WHERE 课程名称 = '高级程序设计A' 
                  AND 学年 = '2021-2022') ap ON pb.学号 = ap.学号
           JOIN 
               (SELECT 学号, 
                   CASE 
                       WHEN 成绩 IN ('优秀','良好','中等','及格','通过') 
                           THEN CASE 成绩
                               WHEN '优秀' THEN 95
                               WHEN '良好' THEN 85
                               WHEN '中等' THEN 75
                               WHEN '及格' THEN 60
                               WHEN '通过' THEN 100
                           END
                       WHEN 成绩 = '不及格' THEN 0
                       ELSE CAST(成绩 AS DECIMAL)
                   END AS grade
                FROM enrollment
                WHERE 课程名称 = '数据结构与算法' 
                  AND 学年 = '2022-2023') ds ON pb.学号 = ds.学号
           LEFT JOIN  -- 关键修改：使用左连接
               (SELECT 学号, 
                   CASE 
                       WHEN 成绩 IN ('优秀','良好','中等','及格','通过') 
                           THEN CASE 成绩
                               WHEN '优秀' THEN 95
                               WHEN '良好' THEN 85
                               WHEN '中等' THEN 75
                               WHEN '及格' THEN 60
                               WHEN '通过' THEN 100
                           END
                       WHEN 成绩 = '不及格' THEN 0
                       ELSE CAST(成绩 AS DECIMAL)
                   END AS grade
                FROM enrollment
                WHERE {target_course_condition}
                  AND 学年 = '2023-2024') os ON pb.学号 = os.学号
       """)


    # 执行查询
    result = db.session.execute(sql)

    # 正确解析查询结果
    data_rows = []
    for row in result:
        row_dict = row._asdict()
        processed_row = {
            '学号': str(row_dict['学号']),
            '基础成绩': float(row_dict['基础成绩']),
            '高级成绩': float(row_dict['高级成绩']),
            '数据结构成绩': float(row_dict['数据结构成绩']),
            target_course+'成绩': float(row_dict[target_course+'成绩'])  # 新增字段
        }
        data_rows.append(processed_row)

    # 创建DataFrame
    data = pd.DataFrame(
        data_rows,
        columns=['学号', '基础成绩', '高级成绩', '数据结构成绩', target_course+'成绩']  # 补充列名
    )

    # 空数据检测
    if data.empty:
        raise ValueError(f"未找到{target_course}相关数据，请检查："
                         f"1.课程名称是否包含'{target_course}'前缀 "
                         f"2.学年设置是否正确")

    # 数据清洗
    initial_count = len(data)
    data = data.dropna(subset=['基础成绩', '高级成绩', '数据结构成绩', target_course+'成绩'])
    print(f"\n[数据清洗] 原始记录数: {initial_count} → 有效记录数: {len(data)}")

    # 验证数据
    print("\n[数据验证] 前5条数据:")
    print(data.head())
    print("\n[数据验证] 统计描述:")
    print(data.describe())
    print("\n[数据验证] 相关系数矩阵:")
    print(data.corr(numeric_only=True))

    return data


def train_model_v3(target_course='操作系统'):
    """添加正确的训练集/测试集划分"""
    # 创建必要目录
    # Path("models").mkdir(exist_ok=True)
    # Path("regression").mkdir(exist_ok=True)

    # 获取数据
    data = get_training_data(target_course)

    # 动态设置特征和目标
    features = ['基础成绩', '高级成绩', '数据结构成绩']
    target = f'{target_course}成绩'

    # --- 数据预处理阶段 ---
    # 1. 成绩分布修正
    for col in features + [target]:
        q75 = data[col].quantile(0.75)
        data[f'{col}_修正'] = np.where(
            data[col] >= q75,
            q75 + (data[col] - q75) ** 0.5,
            data[col]
        )

    # 2. 交互特征工程
    data['基础_高级交互'] = data['基础成绩_修正'] * data['高级成绩_修正']
    data['数据结构_基础差异'] = data['数据结构成绩_修正'] - data['基础成绩_修正']

    # 3. 特征选择
    final_features = [
        '基础成绩_修正', '高级成绩_修正', '数据结构成绩_修正',
        '基础_高级交互', '数据结构_基础差异'
    ]

    # --- 数据划分阶段 ---
    X = data[final_features]
    y = data[f'{target}_修正']

    # # 划分训练集和测试集（先划分再标准化）
    # X_train, X_test, y_train, y_test = train_test_split(
    #     X, y,
    #     test_size=0.2,
    #     random_state=42,
    #     stratify=pd.qcut(y, 5)  # 保持分布一致性
    # )

    # 正确流程：先划分再处理
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # 标准化（仅用训练集参数）
    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)  # 测试集不参与fit

    # 保存标准化器（添加课程标识）
    scaler_path = f'regression/scaler.pkl'
    joblib.dump(scaler, scaler_path)

    from xgboost import XGBRegressor
    # --- 模型训练 ---
    model = XGBRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8
    )

    # 交叉验证（仅在训练集进行）
    cv_scores = cross_val_score(model, X_train_scaled, y_train,
                                cv=KFold(n_splits=5, shuffle=True, random_state=42),
                                scoring='r2')
    print(f"\n[交叉验证] {target} R²: {cv_scores} (均值={np.mean(cv_scores):.3f})")

    # 最终训练
    model.fit(X_train_scaled, y_train)

    # --- 模型评估 ---
    # 训练集评估
    y_train_pred = model.predict(X_train_scaled)
    train_mse = mean_squared_error(y_train, y_train_pred)
    train_r2 = r2_score(y_train, y_train_pred)

    # 测试集评估（新增独立评估）
    y_test_pred = model.predict(X_test_scaled)
    test_mse = mean_squared_error(y_test, y_test_pred)
    test_r2 = r2_score(y_test, y_test_pred)

    from matplotlib import pyplot as plt
    # --- 结果可视化 ---
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_test_pred, alpha=0.5, label='test')
    plt.scatter(y_train, y_train_pred, alpha=0.2, label='train')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
    plt.title(f'{target}predict vs real')
    plt.legend()
    plt.savefig(f'regression/{target}_prediction.png')

    # 保存模型（带课程标识）
    model_path = f'regression/scaler.pkl'
    joblib.dump(model, model_path)

    print(f"训练集评估: MSE={train_mse:.2f}, R²={train_r2:.2f}")
    print(f"测试集评估: MSE={test_mse:.2f}, R²={test_r2:.2f}")

    return {
        'train_mse': train_mse,
        'train_r2': train_r2,
        'test_mse': test_mse,
        'test_r2': test_r2,
        'cv_mean_r2': np.mean(cv_scores)
    }
def train_model_v2(target_course='操作系统'):
    """支持课程动态预测的训练函数"""
    # 获取包含操作系统成绩的数据
    data = get_training_data(target_course)


    # 动态设置特征和目标
    features = ['基础成绩', '高级成绩', '数据结构成绩']
    target = f'{target_course}成绩'

    # 数据预处理增强
    # 1. 成绩分布修正
    for col in features + [target]:
        q75 = data[col].quantile(0.75)
        data[f'{col}_修正'] = np.where(
            data[col] >= q75,
            q75 + (data[col] - q75) ** 0.5,
            data[col]
        )

    # 2. 交互特征工程
    data['基础_高级交互'] = data['基础成绩_修正'] * data['高级成绩_修正']
    data['数据结构_基础差异'] = data['数据结构成绩_修正'] - data['基础成绩_修正']

    # 3. 特征选择
    final_features = [
        '基础成绩_修正', '高级成绩_修正', '数据结构成绩_修正',
        '基础_高级交互', '数据结构_基础差异'
    ]

    X = data[final_features]
    y = data[f'{target}_修正']

    # 数据标准化（带版本控制）
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, f'regression/scaler.pkl')

    # 使用XGBoost模型
    from xgboost import XGBRegressor
    model = XGBRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8
    )

    # 交叉验证优化
    from sklearn.model_selection import KFold
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='r2')
    print(f"\n[交叉验证] {target} R²: {cv_scores} (均值={np.mean(cv_scores):.3f})")

    # 训练最终模型
    model.fit(X_scaled, y)
    joblib.dump(model, f'regression/scaler.pkl')

    # 新增特征重要性分析
    importance = pd.DataFrame({
        '特征': final_features,
        '重要性': model.feature_importances_
    }).sort_values('重要性', ascending=False)
    print(f"\n[特征重要性] {target}:\n{importance}")

    # 增加可视化诊断
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 5))

    # 可视化预测分布
    plt.figure(figsize=(10, 6))
    plt.scatter(y, model.predict(X_scaled), alpha=0.5)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
    plt.title(f'{target}预测值 vs 真实值')
    plt.savefig(f'regression/{target}_prediction.png')

    # 评估训练集
    y_train_pred = model.predict(X_scaled)
    train_mse = mean_squared_error(y, y_train_pred)
    train_r2 = r2_score(y, y_train_pred)

    # 评估测试集
    y_test_pred = model.predict(X_scaled)
    test_mse = mean_squared_error(y, y_test_pred)
    test_r2 = r2_score(y, y_test_pred)

    # 保存模型
    joblib.dump(model, MODEL_PATH)

    print(f"训练集评估: MSE={train_mse:.2f}, R²={train_r2:.2f}")
    print(f"测试集评估: MSE={test_mse:.2f}, R²={test_r2:.2f}")

    return {
        'train_mse': train_mse,
        'train_r2': train_r2,
        'test_mse': test_mse,
        'test_r2': test_r2
    }


# 加载数据并训练模型
def train_model():
    # 获取训练数据
    data = get_training_data()

    # 分离特征与标签
    X = data[['基础成绩', '高级成绩']]
    y = data['数据结构成绩']
    print(f"\n[特征分析] 特征与标签的相关性矩阵:\n{data.corr()}")

    # 调整测试集比例至20%
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 数据标准化（修正后的正确流程）
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)  # 只在训练集上fit
    X_test_scaled = scaler.transform(X_test)        # 使用训练集的参数转换测试集


    # 在数据预处理步骤后添加
    # 1. 处理天花板效应（对高级成绩进行非线性变换）
    data['高级成绩_修正'] = np.where(
        data['高级成绩'] >= 95,
        95 + (data['高级成绩'] - 95) ** 0.5,  # 对高分区做开方拉伸
        data['高级成绩']
    )

    # 2. 创建交互特征
    data['基础_高级_交互'] = data['基础成绩'] * data['高级成绩_修正']

    # 3. 分箱处理基础成绩
    data['基础成绩分箱'] = pd.cut(data['基础成绩'],
                                  bins=[0, 60, 75, 90, 100],
                                  labels=['差', '中', '良', '优'])

    # 4. One-Hot编码
    data = pd.get_dummies(data, columns=['基础成绩分箱'])

    # 更新特征列
    features = ['基础成绩', '高级成绩_修正', '基础_高级_交互',
                '基础成绩分箱_差', '基础成绩分箱_中', '基础成绩分箱_良', '基础成绩分箱_优']
    X = data[features]

    # 保存标准化器
    joblib.dump(scaler, SCALER_PATH)

    # 尝试减小正则化强度
    model = ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=42)  # alpha从0.1调整为0.001

    # 增加5折交叉验证
    from sklearn.model_selection import cross_val_score
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
    print(f"\n[交叉验证] R²得分: {cv_scores} (均值={np.mean(cv_scores):.3f})")

    model.fit(X_train_scaled, y_train)

    # 评估训练集
    y_train_pred = model.predict(X_train_scaled)
    train_mse = mean_squared_error(y_train, y_train_pred)
    train_r2 = r2_score(y_train, y_train_pred)

    # 评估测试集
    y_test_pred = model.predict(X_test_scaled)
    test_mse = mean_squared_error(y_test, y_test_pred)
    test_r2 = r2_score(y_test, y_test_pred)

    # 保存模型
    joblib.dump(model, MODEL_PATH)

    print(f"训练集评估: MSE={train_mse:.2f}, R²={train_r2:.2f}")
    print(f"测试集评估: MSE={test_mse:.2f}, R²={test_r2:.2f}")

    # 增加可视化诊断
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 5))

    # 真实值 vs 预测值
    plt.subplot(1, 2, 1)
    plt.scatter(y_test, y_test_pred, alpha=0.5)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
    plt.xlabel('True Values')
    plt.ylabel('Predictions')

    # 残差分布
    plt.subplot(1, 2, 2)
    residuals = y_test - y_test_pred
    plt.hist(residuals, bins=20)
    plt.xlabel('Residuals')
    plt.tight_layout()
    plt.savefig('regression/diagnostic_plot.png')  # 保存诊断图

    return {
        'train_mse': train_mse,
        'train_r2': train_r2,
        'test_mse': test_mse,
        'test_r2': test_r2
    }


def train_model_v1():
    # 获取训练数据
    data = get_training_data()

    # 分离特征与标签
    X = data[['基础成绩', '高级成绩']]
    y = data['数据结构成绩']
    print(f"\n[特征分析] 特征与标签的相关性矩阵:\n{data.corr()}")

    # 调整测试集比例至20%
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 特征工程（仅在训练集上拟合）
    # 1. 天花板效应处理
    X_train['高级成绩_修正'] = np.where(
        X_train['高级成绩'] >= 95,
        95 + (X_train['高级成绩'] - 95) ** 0.5,
        X_train['高级成绩']
    )
    X_test['高级成绩_修正'] = np.where(  # 应用相同规则到测试集
        X_test['高级成绩'] >= 95,
        95 + (X_test['高级成绩'] - 95) ** 0.5,
        X_test['高级成绩']
    )

    # 2. 创建交互特征
    X_train['基础_高级_交互'] = X_train['基础成绩'] * X_train['高级成绩_修正']
    X_test['基础_高级_交互'] = X_test['基础成绩'] * X_test['高级成绩_修正']

    # 3. KMeans聚类高级成绩（新增）
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=3, random_state=42)
    X_train['高级_聚类'] = kmeans.fit_predict(X_train[['高级成绩_修正']])
    X_test['高级_聚类'] = kmeans.predict(X_test[['高级成绩_修正']])  # 使用训练好的模型

    # 4. One-Hot编码聚类结果
    from sklearn.preprocessing import OneHotEncoder
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    cluster_train = encoder.fit_transform(X_train[['高级_聚类']])
    cluster_test = encoder.transform(X_test[['高级_聚类']])
    cluster_cols = [f'高级聚类_{i}' for i in range(cluster_train.shape[1])]

    # 合并聚类特征
    X_train = pd.concat([
        X_train.reset_index(drop=True),
        pd.DataFrame(cluster_train, columns=cluster_cols)
    ], axis=1)
    X_test = pd.concat([
        X_test.reset_index(drop=True),
        pd.DataFrame(cluster_test, columns=cluster_cols)
    ], axis=1)

    # 数据标准化（使用更新后的特征）
    features = ['基础成绩', '高级成绩_修正', '基础_高级_交互'] + cluster_cols
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train[features])
    X_test_scaled = scaler.transform(X_test[features])

    # 保存标准化器
    joblib.dump(scaler, SCALER_PATH)

    # 尝试调整正则化参数
    model = ElasticNet(alpha=0.001, l1_ratio=0.5, random_state=42)

    # 交叉验证
    from sklearn.model_selection import cross_val_score
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
    print(f"\n[交叉验证] R²得分: {cv_scores} (均值={np.mean(cv_scores):.3f})")

    model.fit(X_train_scaled, y_train)

    # 评估训练集
    y_train_pred = model.predict(X_train_scaled)
    train_mse = mean_squared_error(y_train, y_train_pred)
    train_r2 = r2_score(y_train, y_train_pred)

    # 评估测试集
    y_test_pred = model.predict(X_test_scaled)
    test_mse = mean_squared_error(y_test, y_test_pred)
    test_r2 = r2_score(y_test, y_test_pred)

    # 保存模型
    joblib.dump(model, MODEL_PATH)

    print(f"训练集评估: MSE={train_mse:.2f}, R²={train_r2:.2f}")
    print(f"测试集评估: MSE={test_mse:.2f}, R²={test_r2:.2f}")

    # 增加可视化诊断
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 5))

    # 真实值 vs 预测值
    plt.subplot(1, 2, 1)
    plt.scatter(y_test, y_test_pred, alpha=0.5)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
    plt.xlabel('True Values')
    plt.ylabel('Predictions')

    # 残差分布
    plt.subplot(1, 2, 2)
    residuals = y_test - y_test_pred
    plt.hist(residuals, bins=20)
    plt.xlabel('Residuals')
    plt.tight_layout()
    plt.savefig('regression/diagnostic_plot.png')  # 保存诊断图

    return {
        'train_mse': train_mse,
        'train_r2': train_r2,
        'test_mse': test_mse,
        'test_r2': test_r2
    }

# 预测函数
def predict(data):
    # 加载模型和标准化器
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    # 将输入数据转为 DataFrame
    input_data = pd.DataFrame([data])

    # 数据标准化
    input_scaled = scaler.transform(input_data)

    # 进行预测
    prediction = model.predict(input_scaled)
    return prediction[0]


# Flask 路由：训练模型
@api_reg.route('/train', methods=['GET'])
def train():
    try:
        metrics = train_model_v3('操作系统')
        return jsonify({
            "message": "模型训练完成",
            "metrics": {
                "training_set": {
                    "mse": metrics['train_mse'],
                    "r2": metrics['train_r2']
                },
                "test_set": {
                    "mse": metrics['test_mse'],
                    "r2": metrics['test_r2']
                }
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask 路由：预测
@api_reg.route('/predict', methods=['POST'])
def predict_route():
    # 从请求中获取数据
    input_data = request.json
    try:
        # 确保输入数据包含必要字段
        if 'grade_基础' not in input_data or 'grade_高级' not in input_data:
            return jsonify({"error": "输入数据缺少必要字段"}), 400

        # 进行预测
        result = predict(input_data)
        return jsonify({"预测结果": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500