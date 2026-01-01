import sqlite3
import os


def create_database():
    db_path = './data/upgrade.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    create table upgrade_input(
    user_id int primary key,
    data text,
    size int
    )
    ''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()


# action表
# id(integer)      type(text)      action(text)
#   编号(主键)          类型             内容

# insert_log表
# id(integer)     time(datetiem)      value(text)       user_id(int)
#   编号(主键)           时间              插入的值           用户id

# delete表
# id(integer)     time(datetiem)      value(text)       user_id(int)
#   编号(主键)           时间              删除的值           用户id

# user_log表
# id(integer)     time(datetiem)      behavior(text)       user_id(int)
#   编号(主键)           时间              用户行为               用户id

# user_info表
# user_id(integer)     open_time(datetime)       name(text)        password(text)        account(text)         run_time(datetime)
#   用户id(主键)              创建时间                用户名              用户密码                账号                      登录时间

# fly_ludo_input
# user_id (int)        data(text)       count(int)
#  用户id(主键)           比例数据           个数数据

# bingo_input
# user_id (int)        data(text)       count(int)
#  用户id(主键)           比例数据            尺寸

# schedule_input
# user_id (int)        data(text)       max_capacity(int)
#  用户id(主键)           比例数据             最大容量

# upgrade_input
# user_id (int)        data(text)       size(int)
#  用户id(主键)           比例数据         表格等级数