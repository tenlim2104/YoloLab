import cv2
from picamera2 import Picamera2

class Camera:
    def __init__(self):
        self.camera = Picamera2()
        self.started = False

    def start_now(self):
        self.camera.preview_configuration.main.size = (1280, 1280)
        self.camera.preview_configuration.main.format = "RGB888"
        self.camera.preview_configuration.align()
        self.camera.configure("preview")
        self.camera.start()
        self.started = True

    def start_capture(self):
        if self.started:
            return self.camera.capture_array() # can i just call this, instead of returning, am i returning frame?
        else:
            print('Camera not initialized, kindly create Camera obj by picam2 = Camera() and call picam2.start_capture().')
            return None
        
    def stop_capture(self):
        if self.started:
            self.camera.stop()
            print("Camera stopped")
            cv2.destroyAllWindows()
            self.started = False

def getImg(cap,display=False, size=[480, 640]):
    img = cv2.resize(cap, (size[0], size[1]))
    if display:
        cv2.imshow('IMG', img)
        cv2.waitKey(1)
    return img
    
"""
if __name__ == '__main__':
    while True:
        img = getImg(True)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    img.release()
    cv2.destroyAllWindows()
"""