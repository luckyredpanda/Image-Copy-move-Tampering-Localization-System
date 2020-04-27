import sys,os
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import *
from main_ui import *

class MyMainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.show_img)
        self.pushButton_2.clicked.connect(self.crop_image)
        self.pushButton_3.clicked.connect(self.paste_image)
        self.pushButton_8.clicked.connect(self.save_image)
        self.pushButton_9.clicked.connect(self.detect_image)
        self.pushButton_10.clicked.connect(self.detectmore_image)

    def text_create(self,msg):
        desktop_path = "/Users/chenweihao/PycharmProjects/Bishe/"  # 新创建的txt文件的存放路径
        full_path = desktop_path +'fileaddress.txt'  # 也可以创建一个.doc的word文档
        file = open(full_path, 'w')
        file.write(msg)

    #show image
    def show_img(self):
        global pic_path
        pic_path, _ = QFileDialog.getOpenFileName(self, '显示图片', '/Users/', 'Image files(*.jpg *.gif *.png *.tif)')
        self.text_create(pic_path)
        if pic_path:
            image2 = cv2.imread(pic_path)
            global show
            show = cv2.resize(image2, (800, 600))
            show2 = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            showImage = QtGui.QImage(show2.data, show2.shape[1], show2.shape[0],
                                     QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
            self.label.setPixmap(QtGui.QPixmap.fromImage(showImage))  # 往显示视频的Label里 显示QImage

    #crop
    def crop_image(self):
        result = os.path.exists('/Users/chenweihao/PycharmProjects/Bishe/fileaddress.txt')
        if result == True:
            os.system('python cropimagecir.py')
            QMessageBox.information(self,"成功了！","您已经抠图成功！",QMessageBox.Yes | QMessageBox.No)
        else:
            QMessageBox.information(self,"错误","请选择一张图片！",QMessageBox.Yes | QMessageBox.No)

    #paste
    def paste_image(self):
        result = os.path.exists('/Users/chenweihao/PycharmProjects/Bishe/fileaddress.txt')
        if result == True:
            os.system('python pasteimage.py')
            QMessageBox.information(self,"成功了！","您已经贴图成功！如果不满意可以重新操作。",QMessageBox.Yes | QMessageBox.No)
        else:
            QMessageBox.information(self,"错误","请选择一张图片！",QMessageBox.Yes | QMessageBox.No)

    #save
    def save_image(self):
        result = os.path.exists('/Users/chenweihao/PycharmProjects/Bishe/fileaddress.txt')
        if result == True:
            pic_path = "/Users/chenweihao/PycharmProjects/Bishe/rectangle_result.png"
            self.text_create("/Users/chenweihao/PycharmProjects/Bishe/rectangle_result.png")
            QMessageBox.information(self,"成功了！","图像已保存！",QMessageBox.Yes | QMessageBox.No)
            image2 = cv2.imread(pic_path)
            show = cv2.resize(image2, (800, 600))
            show2 = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            showImage = QtGui.QImage(show2.data, show2.shape[1], show2.shape[0],
                                    QtGui.QImage.Format_RGB888)
            self.label.setPixmap(QtGui.QPixmap.fromImage(showImage))
        else:
            QMessageBox.information(self,"错误","请选择一张图片！",QMessageBox.Yes | QMessageBox.No)

    #detect
    def detect_image(self):
        QMessageBox.information(self,"检测中","检测中，请稍等！大约需要20秒。",QMessageBox.Yes | QMessageBox.No)
        os.system('python model.py')
    #detect more than one pictures
    def detectmore_image(self):
        global directory
        directory = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      "./")
        self.text_create(directory)
        QMessageBox.information(self,"检测中","检测中，请稍等！先喝杯茶吧。",QMessageBox.Yes | QMessageBox.No)
        os.system('python morepictures.py')
        QMessageBox.information(self,"完成了！","恭喜你！完成啦！",QMessageBox.Yes | QMessageBox.No)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())