from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, QRect
from PyQt5.QtWidgets import QFileDialog
import PIL
from PIL import Image, ImageDraw, ImageFilter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import *
import sys,os

global a,b

with open("/Users/chenweihao/PycharmProjects/Bishe/fileaddress.txt", "r") as f:
    data = f.read()
    im1 = Image.open(data)
    a = im1.size[0]
    b = im1.size[1]


class myLabel2(QMainWindow):

    x0 = 0
    y0 = 0
    flag = False
    global x, y

    def __init__(self, parent=None):
        super(myLabel2, self).__init__(parent)

        self.setWindowTitle('贴图界面')
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap(data)))
        self.setPalette(window_pale)
        self.resize(a,b)


    def mousePressEvent(self, event):
        self.flag = True
        self.x0 = event.x()
        self.y0 = event.y()
        global x
        global y
        x = self.x0
        y = self.y0
        print(x)
        print(y)
        im1 = Image.open(data)
        im2 = Image.open('test.png')
        c = im2.size[0]
        d = im2.size[1]
        mask_im =Image.open('masktest.png').resize(im2.size).convert('L')
        back_im = im1.copy()
        x = int(x-(c/2))
        y = int(y-(d/2))
        print(x)
        print(y)
        back_im.paste(im2, (x, y), mask_im)
        back_im.save('rectangle_result.png', quality=95)
        back_im.show('rectangle_result.png')
        self.pic = QtGui.QPixmap("rectangle_result.png")

    def mouseReleaseEvent(self, event):
        self.flag = False


qapp = QApplication(sys.argv)
app = myLabel2()

app.show()
sys.exit(qapp.exec_())