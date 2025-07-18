############## Import Libraries #######################
from motor import Motor
from LaneModule import getLane
#import camera
from picame import Camera,getImg
import cv2
import utils
 
############  Initialize class Objects #################
motor = Motor()
motor.start()

picam2 = Camera()
picam2.start_now()
################ Define Motor Directions to leave parking lot #############

# move_forward(speed,duration)
# turn_left(speed,duration)
# turn_right(speed,duration)
# stop_motors(speed,duration)

motor.move_forward(40,0.3)

# My main function for all the algorithms to run 


def main():
    cap = picam2.start_capture()
    img = getImg(cap)
    h,w,c = img.shape
    scaled_h = h//2
    scaled_width = w//2
    img = cv2.resize(img,(scaled_h,scaled_width))
    curveVal= getLane(img)
 
    sen = 1.2  # SENSITIVITY
    maxVAl= 0.3 # MAX SPEED
    if curveVal>maxVAl:
        curveVal = maxVAl
    if curveVal<-maxVAl: 
        curveVal =-maxVAl
    
    if curveVal>0:
        if curveVal<0.05: 
            curveVal=0
    else:
        if curveVal>-0.08: 
            curveVal=0

    motor.MotorRun_Lane(speed=20,turn = curveVal*sen, duration = 0.1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        picam2.stop_capture()
        motor.stop()
     
if __name__ == '__main__':
    while True:
        main()

