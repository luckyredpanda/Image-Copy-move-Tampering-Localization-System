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

from BusterNetCore import create_BusterNet_testing_model

model_dir =  '/Users/chenweihao/Downloads/CM/logs'
sys.path.insert( 0, model_dir )
busterNetModel = create_BusterNet_testing_model( os.path.join( model_dir, 'pretrained_busterNet.hd5' ) )

with open("/Users/chenweihao/PycharmProjects/Bishe/fileaddress.txt", "r") as f:
    data = f.read()

for filename in os.listdir(data):
    if filename.endswith('jpg') or filename.endswith('png') or filename.endswith('tif'):
        print (data+'/'+filename) # 测试其它图像，修改文件名
        X = cv2.imread(data+'/'+filename)
        pyplot.subplot(1,2,1)
        pyplot.imshow(X)
        Z = busterNetModel.predict( np.uint8(np.expand_dims(X, axis=0)), verbose = 0)
        Z = np.uint8(Z[0] * 255.0)
        Z1 = cv2.cvtColor(Z, cv2.COLOR_BGR2GRAY)
        ret, result_img = cv2.threshold(Z1, 90, 255, cv2.THRESH_BINARY)
        pyplot.subplot(1,2,2)
        pyplot.imshow(result_img)
        filename = filename [:-4]
        cv2.imwrite(data+'/'+filename + 'mask.png', np.uint8(result_img))







