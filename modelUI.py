import sys,os,cv2
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

global a,b

with open("/Users/chenweihao/PycharmProjects/Bishe/X.txt", "r") as f:
    datax = f.read()

class modelUI (QMainWindow):

    def __init__(self):
        super ().__init__()
        self.initUI ()

    def initUI(self):


        pix1 = QPixmap(datax)
        lb1 = QLabel(self)
        lb1.setGeometry(0,0,300,300)
        lb1.setStyleSheet("border: 1px solid black")
        lb1.setPixmap(pix1)

        pix2 = QPixmap('114514.png')

        lb1 = QLabel(self)
        lb1.setGeometry(0,300,300,300)
        lb1.setStyleSheet("border: 1px solid black")
        lb1.setPixmap(pix2)


        #设置窗口的位置和大小
        self.setGeometry(300, 600, 300, 600)
        #设置窗口的标题
        self.setWindowTitle('最终结果')

        self.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    md = modelUI ()
    os.remove('/Users/chenweihao/PycharmProjects/Bishe/X.txt')
    os.remove('/Users/chenweihao/PycharmProjects/Bishe/fileaddress.txt')
    os.remove('/Users/chenweihao/PycharmProjects/Bishe/114514.png')
    os.remove('/Users/chenweihao/PycharmProjects/Bishe/114.png')
    sys.exit (app.exec_())


