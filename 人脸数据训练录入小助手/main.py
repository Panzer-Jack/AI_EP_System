import os
import sys
from main_win import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import cv2
from personData import *
# import paddlehub as hub
import numpy as np
from pyzbar import pyzbar
import requests
import ast

# TODO
# 1. 人脸识别 记录违反人员
# 2. 口罩识别
# 3. 健康码识别
# 扩展功能 - 红外线测温
# 可部署在 类似树莓派-Linux / STM32单片机
# print(hub.__file__)

class mainWin(QMainWindow, Ui_HealthSystem_main):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 主程序按钮
        self.button_main.clicked.connect(self.evt_page1)
        self.button_training.clicked.connect(self.evt_page2)
        self.button_getSample.clicked.connect(self.evt_page3)
        self.button_close.clicked.connect(self.evt_close)
        self.button_close2.clicked.connect(self.evt_close)
        self.button_small.clicked.connect(self.evt_small)

        # 页面按钮
        self.page1_main.clicked.connect(self.evt_page1_main)
        self.page2_read.clicked.connect(self.evt_page2_read)
        self.page2_run.clicked.connect(self.evt_page2_run)
        self.page3_run.clicked.connect(self.evt_page3_run)

        # OpenCV
        self.textboxValue = self.name = self.frame = self.cap = None
        # self.module = hub.Module(name="pyramidbox_lite_mobile_mask")
        self.recog = cv2.face.LBPHFaceRecognizer_create()
        self.face_xml = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.textBrowser.setText(" <h2>我是小帮手绫乃,"
                                 " 这里的给了功能库中的几项主要功能, 可根据需求进行样本录制、训练和现场识别</h2>"
                                 " <h2>对了,请放心, 我会跟随你的相关步骤进行说明的</h2>")

        # 窗口可拖动
        self.mouse_x = self.mouse_y = self.origin_x = self.origin_y = None

    # 1.鼠标点击事件
    def mousePressEvent(self, evt):
        # 获取鼠标当前的坐标
        self.mouse_x = evt.globalX()
        self.mouse_y = evt.globalY()

        # 获取窗体当前坐标
        self.origin_x = self.x()
        self.origin_y = self.y()

    # 2.鼠标移动事件
    def mouseMoveEvent(self, evt):
        # 计算鼠标移动的x，y位移
        move_x = evt.globalX() - self.mouse_x
        move_y = evt.globalY() - self.mouse_y

        # 计算窗体更新后的坐标：更新后的坐标 = 原本的坐标 + 鼠标的位移
        dest_x = self.origin_x + move_x
        dest_y = self.origin_y + move_y

        # 移动窗体
        self.move(dest_x, dest_y)

    def run(self):
        valueText = self.lineEdit_3.text()
        self.recog.read(valueText)
        self.cap = cv2.VideoCapture(0)
        self.isOpened = self.cap.isOpened()
        self.cap_working()

    def cap_working(self):
        if self.isOpened:
            self.face_detect()
            self.mask_detect()
            self.hQRcode_detect()
            self.release()

    def face_detect(self):
        while 1:
            _, self.frame = self.cap.read()
            frameGray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            face = self.face_xml.detectMultiScale(frameGray, 1.1, 3)
            if ord("q") == cv2.waitKey(1):
                return
            # cv2.imshow("Detect", self.frame)
            for (x, y, w, h) in face:
                ids, confidence = self.recog.predict(frameGray[y:y + h, x:x + w])
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 255, 1), 2, cv2.LINE_AA)
                if confidence > 70:
                    cv2.putText(self.frame, "Who are you?", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    cv2.putText(self.frame, names[ids - 1], (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    self.name = names[ids - 1]
                    print(f"{self.name} is OK！")
                    self.textBrowser.setText("<h2> 身份已确认，接下来进行口罩识别功能测试</h2>")
                    QMessageBox.information(self, "身份验证", f"{self.name} 已确认",
                                            QMessageBox.Yes)
                    QMessageBox.information(self, "提示", f"{self.name} 接下来进行口罩识别功能测试，请正确佩戴口罩",
                                            QMessageBox.Yes)
                    return 1

    def mask_detect(self):
        pass
        # while 1:
        #     _, self.frame = self.cap.read()
        #     results = self.module.face_detection(data={"data": [self.frame]})
        #     for result in results:
        #         label = result['data'][0]['label']
        #         confidence = result['data'][0]['confidence']
        #         if ord("q") == cv2.waitKey(1):
        #             return
        #         # cv2.imshow("Detect", self.frame)
        #         if label == "MASK" and confidence > 0.95:
        #             cv2.putText(self.frame, "Please go foward.", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (25, 255, 25),
        #                         2)
        #             # print("Mask is OK!")
        #             self.textBrowser.setText("<h2> 口罩佩戴正确，接下来进行健康码认证，请正确对准摄像头扫描健康码</h2>")
        #             QMessageBox.information(self, "口罩识别", f"{self.name} 口罩佩戴正确",
        #                                     QMessageBox.Yes)
        #             QMessageBox.information(self, "提示", f"{self.name} 接下来进行健康码认证，请正确对准摄像头扫描健康码",
        #                                     QMessageBox.Yes)
        #             return 1
        #         elif label == "NO MASK" or label == "MASK" and confidence < 0.85:
        #             cv2.putText(self.frame, "please put on mask!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (25, 25, 255),
        #                         2)
        #             print(f"{self.name} 防疫不规范，请正确佩戴口罩")

    def hQRcode_detect(self):
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
                # print(tar_json)
                if ord("q") == cv2.waitKey(1):
                    return
                if tar_json == "00":
                    self.textBrowser.setText("<h2> 防疫系统三个主要功能流程已结束，解下来请期待正式版系统</h2>")
                    QMessageBox.information(self, "结束", f"{self.name} 健康码正常，智能防疫系统结束",
                                            QMessageBox.Yes)
                    return 1
                else:
                    QMessageBox.information(self, "警告", f"{self.name} 健康码 有风险 请等待工作人员核查！",
                                            QMessageBox.Yes)
                    self.textBrowser.setText("<h2> ！！！！ 哇哇哇哇阿！！！！ 隔离隔离隔离隔离！！！</h2>")
                    save_data = open("data.txt", "w")
                    save_data.write(f"{self.name.get()}\n")
                    return 0

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def evt_page1_main(self):
        self.main_stackedWidget.setCurrentIndex(3)
        self.run()

    def samples_and_labels(self):
        faceData = []
        ids = []
        path1 = self.textboxValue
        for content in os.walk(path1):
            for i in range(0, 2000):
                maskPath = path1 + '/' + content[2][i]
                img = cv2.imread(maskPath)
                imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_xml.detectMultiScale(imgGray, 1.1, 3)
                for (x, y, w, h) in faces:
                    ids.append(1)
                    faceData.append(imgGray[y:y + h, x:x + w])

        return faceData, ids

    def evt_page2_read(self):
        self.textboxValue = self.lineEdit.text()
        print(self.textboxValue)

    def evt_page2_run(self):
        (faces, ids) = self.samples_and_labels()
        print(faces, ids)
        print("Training...")
        jackData = cv2.face.LBPHFaceRecognizer_create()  # 创建LBPH
        jackData.train(faces, np.array(ids))  # 参数1 为人脸像素数据  参数2 为对应人脸标签
        jackData.save("Data_trainner.yml")
        QMessageBox.information(self, "训练模型", "模型训练完毕，已保存至本地",
                                QMessageBox.Yes)

    def evt_page3_run(self):
        self.cap = cv2.VideoCapture(0)
        i = 0
        textValue = str(self.lineEdit_2.text())
        print(textValue)
        QMessageBox.information(self, "样本录制", "样本即将录制。。",
                                QMessageBox.Yes)
        while 1:
            _, self.frame = self.cap.read()
            if i == 2000:
                break
            else:
                i += 1
            fileName = "image" + str(i) + ".jpg"
            cv2.imwrite(f"{textValue}/{fileName}", self.frame, [cv2.IMWRITE_JPEG_QUALITY, 100])
            cv2.imshow("Recording...", self.frame)
            if ord("q") == cv2.waitKey(1):
                return
        self.release()

    def evt_small(self):
        self.showMinimized()

    def evt_close(self):
        sys.exit(app.exec_())

    def evt_page1(self):
        self.main_stackedWidget.setCurrentIndex(0)
        self.textBrowser.setText("<h2> 这里是现场视觉识别演示，分为三个步骤1. 人脸身份认证、口罩识别 以及健康码认证</h2>"
                                 "<h2> 注意：执行程序后 请跟随我的提示进行相关操作</h2>")

    def evt_page2(self):
        self.main_stackedWidget.setCurrentIndex(1)
        self.textBrowser.setText("<h2> 这里是模型训练功能，你可以在上方的输入栏里，输入你准备用来样本训练的相关文件夹，"
                                 "注意是 文件夹！(注：这里的文件路径要使用Linux的格式)</h2>")

    def evt_page3(self):
        self.main_stackedWidget.setCurrentIndex(2)
        self.textBrowser.setText("<h2> 这里是样本录制功能，你可以在上方的输入栏里，输入样本保存的目标文件夹"
                                 "注意是 文件夹！(注：这里的文件路径要使用Linux的格式)</h2>"
                                 "<h2> 你问用法？你直接把你的脸怼到我的摄像头面前就OK了，然后简单的做几个动作"
                                 "，让我看到你左脸和右脸</h2>")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = mainWin()
    main_win.show()
    sys.exit(app.exec_())
