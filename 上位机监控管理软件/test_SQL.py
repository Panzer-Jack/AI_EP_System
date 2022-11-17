import pymysql

EP_DB = pymysql.connect(
            host='192.168.101.50',
            user='root',
            password='123456123',
            database='AI_EP_System',
            charset='utf8'
        )
print("数据库已连接")


def Insert():
    cur = EP_DB.cursor()
    sql = f'INSERT INTO personCheck(name, health_conditon, identity, phone, healthHQ, temperation, checked, checkTime)' \
          f' VALUES ("Jack先生", "正常", "学生", 17322208879, "正常", 36.5, "签入", "2020-09-16 23:18:17");'
    cur.execute(sql)
    EP_DB.commit()
    # EP_DB.close()

def update(name):
    cur = EP_DB.cursor()
    sql = f'update personCheck set name="Jay·C" where name="{name}"'
    cur.execute(sql)
    EP_DB.commit()
    # EP_DB.close()


def recv_SQL(name):
    """查询数据库 ---> 获取检测人员身份信息"""
    cur = EP_DB.cursor()
    # sql = f'# select * from personCheck where name = "{name}"'
    sql = f'select * from personCheck'
    cur.execute(sql)
    res = cur.fetchall()
    EP_DB.close()
    return res


# update("JayCx")
# res = recv_SQL("Jay·C")
# print(res)
Insert()
