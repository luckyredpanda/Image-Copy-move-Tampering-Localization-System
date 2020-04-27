

#from __future__ import print_function
import os
import sys
import cv2
import pandas
import tensorflow as tf
import numpy as np
import warnings
from matplotlib import pyplot
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import matplotlib



def visualize_one_sample( X, Y, Z, figsize=(12,4)):
    x = np.array(X).astype('uint8')
    y = np.array(Y).astype('uint8')
    z = np.array(Z)
    pyplot.figure(figsize=figsize)
    pyplot.subplot(131)
    pyplot.imshow( x )
    pyplot.title('test image')
    pyplot.subplot(132)
    pyplot.imshow( y )
    pyplot.title('ground truth')
    pyplot.subplot(133)
    pyplot.imshow( z )
    pyplot.title('BusterNet predicted')
    return

def text_createX(msg):
    desktop_path = "/Users/chenweihao/PycharmProjects/Bishe/"  # 新创建的txt文件的存放路径
    full_path = desktop_path +'X.txt'  # 也可以创建一个.doc的word文档
    file = open(full_path, 'w')
    file.write(msg)

from BusterNetCore import create_BusterNet_testing_model

with open("/Users/chenweihao/PycharmProjects/Bishe/fileaddress.txt", "r") as f:
    data = f.read()

model_dir =  '/Users/chenweihao/Downloads/CM/logs'
sys.path.insert( 0, model_dir )
busterNetModel = create_BusterNet_testing_model( os.path.join( model_dir, 'pretrained_busterNet.hd5' ) )

filename_test = data  # 测试其它图像，修改文件名
X = cv2.imread(data)
X = cv2.resize(X, (300, 300))
cv2.imwrite('114.png', np.uint8(X))
text_createX('/Users/chenweihao/PycharmProjects/Bishe/114.png')
pyplot.subplot(1,2,1)
pyplot.imshow(X)
X = cv2.resize(X, (300, 300))
Z = busterNetModel.predict(np.uint8(np.expand_dims(X, axis=0)), verbose = 0)
Z = np.uint8(Z[0] * 255.0)
Z1 = cv2.cvtColor(Z, cv2.COLOR_BGR2GRAY)
ret, result_img = cv2.threshold(Z1, 90, 255, cv2.THRESH_BINARY)
pyplot.subplot(1,2,2)
pyplot.imshow(result_img)
cv2.imwrite('114514.png', np.uint8(result_img))
os.system("python modelUI.py")

