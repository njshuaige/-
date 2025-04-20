import cv2
from process import Detector
import chess
cap = cv2.VideoCapture(1)

detector = Detector()
if not cap.isOpened():
    print("摄像头无法打开！")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    yellow, list = detector.find_roi(frame)
    print(list)
    
    
    cv2.imshow("Frame with Yellow Rectangle and Grid", yellow)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
