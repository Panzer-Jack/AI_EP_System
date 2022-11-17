import time

import pymysql
import sys
from main_win import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import socket
import cv2
import numpy as np
import threading

# 实地测试
Server_Host = '192.168.76.143'  # 填写上位机的 IP地址
Client_Host = '192.168.76.40'  # 填写下位机的 IP地址


tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.bind((Server_Host, 1919))
tcpServer.listen(10)

name = None
img_decode = None


class recvTCP_thread(QThread):
    update_date = pyqtSignal(str)

    def __init__(self, parent=None):
        super(recvTCP_thread, self).__init__(parent)

    def my_recv(self, sock, count):
        data = b''
        while count:
            recvData = sock.recv(count)
            if not recvData:
                return None
            data += recvData
            count -= len(recvData)
        return data

    def recv_img(self):
        # tcpServer.send(b'get-img')
        client, address = tcpServer.accept()
        while True:
            global name
            name = client.recv(1024).decode()
            print(name)
            tempdata_len = client.recv(1024).decode()
            print(int(tempdata_len))

            data = self.my_recv(client, int(tempdata_len))
            nparr = np.fromstring(data, dtype='uint8')
            global img_decode
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_decode = QtGui.QImage(img_RGB.data,
                                      img_RGB.shape[1],
                                      img_RGB.shape[0],
                                      img_RGB.shape[1] * 3,
                                      QtGui.QImage.Format_RGB888)
            self.update_date.emit('update')
            print(img_decode)
            break
        client.close()
        cv2.destroyAllWindows()

    def run(self):
        # self.client, self.address = tcpServer.accept()
        while 1:
            self.recv_img()
        # t = threading.Thread(target=self.recv_img)
        # t.start()


class mainWin(QMainWindow, Ui_HealthSystem_main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 参数
        self.recv_msg = recvTCP_thread()

        self.enter_pic_data = None
        self.enter_name_data = 0
        self.enter_ide_data = 0
        self.enter_phone_data = 0
        self.enter_isHealthy = 0
        self.enter_HQcode_data = 0
        self.enter_temp_data = 0
        self.enter_num_data = 0
        self.enter_num_danger_data = 0

        self.out_pic_data = None
        self.out_name_data = 0
        self.out_ide_data = 0
        self.out_phone_data = 0
        self.out_isHealthy = 0
        self.out_HQcode_data = 0
        self.out_temp_data = 0

        self.enter_num_danger.setText(f'<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                                      'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" '
                                      f'font-size:40pt; font-weight:600; color:#ff2d1a;">{self.enter_num_danger_data}</span></p>')
        self.enter_num.setText(f'<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                               'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" '
                               f'font-size:40pt; font-weight:600; color:#00ff00;">{self.enter_num_data}</span></p>')

        # 主程序按钮
        self.button_main.clicked.connect(self.evt_page1)
        self.button_goSQL.clicked.connect(self.evt_page2)
        self.button_close.clicked.connect(self.evt_close)
        self.button_close2.clicked.connect(self.evt_close)
        self.button_small.clicked.connect(self.evt_small)

        # 页面按钮
        self.button_main_2.clicked.connect(self.initRuning)
        # self.page2_read.clicked.connect(self.evt_page2_read)
        # self.page2_run.clicked.connect(self.evt_page2_run)
        # self.page3_run.clicked.connect(self.evt_page3_run)

        # 窗口可拖动
        self.mouse_x = self.mouse_y = self.origin_x = self.origin_y = None

    def initRuning(self):
        """初始化 并与下位机建立连接"""
        self.init_msg.setText('<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                              'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:24pt; '
                              'font-weight:600; color:#ff0000;">正在与下位机建立连接中...</span></p>')
        try:
            self.recv_SQL()
            self.init_msg.setText('<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                                  'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:24pt; '
                                  'font-weight:600; color:#00ff00;">已与下位机成功建立连接</span></p>')
        except:
            self.init_msg.setText('<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                                  'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:24pt; '
                                  'font-weight:600; color:#ff0000;">连接建立失败, 请联系管理员</span></p>')

    def access_info(self):
        self.enter_pic_data = img_decode
        self.enter_name_data = name
        self.findHealth_SQL()
        self.recv_SQL()
        self.find_SQL(self.enter_name_data)
        print('\n---------access_info---------')
        print(self.enter_pic_data)
        self.enter_pic.setPixmap(QPixmap.fromImage(self.enter_pic_data))
        # print("--------Debug00!--------")
        # self.enter_num_danger.setText(self.enter_num_danger_data)
        self.enter_num_danger.setText(f'<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                                      'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" '
                                      f'font-size:40pt; font-weight:600; color:#ff2d1a;">{self.enter_num_danger_data}</span></p>')
        print(self.enter_num_data)
        self.enter_num.setText(f'<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                               'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" '
                               f'font-size:40pt; font-weight:600; color:#00ff00;">{self.enter_num_data}</span></p>')
        # print("--------Debug2!--------")
        # print("--------Debug01!--------")
        self.enter_name.setText(f"<H2>{self.enter_name_data}</H2>")
        self.enter_ide.setText(f"<H2>{self.enter_ide_data}</H2>")
        self.enter_phone.setText(f"<H3>{self.enter_phone_data}</H3>")
        # print("--------Debug02!--------")
        if self.enter_isHealthy == '正常':
            # print("--------Debug1!--------")
            self.enter_HQcode.setText(f'<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                                      'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" '
                                      f'font-size:24pt; font-weight:600; color:#00ff00;">{self.enter_HQcode_data}</span></p>')
            # print("--------Debug2!--------")
            self.enter_temp.setText('<p align="center" style=" margin-top:0px; margin-bottom:0px; margin-left:0px; '
                                    'margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" '
                                    f'font-size:24pt; font-weight:600; color:#00ff00;">{self.enter_temp_data}</span></p>')
            # print("--------Debug3!--------")
        self.enter_pic.setScaledContents(True)
        time.sleep(1)
        pass

    def findHealth_SQL(self):
        """接收数据库信息 并显示到软件前端界面上"""
        EP_DB = pymysql.connect(
            host=Client_Host,
            user='root',
            password='123456123',
            database='AI_EP_System',
            charset='utf8'
        )
        print("数据库已连接")
        sql = f'select health_conditon from personCheck where health_conditon="正常" and checked="签入"'
        cur = EP_DB.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        print(res)
        self.enter_num_data = len(res)
        EP_DB.close()

    def find_SQL(self, name):
        """接收数据库信息 并显示到软件前端界面上"""
        EP_DB = pymysql.connect(
            host=Client_Host,
            user='root',
            password='123456123',
            database='AI_EP_System',
            charset='utf8'
        )
        print("数据库已连接")
        sql = f'select * from personCheck where name="{name}"'
        cur = EP_DB.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        self.enter_ide_data = res[0][2]
        self.enter_phone_data = res[0][3]
        self.enter_isHealthy = res[0][1]
        self.enter_HQcode_data = res[0][4]
        self.enter_temp_data = res[0][5]
        # print(res)
        EP_DB.close()

    def recv_SQL(self):
        """接收数据库信息 并显示到软件前端界面上"""
        EP_DB = pymysql.connect(
            host=Client_Host,
            user='root',
            password='123456123',
            database='AI_EP_System',
            charset='utf8'
        )
        print("数据库已连接")
        model = QStandardItemModel()
        title = ["    姓名    ", "    健康状态    ", "    身份    ", "    手机号    ", "    健康码(最新)    ",
                 "    体温(最新)    ", "    签入状态(最新)    ", "        检测时间(最新)        "]
        model.setHorizontalHeaderLabels(title)
        sql = f'select * from personCheck'
        cur = EP_DB.cursor()
        cur.execute(sql)
        res = cur.fetchall()

        for i in range(0, len(res)):
            for j in range(0, len(res[i])):
                item = QStandardItem("%s" % res[i][j])
                model.setItem(i, j, item)
        self.Person_SQL.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Person_SQL.setModel(model)
        self.Person_SQL.resizeRowsToContents()
        self.Person_SQL.resizeColumnsToContents()
        EP_DB.close()
        pass

    def recv_msg(self):
        client, address = tcpServer.accept()
        request = client.recv(1024).decode(encoding='utf-8')
        client.close()
        print(request)
        return request

    def mousePressEvent(self, evt):
        """鼠标点击事件"""
        # 获取鼠标当前的坐标
        self.mouse_x = evt.globalX()
        self.mouse_y = evt.globalY()

        # 获取窗体当前坐标
        self.origin_x = self.x()
        self.origin_y = self.y()

    def mouseMoveEvent(self, evt):
        """鼠标移动事件"""
        # 计算鼠标移动的x，y位移
        move_x = evt.globalX() - self.mouse_x
        move_y = evt.globalY() - self.mouse_y

        # 计算窗体更新后的坐标：更新后的坐标 = 原本的坐标 + 鼠标的位移
        dest_x = self.origin_x + move_x
        dest_y = self.origin_y + move_y

        # 移动窗体
        self.move(dest_x, dest_y)

    def evt_small(self):
        self.showMinimized()

    def evt_close(self):
        sys.exit(app.exec_())

    def evt_page1(self):
        self.stackedWidget.setCurrentIndex(1)

    def evt_page2(self):
        self.stackedWidget.setCurrentIndex(2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = mainWin()
    update_data_thread = recvTCP_thread()
    update_data_thread.update_date.connect(main_win.access_info)  # 链接信号
    update_data_thread.start()

    main_win.show()
    sys.exit(app.exec_())
