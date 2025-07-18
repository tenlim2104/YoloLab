import cv2
import numpy as np
import utils

curve_List = []
max_curve_length = 5

def getLane(frame, display = 2):
    img_copy = frame.copy()

    imgResult = frame.copy()

    #step 1: Mask up the image
    img_th = utils.threshold(frame)

    #step 2: proccess for a better view/ perspective
    h,w,c = frame.shape
    #w = w//4
    #h = w//4
    print(w,h,c)
    #points = utils.get_valTrackBar()
    """
    points = [[  9.0, 350.0],
              [491.0, 350.0],
              [  0.0, 480.0],
              [500.0, 480.0]]
    """

    points = [[  43.0, 140.0],
              [277.0, 140.0],
              [  0.0, 240.],
              [320.0, 240.]]
    
    #print (points) #debug
    #warpped_Img = utils.warpImg(frame,points,w,h) #we want black and white so masked
    warpped_Img = utils.warpImg(img_th,points,w,h)
    draw_point_img = utils.drawPoints(img_copy,points)

    #Step 3: Create algo to determine which side to turn based on a reference
    #center line on which side has more pixel
    #using mean value to capture varying center line
    midPoint,histImg = utils.getHistogram(warpped_Img,True,minVal=0.9)
    curveAvgPoint,scaled_histImg = utils.getHistogram(warpped_Img,True,minVal=0.5,region=4)

    curve_indicate = midPoint - curveAvgPoint
    
    #print(curve_indicate)
    
    #STEP 4
    curve_List.append(curve_indicate)
    if len(curve_List)>max_curve_length:
        curve_List.pop(0)
        
    #raw_curveAvg = sum(curve_List)/len(curve_List) #newly edited

    curve = int(sum(curve_List)/len(curve_List))
    #print(curve)

    #STEP 5 Display
    if display != 0:
       imgInvWarp = utils.warpImg(warpped_Img, points, w, h, inv = True)
       imgInvWarp = cv2.cvtColor(imgInvWarp,cv2.COLOR_GRAY2BGR)
       imgInvWarp[0:h//3,0:w] = 0,0,0
       imgLaneColor = np.zeros_like(frame)
       imgLaneColor[:] = 0, 255, 0
       print(f"imgWarp: {warpped_Img.shape}, frame: {frame.shape}")
 
       print(f"imgInvWarp: {imgInvWarp.shape}, imgLaneColor: {imgLaneColor.shape}")


       imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
       imgResult = cv2.addWeighted(imgResult,1,imgLaneColor,1,0)
       midY = 450
       cv2.putText(imgResult,str(curve),(w//2-80,85),cv2.FONT_HERSHEY_COMPLEX,2,(255,0,255),3)
       cv2.line(imgResult,(w//2,midY),(w//2+(curve*3),midY),(255,0,255),5)
       cv2.line(imgResult, ((w // 2 + (curve * 3)), midY-25), (w // 2 + (curve * 3), midY+25), (0, 255, 0), 5)
       for x in range(-30, 30):
           w_sc = w // 20
           cv2.line(imgResult, (w_sc * x + int(curve//50 ), midY-10),
                    (w_sc * x + int(curve//50 ), midY+10), (0, 0, 255), 2)
       #fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
       #cv2.putText(imgResult, 'FPS '+str(int(fps)), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (230,50,50), 3);
    if display == 2:
        imgStacked = utils.stackImages(0.7,([frame,draw_point_img,warpped_Img],
                                            [histImg,imgLaneColor,imgResult]))
        cv2.imshow('ImageStack',imgStacked)
    elif display == 1:
        cv2.imshow('Resutlt',imgResult)




    #cv2.imshow('Mask Window',img_th)
    #cv2.imshow('Bird Eye Window',warpped_Img)
    #cv2.imshow('Point showing Window',draw_point_img)
    #cv2.imshow('Histo Window',histImg)
    #cv2.imshow('Scaled Histo Window',scaled_histImg)
    #return img_th

    #normalisation
    curve = curve/100 #newly edited
    if curve > 1:
        curve = 1
    if curve<-1:
        curve = -1
    print(curve)

    return curve