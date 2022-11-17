import time
import io
import cv2
import numpy as np
import struct
from personData import *
from pyzbar import pyzbar
import requests
import ast
import pymysql
import socket
import datetime

# 实地测试
Server_Host = '192.168.101.10'

ListenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# ListenSocket.bind((Server_Host, 1919))
ListenSocket.connect((Server_Host, 1919))


# TODO
# 实时更新内容：
# 1. 健康码
# 2. 体温
# 3. 检测时间
# 4. 签入状态：由上个 签入状态 决定
# 5. 健康状态：由 ”健康码" 与 "体温“ 共同决定
# 0. 传输的实体照片


class AI_EP_System():
    def __init__(self):
        # 数据库连接
        self.EP_DB = pymysql.connect(
            host='localhost',
            user='root',
            password='123456123',
            database='AI_EP_System',
            charset='utf8'
        )
        print("数据库已连接")
        print("正在与上位机建立TCP连接。。。")

        # 参数
        self.pic_data = None
        self.health_conditon = None
        self.healthHQ = None
        self.temperation = None
        self.checked = None
        self.checkTime = None

        # OpenCV
        self.hQcode = self.name = self.frame = self.cap = None
        # self.module = hub.Module(name="pyramidbox_lite_mobile_mask")
        self.recog = cv2.face.LBPHFaceRecognizer_create()
        self.recog.read('jackData-True_trainner.yml')
        self.face_xml = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def send_msg(self):
        """发送身份信息到上位机"""
        encode_len = str(len(self.pic_data)).encode()
        print(len(encode_len))

        ListenSocket.send(self.name.encode())
        time.sleep(1)
        ListenSocket.send(encode_len)
        time.sleep(1)
        ListenSocket.send(self.pic_data)

        nparr = np.fromstring(self.pic_data, dtype='uint8')
        img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        print(img_decode)
        cv2.imshow("img_decode", img_decode)  # 显示图片
        cv2.waitKey(0)

        # ListenSocket.send(self.pic_data)

    def update_SQL(self):
        """更新数据库信息"""
        health_conditon, checked = self.recv_SQL()
        cur = self.EP_DB.cursor()
        self.checkTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = f'update personCheck set health_conditon="{health_conditon}", checked="{checked}", checkTime="{self.checkTime}" where name="{self.name}"'
        cur.execute(sql)
        self.EP_DB.commit()
        pass

    def recv_SQL(self):
        """查询数据库 ---> 获取检测人员身份信息"""
        cur = self.EP_DB.cursor()
        sql = f'select healthHQ, temperation, checked from personCheck where name = "{self.name}"'
        cur.execute(sql)
        res = cur.fetchall()
        print(res)
        print(type(res[0][2]))
        ishealth = ''
        if res[0][0] == '正常' and res[0][1]<37.2:
            ishealth = '正常'
        else:
            ishealth = '异常'
        if res[0][2] == '签出':
            checked = '签入'
        else:
            checked = '签出'
        print(ishealth, '  ', checked)
        return ishealth, checked

    def run(self):
        """ 主程序启动 """
        self.cap = cv2.VideoCapture(0)
        self.isOpened = self.cap.isOpened()
        self.cap_working()
        self.update_SQL()
        self.send_msg()
        print("完成！")

    def cap_working(self):
        """视觉检测启动"""
        if self.isOpened:
            print("成功建立连接")
            print("--进入摄像头识别流程--")
            self.face_detect()
            print("进入健康码检测")
            # self.hQcode = self.hQRcode_detect()
            self.release()

    def face_detect(self):
        """人脸识别"""
        while 1:
            _, self.frame = self.cap.read()
            frameGray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            face = self.face_xml.detectMultiScale(frameGray, 1.1, 3)
            if ord("q") == cv2.waitKey(1):
                return
            # cv2.imshow("Detect", self.frame)
            for (x, y, w, h) in face:
                ids, confidence = self.recog.predict(frameGray[y:y + h, x:x + w])
                # cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 255, 1), 2, cv2.LINE_AA)

                if confidence > 50:
                    pass
                    # cv2.putText(self.frame, "Who are you?", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:

                    # cv2.putText(self.frame, names[ids - 1], (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    img = self.frame[y:y + h, x:x + w]
                    img_encode = cv2.imencode('.jpg', img)[1]
                    data_encode = np.array(img_encode)
                    self.pic_data = data_encode.tostring()
                    self.name = names[ids - 1]
                    print(f"{self.name} is OK！")
                    # cv2.imshow('test', img)
                    # cv2.waitKey(0)
                    return self.pic_data

    def hQRcode_detect(self):
        """健康码识别"""
        while 1:
            _, self.frame = self.cap.read()
            bacodes = pyzbar.decode(self.frame, symbols=[pyzbar.ZBarSymbol.QRCODE])
            for bacode in bacodes:
                url = bacode.data.decode("UTF-8")

                uid = url[str(url).find(".cn/") + 4:]
                tar_url = f"https://suishenmafront1.sh.gov.cn/smzy/yqfkewm/ssm/ewmcheck?uid={uid}"

                tar_req = requests.get(tar_url, 'lxml')
                tar_req.encoding = 'utf-8'
                tar_json = ast.literal_eval(tar_req.json()["data"])["type"]
                # print(tar_url)
                # print(url)
                if ord("q") == cv2.waitKey(1):
                    return

                if tar_json == "00":
                    print("健康码正常")
                    return 1
                else:
                    print("健康码异常")
                    return 0

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    AIEPSYS = AI_EP_System()

    AIEPSYS.run()
