from picame import Camera,getImg
import cv2
from ultralytics import YOLO
import utils


#load yolo pretrained model cuz im lazy
model = YOLO("my_model.pt")
picam2 = Camera()
picam2.start_now()

while True:
    # Capture a frame from the camera
    frame = picam2.picam2.start_capture()
    frame = getImg(frame)
    
    # Run YOLO model on the captured frame and store the results
    results = model(frame)

    for result in results:
        class_name = utils.extract_class_name(result)
        if class_name == "cone":
            #do something when cone is detected
            print("Cone detected!")
        else:
            #do something else when cone is not detected
            print("No cone detected!")
            
    annotated_frame = utils.annotate_Result2Frame(results)

    # Display the resulting frame
    cv2.imshow("Camera", annotated_frame)

    # Exit the program if q is pressed
    if cv2.waitKey(1) == ord("q"):
        break

# Close all windows
picam2.stop_capture()
cv2.destroyAllWindows()