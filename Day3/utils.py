import cv2
import numpy as np

def threshold(frame):
    hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lowerWhite = np.array([80,0,149])
    upperWhite = np.array([179,64,255])
    mask_img = cv2.inRange(hsv_img,lowerWhite,upperWhite)
    return mask_img

def warpImg(frame, points, width, height, inv = False):
    point1 = np.float32(points)
    point2 = np.float32([ [0,0],[width,0],[0,height],[width,height] ])
    
    if inv:
        matrix = cv2.getPerspectiveTransform(point2,point1)
    else:
        matrix = cv2.getPerspectiveTransform(point1,point2)
    
    result_img = cv2.warpPerspective(frame,matrix,(width,height))
    return result_img

def nothing(x):
    pass

def init_TrackBar(initialTraceBarVals,width_T, height_T):
    cv2.namedWindow("Trackers")
    cv2.resizeWindow("Trackers",360,240)

    #width is divided by half to create a symmetrical trapezoid
    #assumes that car is in center
    #height can go from min 2 max within area of interest
    cv2.createTrackbar("Width Top", "Trackers",initialTraceBarVals[0],width_T//2,nothing)
    cv2.createTrackbar("Height Top", "Trackers",initialTraceBarVals[1],height_T,nothing)
    cv2.createTrackbar("Width Bottom", "Trackers",initialTraceBarVals[2],width_T//2,nothing)
    cv2.createTrackbar("Height Bottom", "Trackers",initialTraceBarVals[3],height_T,nothing)

def get_valTrackBar(width_T, height_T):
    width_top = cv2.getTrackbarPos("Width Top","Trackers")
    height_top = cv2.getTrackbarPos("Height Top","Trackers")
    width_bottom = cv2.getTrackbarPos("Width Bottom","Trackers")
    height_bottom = cv2.getTrackbarPos("Height Bottom","Trackers")
    points = np.float32([ [width_top,height_top], [width_T-width_top,height_top], [width_bottom, height_bottom], [width_T-width_bottom, height_bottom] ])

    return points

def extract_class_name(result):
    if result.boxes is not None:
        for i, box in enumerate(result.boxes):
            class_id = int(box.cls.cpu().numpy())
            class_name = result.names[class_id]
            confidence = float(box.conf.cpu().numpy())

            return class_name

def annotate_Result2Frame(results):
    annotated_frame = results[0].plot()
    # Get inference time
    inference_time = results[0].speed['inference']
    fps = 1000 / inference_time  # Convert to milliseconds
    text = f'FPS: {fps:.1f}'

    # Define font and position
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 1, 2)[0]
    text_x = annotated_frame.shape[1] - text_size[0] - 10  # 10 pixels from the right
    text_y = text_size[1] + 10  # 10 pixels from the top

    # Draw the text on the annotated frame
    cv2.putText(annotated_frame, text, (text_x, text_y), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

    return annotated_frame

def drawPoints(img,points):
    #cv2.circle(image, center_coordinates, radius, color, line_thickness)
    #color is BGR
    for x in range(4):
        cv2.circle(img, ( int(points[x][0]),int(points[x][1]) ),15,(0,0,255),cv2.FILLED)
    return img 

def getHistogram(img,display=False,minVal = 0.1,region=1):
    if region == 1:
        histValues = np.sum(img, axis=0)
    else:
        histValues = np.sum(img[img.shape[0]//region::], axis=0)
    maxValue = np.max(histValues)  # FIND THE MAX VALUE, this is just one value
    minValue = minVal*maxValue #just one value threshold
    indexArray = np.where(histValues >= minValue) # ALL INDICES WITH MIN VALUE OR ABOVE
    basePoint =  int(np.average(indexArray)) # AVERAGE ALL passing INDICES VALUES, find the center point in every segment to avoid misinterpretation of center line
    if display:
        imgHist = np.zeros((img.shape[0],img.shape[1],3),np.uint8)
        for x,intensity in enumerate(histValues):
        # print(intensity)
            cv2.line(imgHist,(x,img.shape[0]),(x,int(img.shape[0]-intensity//255//region)),(255,0,255),1)
            cv2.circle(imgHist,(basePoint,img.shape[0]),20,(0,255,255),cv2.FILLED)
        return basePoint,imgHist
    return basePoint

def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver