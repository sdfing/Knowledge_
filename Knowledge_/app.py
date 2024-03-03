# 第一步导入create_engine
from sqlalchemy import create_engine

# 第二步生成引擎对象
engine = create_engine(
    'mysql+pymysql://root:Asd12345@127.0.0.1:3306/aaa',
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)
# 第三步 使用引擎获取连接，操作数据库
conn=engine.raw_connection()
# 创建游标
cursor=conn.cursor()
# sql语句
cursor.execute('select * from luffy_course')
print(cursor.fetchall())