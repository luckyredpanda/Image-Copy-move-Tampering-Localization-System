# -*- coding: utf-8 -*-
from main import *

global img
global point1, point2

lsPointsChoose = []
tpPointsChoose = []
lx = []
ly = []

pointsCount = 0
count = 0
pointsMax = 5

#-----------------------鼠标操作相关------------------------------------------
#------------------------------------------------------------------------------
lsPointsChoose = []
tpPointsChoose = []

pointsCount = 0
count = 0
pointsMax = 20

def on_mouse(event, x, y, flags, param):
    global img, point1, point2,count,pointsMax
    global lsPointsChoose, tpPointsChoose  #存入选择的点
    global pointsCount   #对鼠标按下的点计数
    global img2, ROI_bymouse_flag
    global a,b
    img2 = img.copy()   #此行代码保证每次都重新再原图画  避免画多了




    if event == cv2.EVENT_LBUTTONDOWN:         #左键点击

        pointsCount=pointsCount+1

        #       为了保存绘制的区域，画的点稍晚清零
        if(pointsCount==pointsMax+1):
            pointsCount = 0
            tpPointsChoose=[]
        print('pointsCount:', pointsCount)
        point1 = (x, y)
        print(x, y)
        lx.append(x)
        ly.append(y)
        print (lx)

        if (pointsCount == 1):
            a=x;b=y;
        #        画出点击的点
        cv2.circle(img2, point1, 10, (0, 255, 0), 5)

        #       将选取的点保存到list列表里
        lsPointsChoose.append([x, y])  #用于转化为darry 提取多边形ROI
        tpPointsChoose.append((x, y))  #用于画点
        #----------------------------------------------------------------------
        #将鼠标选的点用直线链接起来
        print(len(tpPointsChoose))
        for i in range(len(tpPointsChoose)-1):
            cv2.line(img2, tpPointsChoose[i], tpPointsChoose[i+1], (0, 0, 255), 2)
        #----------------------------------------------------------------------
        #----------点击到pointMax时可以提取去绘图----------------
        if (pointsCount !=pointsMax):
            if(pointsCount > 2):
                if(point1==(a,b) or point1==(a+1,b) or point1==(a-1,b)or point1==(a,b+1)or point1==(a,b-1)or point1==(a-1,b-1)or point1==(a+1,b+1)):
            #-----------绘制感兴趣区域-----------
                    ROI_byMouse()
                    ROI_bymouse_flag = 1
                    lsPointsChoose = []
                    sys.exit(0)
        else:
            ROI_byMouse()
            ROI_bymouse_flag = 1
            lsPointsChoose = []
            sys.exit(0)
        #--------------------------------------------------------
        cv2.imshow('src', img2)
    #-------------------------右键按下清除轨迹（未完成）-----------------------------
    if event == cv2.EVENT_RBUTTONDOWN:         #右键点击
        print("right-mouse")
        pointsCount = 0


        tpPointsChoose = []
        lsPointsChoose = []


#--------------------------------------------------------------
def ROI_byMouse():
    global src, ROI, ROI_flag, mask2
    mask = np.zeros(img.shape, np.uint8)
    pts = np.array([lsPointsChoose], np.int32)
    # pts.shape=(4，2)
    pts = pts.reshape((-1, 1, 2)) # -1代表剩下的维度自动计算
    # reshape 后的 pts.shape=(4。1，2)？？
    #--------------画多边形---------------------
    mask = cv2.polylines(mask, [pts], True, (0, 255, 255))
    ##-------------填充多边形---------------------
    mask2 = cv2.fillPoly(mask, [pts], (255,255,255))
    #cv2.imshow('mask', mask2)
    dst = cv2.bitwise_and(img, mask)

    cv2.imwrite("image.png", dst)
    croppedmask = mask[ min(ly):max(ly),min(lx):max(lx)]
    cv2.imwrite("masktest.png",croppedmask)

    file_name = "image.png"
    src = cv2.imread(file_name, 1)
    tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(src)
    rgba = [b,g,r, alpha]
    dst = cv2.merge(rgba,4)
    cropped = dst[ min(ly):max(ly),min(lx):max(lx)]
    cv2.imshow("test.png", cropped)
    cv2.imwrite("test.png", cropped)
    os.remove("image.png")

def main():
    global img,img2,ROI
    with open("/Users/chenweihao/PycharmProjects/Bishe/fileaddress.txt", "r") as f:
        data = f.read()
    img = cv2.imread(data)

    #---------------------------------------------------------
    #--图像预处理，设置其大小
    height, width = img.shape[:2]
    size = (int(width*1), int(height*1))
    img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    #------------------------------------------------------------
    ROI = img.copy()
    cv2.namedWindow('src')
    cv2.setMouseCallback('src', on_mouse)
    cv2.imshow('src', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':

    main()
    sys.exit(0)